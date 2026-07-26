# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (service.py)
# Date: 2026-03-27
# ---------------------------------------------------------------------------
from __future__ import annotations

import copy
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ollama_client import generate_recommendation, generate_weighted_prediction
from .workbook import LEVELS, UIWorkbookLoader, WorkbookTemplateLoader

LEVEL_SCORE = {level["key"]: level["score"] for level in LEVELS}


class AssessmentService:
    # Function: __init__
    def __init__(self, workbook_path: Path, state_dir: Path, ui_workbook_path: Path, dbdata_path: Path):
        self.workbook_path = workbook_path
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

        loaded = WorkbookTemplateLoader(workbook_path).load()
        ui_loaded = UIWorkbookLoader(ui_workbook_path).load()
        self.levels = loaded["levels"]
        self.templates = loaded["editable_towers"]
        self.reference_template = loaded["applications_reference"]
        self.dashboard_template = loaded["dashboard_template"]
        self.current_state_map = self._load_current_state_map(dbdata_path)
        self.ui_collections = {
            "applications": [
                {
                    "value": tower_key,
                    "label": tower_meta["name"],
                }
                for app_name in ui_loaded["applications"]
                for tower_key, tower_meta in self.templates.items()
                if tower_meta["name"] == app_name
            ],
            "dimensions": ui_loaded["dimensions"],
            "phases": ui_loaded["phases"],
            "questions": ui_loaded["questions"],
            "currentStates": ui_loaded["currentStates"],
        }

    # Function: bootstrap
    def bootstrap(self) -> dict[str, Any]:
        towers = [self.get_tower(key) for key in self.templates]
        return {
            "module": "SSDLC Process Assessment",
            "levels": self.levels,
            "uiCollections": self.ui_collections,
            "currentStateMap": self.current_state_map,
            "dashboard": self.build_dashboard(),
            "towers": towers,
            "referenceTemplate": {
                "name": self.reference_template["name"],
                "sheetName": self.reference_template["sheetName"],
                "questionCount": len(self.reference_template["responses"]),
            },
        }

    # Function: get_tower
    def get_tower(self, tower_key: str) -> dict[str, Any]:
        template = self._require_template(tower_key)
        state = self._load_state(tower_key)
        tower = copy.deepcopy(template)
        tower["responses"] = [
            self._merge_response(template_row, state_row)
            for template_row, state_row in zip(template["responses"], state["responses"], strict=True)
        ]
        tower["summary"] = self._build_tower_summary(tower["responses"])
        tower["updatedAt"] = state.get("updatedAt")
        return tower

    # Function: update_tower
    def update_tower(self, tower_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        template = self._require_template(tower_key)
        incoming = payload.get("responses") or []
        incoming_by_id = {row.get("id"): row for row in incoming if row.get("id")}
        existing_state = self._load_state(tower_key)
        existing_by_id = {row["id"]: row for row in existing_state.get("responses") or []}
        merged = []
        for template_row in template["responses"]:
            current = incoming_by_id.get(template_row["id"], {})
            existing = existing_by_id.get(template_row["id"], {})
            merged.append(
                {
                    "id": template_row["id"],
                    "selectedLevelKey": self._normalize_level(current.get("selectedLevelKey")),
                    "predictedWeight": self._normalize_weight(current.get("predictedWeight")),
                    "evidence": (current.get("evidence") or "").strip(),
                    "gapRecommendation": (current.get("gapRecommendation") or "").strip(),
                    "recommendationSource": current.get("recommendationSource"),
                    "recommendationModel": current.get("recommendationModel"),
                    "evidenceFiles": existing.get("evidenceFiles") or [],
                }
            )

        state = {"towerKey": tower_key, "updatedAt": self._utc_now(), "responses": merged}
        self._save_state(tower_key, state)
        return self.get_tower(tower_key)

    # Function: generate_recommendations
    def generate_recommendations(
        self,
        tower_key: str,
        row_ids: list[str] | None = None,
        force: bool = False,
        requested_model: str | None = None,
    ) -> dict[str, Any]:
        tower = self.get_tower(tower_key)
        selected_row_ids = set(row_ids or [])
        for row in tower["responses"]:
            if selected_row_ids and row["id"] not in selected_row_ids:
                continue
            if not force and row.get("gapRecommendation"):
                continue
            generated = generate_recommendation(row, requested_model=requested_model)
            row["gapRecommendation"] = generated["text"]
            row["recommendationSource"] = generated["source"]
            row["recommendationModel"] = generated["model"]

        self.update_tower(
            tower_key,
            {
                "responses": [
                    {
                        "id": row["id"],
                        "selectedLevelKey": row.get("selectedLevelKey"),
                        "predictedWeight": row.get("predictedWeight"),
                        "evidence": row.get("evidence"),
                        "gapRecommendation": row.get("gapRecommendation"),
                        "recommendationSource": row.get("recommendationSource"),
                        "recommendationModel": row.get("recommendationModel"),
                    }
                    for row in tower["responses"]
                ]
            },
        )
        return self.get_tower(tower_key)

    # Function: generate_row_predictions
    def generate_row_predictions(
        self,
        tower_key: str,
        row_id: str,
        selected_level_key: str | None,
        evidence: str = "",
        current_state: str = "",
        requested_model: str | None = None,
    ) -> dict[str, Any]:
        template = self._require_template(tower_key)
        template_row = next((row for row in template["responses"] if row["id"] == row_id), None)
        if template_row is None:
            raise KeyError(f"Unknown row id: {row_id}")

        selected_level_key = self._normalize_level(selected_level_key)
        evidence = (evidence or "").strip()
        prediction_row = self._merge_response(
            template_row,
            {
                "selectedLevelKey": selected_level_key,
                "predictedWeight": None,
                "evidence": evidence,
                "gapRecommendation": "",
                "recommendationSource": None,
                "recommendationModel": None,
            },
        )
        prediction_row["applicationName"] = template["name"]
        prediction_row["currentState"] = (current_state or "").strip()
        weighted = generate_weighted_prediction(prediction_row, requested_model=requested_model)

        state = self._load_state(tower_key)
        for row in state["responses"]:
            if row["id"] != row_id:
                continue
            row["selectedLevelKey"] = selected_level_key
            row["predictedWeight"] = weighted["weight"]
            row["evidence"] = evidence
            row["gapRecommendation"] = weighted["recommendation"]
            row["recommendationSource"] = weighted["source"]
            row["recommendationModel"] = weighted["model"]
            break
        state["updatedAt"] = self._utc_now()
        self._save_state(tower_key, state)
        return self.get_tower(tower_key)

    # Function: build_dashboard
    def build_dashboard(self) -> dict[str, Any]:
        towers = [self.get_tower(key) for key in self.templates]
        target_pct = self.dashboard_template["targetPct"]
        cards = []
        tower_map = {}
        scores = []
        for tower in towers:
            summary = tower["summary"]
            tower_map[tower["key"]] = {
                "name": tower["name"],
                "dimensionMetrics": {item["dimension"]: item for item in summary["dimensionMetrics"]},
            }
            if summary["overallScorePct"] is not None:
                scores.append(summary["overallScorePct"])
            cards.append(
                {
                    "key": tower["key"],
                    "name": tower["name"],
                    "overallScorePct": summary["overallScorePct"],
                    "overallLevel": summary["overallLevel"],
                    "answered": summary["answeredQuestions"],
                    "totalQuestions": summary["totalQuestions"],
                    "topConcern": summary["topConcern"],
                    "targetPct": target_pct,
                    "gapToTarget": None if summary["overallScorePct"] is None else round(target_pct - summary["overallScorePct"], 2),
                }
            )

        dimension_rows = []
        for dimension in self.dashboard_template["dimensionOrder"]:
            towers_for_dimension = {}
            for tower_key, tower_meta in tower_map.items():
                towers_for_dimension[tower_key] = tower_meta["dimensionMetrics"].get(
                    dimension,
                    {
                        "dimension": dimension,
                        "scorePct": None,
                        "answeredQuestions": 0,
                        "totalQuestions": 0,
                    },
                )
            dimension_rows.append({"dimension": dimension, "towers": towers_for_dimension})

        portfolio_score = round(sum(scores) / len(scores), 2) if scores else None
        return {
            "targetPct": target_pct,
            "portfolio": {
                "overallScorePct": portfolio_score,
                "overallLevel": self._score_to_level(portfolio_score),
                "assessedTowers": len(scores),
                "towerCount": len(towers),
            },
            "cards": cards,
            "dimensionMatrix": dimension_rows,
        }

    # Function: generate_adhoc_prediction
    def generate_adhoc_prediction(
        self,
        application_name: str,
        dimension: str,
        phase: str,
        question: str,
        selected_level_key: str | None,
        evidence: str = "",
        current_state: str = "",
        requested_model: str | None = None,
    ) -> dict[str, Any]:
        selected_level_key = self._normalize_level(selected_level_key)
        maturity_options = [
            {"key": lv["key"], "label": lv["label"], "score": lv["score"], "description": lv.get("description", "")}
            for lv in self.levels
        ]
        score = LEVEL_SCORE.get(selected_level_key or "", 0)
        prediction_row = {
            "dimension": dimension,
            "phase": phase,
            "question": question,
            "applicationName": application_name,
            "selectedLevelKey": selected_level_key,
            "score": score,
            "evidence": (evidence or "").strip(),
            "currentState": (current_state or "").strip(),
            "maturityOptions": maturity_options,
        }
        return generate_weighted_prediction(prediction_row, requested_model=requested_model)

    # Function: _find_template_row
    @staticmethod
    def _find_template_row(tower_template: dict[str, Any] | None, question: str) -> dict[str, Any] | None:
        if not tower_template:
            return None
        q = (question or "").strip()
        return next(
            (r for r in tower_template["responses"] if (r.get("question") or "").strip() == q),
            None,
        )

    # Function: _default_maturity_options
    def _default_maturity_options(self) -> list[dict[str, Any]]:
        return [
            {
                "key": lv["key"],
                "label": lv["label"],
                "score": lv["score"],
                "description": lv.get("description", ""),
            }
            for lv in self.levels
        ]

    # Function: _resolve_batch_row_context
    def _resolve_batch_row_context(
        self, application: str, row_item: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str]:
        """Locate the workbook template row for this question, if any, plus its maturity options and app name."""
        tower_template = self.templates.get(application)
        template_row = self._find_template_row(tower_template, row_item.get("question"))

        if template_row:
            maturity_options = template_row.get("maturityOptions", [])
            application_name = tower_template.get("name", application)
        else:
            maturity_options = self._default_maturity_options()
            application_name = row_item.get("applicationName") or application

        return template_row, maturity_options, application_name

    # Function: _persist_batch_prediction
    def _persist_batch_prediction(
        self,
        application: str,
        template_row: dict[str, Any] | None,
        selected_level_key: str,
        evidence: str,
        weighted: dict[str, Any],
    ) -> None:
        if not (template_row and application):
            return
        row_id = template_row["id"]
        state = self._load_state(application)
        for state_row in state["responses"]:
            if state_row["id"] == row_id:
                state_row["selectedLevelKey"] = selected_level_key
                state_row["predictedWeight"] = weighted["weight"]
                state_row["evidence"] = evidence
                state_row["gapRecommendation"] = weighted["recommendation"]
                state_row["recommendationSource"] = weighted["source"]
                state_row["recommendationModel"] = weighted["model"]
                break
        state["updatedAt"] = self._utc_now()
        self._save_state(application, state)

    # Function: generate_single_prediction_for_batch
    def generate_single_prediction_for_batch(
        self,
        row_item: dict[str, Any],
        requested_model: str | None = None,
    ) -> dict[str, Any]:
        """Process one row for batch prediction and persist result if a catalog entry exists."""
        application = row_item.get("application", "")
        selected_level_key = self._normalize_level(row_item.get("selectedLevelKey"))

        if not selected_level_key:
            return {"weight": None, "recommendation": "", "source": None, "model": None, "skipped": True}

        template_row, maturity_options, application_name = self._resolve_batch_row_context(application, row_item)

        evidence = (row_item.get("evidence") or "").strip()
        score = LEVEL_SCORE.get(selected_level_key, 0)
        prediction_row = {
            "applicationName": application_name,
            "dimension": row_item.get("dimension", ""),
            "phase": row_item.get("phase", ""),
            "question": row_item.get("question", ""),
            "selectedLevelKey": selected_level_key,
            "score": score,
            "currentState": (row_item.get("currentState") or "").strip(),
            "evidence": evidence,
            "maturityOptions": maturity_options,
        }

        weighted = generate_weighted_prediction(prediction_row, requested_model=requested_model)
        self._persist_batch_prediction(application, template_row, selected_level_key, evidence, weighted)

        return {
            "weight": weighted["weight"],
            "recommendation": weighted["recommendation"],
            "source": weighted["source"],
            "model": weighted["model"],
            "skipped": False,
        }

    # Function: add_evidence_file
    def add_evidence_file(self, tower_key: str, row_id: str, stored_name: str, original_name: str) -> None:
        state = self._load_state(tower_key)
        for row in state["responses"]:
            if row["id"] == row_id:
                if not isinstance(row.get("evidenceFiles"), list):
                    row["evidenceFiles"] = []
                row["evidenceFiles"].append({"storedName": stored_name, "originalName": original_name})
                break
        state["updatedAt"] = self._utc_now()
        self._save_state(tower_key, state)

    # Function: remove_evidence_file
    def remove_evidence_file(self, tower_key: str, row_id: str, stored_name: str) -> None:
        state = self._load_state(tower_key)
        for row in state["responses"]:
            if row["id"] == row_id:
                row["evidenceFiles"] = [
                    f for f in (row.get("evidenceFiles") or []) if f.get("storedName") != stored_name
                ]
                break
        state["updatedAt"] = self._utc_now()
        self._save_state(tower_key, state)

    # Function: _require_template
    def _require_template(self, tower_key: str) -> dict[str, Any]:
        if tower_key not in self.templates:
            raise KeyError(f"Unknown tower key: {tower_key}")
        return self.templates[tower_key]

    # Function: _load_state
    def _load_state(self, tower_key: str) -> dict[str, Any]:
        path = self.state_dir / f"{tower_key}.json"
        if path.exists():
            saved = json.loads(path.read_text(encoding="utf-8"))
            if len(saved.get("responses") or []) == len(self.templates[tower_key]["responses"]):
                return saved

        template_rows = self.templates[tower_key]["responses"]
        return {
            "towerKey": tower_key,
            "updatedAt": None,
            "responses": [
                {
                    "id": row["id"],
                    "selectedLevelKey": row.get("selectedLevelKey"),
                    "predictedWeight": row.get("predictedWeight"),
                    "evidence": row.get("evidence", ""),
                    "gapRecommendation": row.get("gapRecommendation", ""),
                    "recommendationSource": row.get("recommendationSource"),
                    "recommendationModel": row.get("recommendationModel"),
                    "evidenceFiles": row.get("evidenceFiles", []),
                }
                for row in template_rows
            ],
        }

    # Function: _save_state
    def _save_state(self, tower_key: str, state: dict[str, Any]) -> None:
        path = self.state_dir / f"{tower_key}.json"
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Function: _merge_response
    def _merge_response(self, template_row: dict[str, Any], state_row: dict[str, Any]) -> dict[str, Any]:
        row = copy.deepcopy(template_row)
        row["selectedLevelKey"] = self._normalize_level(state_row.get("selectedLevelKey"))
        row["defaultWeight"] = int(template_row["weight"])
        row["predictedWeight"] = self._normalize_weight(state_row.get("predictedWeight"))
        row["evidence"] = state_row.get("evidence") or ""
        row["gapRecommendation"] = state_row.get("gapRecommendation") or ""
        row["recommendationSource"] = state_row.get("recommendationSource")
        row["recommendationModel"] = state_row.get("recommendationModel")
        row["evidenceFiles"] = state_row.get("evidenceFiles") or []

        score = LEVEL_SCORE.get(row["selectedLevelKey"], 0)
        effective_weight = row["predictedWeight"] or 0
        row["weight"] = effective_weight
        row["score"] = score
        row["weightedScore"] = score * effective_weight if score and effective_weight else 0
        selected_option = next((option for option in row["maturityOptions"] if option["key"] == row["selectedLevelKey"]), None)
        row["selectedLevelLabel"] = selected_option["label"] if selected_option else ""
        row["selectedLevelDescription"] = selected_option["description"] if selected_option else ""
        return row

    # Function: _build_tower_summary
    def _build_tower_summary(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        answered = [row for row in responses if row["score"] > 0]
        answered_weight = sum(row["weight"] for row in answered)
        weighted_score = sum(row["weightedScore"] for row in answered)
        overall_score = round((weighted_score / (answered_weight * 4)) * 100, 2) if answered_weight else None

        dimension_metrics = []
        lowest_dimension = None
        for dimension in self._dimension_order_for_responses(responses):
            dimension_rows = [row for row in responses if row["dimension"] == dimension]
            answered_dimension_rows = [row for row in dimension_rows if row["score"] > 0]
            dimension_weight = sum(row["weight"] for row in answered_dimension_rows)
            dimension_score = sum(row["weightedScore"] for row in answered_dimension_rows)
            score_pct = round((dimension_score / (dimension_weight * 4)) * 100, 2) if dimension_weight else None
            metric = {
                "dimension": dimension,
                "scorePct": score_pct,
                "weightedScore": dimension_score,
                "answeredWeight": dimension_weight,
                "answeredQuestions": len(answered_dimension_rows),
                "totalQuestions": len(dimension_rows),
            }
            dimension_metrics.append(metric)
            if score_pct is not None and (lowest_dimension is None or score_pct < lowest_dimension["scorePct"]):
                lowest_dimension = metric

        return {
            "overallScorePct": overall_score,
            "overallLevel": self._score_to_level(overall_score),
            "answeredQuestions": len(answered),
            "totalQuestions": len(responses),
            "weightedScore": weighted_score,
            "answeredWeight": answered_weight,
            "topConcern": "Awaiting assessment inputs" if lowest_dimension is None else lowest_dimension["dimension"],
            "dimensionMetrics": dimension_metrics,
        }

    # Function: _dimension_order_for_responses
    def _dimension_order_for_responses(self, responses: list[dict[str, Any]]) -> list[str]:
        ordered = []
        for dimension in self.dashboard_template["dimensionOrder"]:
            if any(row["dimension"] == dimension for row in responses):
                ordered.append(dimension)
        for row in responses:
            if row["dimension"] not in ordered:
                ordered.append(row["dimension"])
        return ordered

    # Function: _score_to_level
    def _score_to_level(self, score: float | None) -> str | None:
        if score is None:
            return None
        if score < 40:
            return "Early"
        if score < 65:
            return "Emerging"
        if score < 85:
            return "Mature"
        return "Fully Mature"

    # Function: _normalize_level
    def _normalize_level(self, value: str | None) -> str | None:
        return value if value in LEVEL_SCORE else None

    # Function: _normalize_weight
    def _normalize_weight(self, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            return None
        return numeric if 1 <= numeric <= 10 else None

    # Function: _utc_now
    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # Function: _load_current_state_map
    def _load_current_state_map(self, dbdata_path: Path) -> dict[str, dict[str, Any]]:
        mapping: dict[str, dict[str, Any]] = {}
        with sqlite3.connect(dbdata_path) as connection:
            cursor = connection.cursor()
            rows = cursor.execute(
                """
                SELECT early_1, emerging_2, mature_3, fully_mature_4
                FROM dbdata
                """
            ).fetchall()

        for early_value, emerging_value, mature_value, fully_mature_value in rows:
            for level_key, score, description in (
                ("Early", 1, early_value),
                ("Emerging", 2, emerging_value),
                ("Mature", 3, mature_value),
                ("Fully Mature", 4, fully_mature_value),
            ):
                cleaned = (description or "").strip()
                if not cleaned:
                    continue
                mapping[cleaned] = {
                    "key": level_key,
                    "score": score,
                }
        return mapping
