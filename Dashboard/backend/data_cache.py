# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: In-memory DataCache singleton.
# Date: 2025-07-12
# ---------------------------------------------------------------------------
"""
In-memory DataCache singleton.

Responsibilities
----------------
* Hold the three canonical DataFrames (incidents, changes, service_requests).
* Load from ServiceNow via sn_client or from an XLSX fallback.
* Parse / normalise date columns and derive computed columns.
* Expose thread-safe read/write access via a threading.Lock.
"""

import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from sn_client import ServiceNowClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name constants
# ---------------------------------------------------------------------------

DATE_COLUMNS_INCIDENT = ["opened_at", "resolved_at", "closed_at"]
DATE_COLUMNS_CHANGE = [
    "opened_at", "start_date", "end_date", "actual_start", "actual_end", "closed_at",
]
DATE_COLUMNS_SR = ["opened_at", "closed_at", "due_date"]

# XLSX sheet names (case-insensitive matching attempted)
XLSX_SHEET_MAP = {
    "incidents": "Incidents",
    "changes": "Changes",
    "service_requests": "ServiceRequests",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

# Function: _parse_dates
def _parse_dates(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    """Convert listed columns to pandas datetime (UTC-aware), coercing errors."""
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    return df


# Function: _add_incident_derived
def _add_incident_derived(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "resolved_at" in df.columns and "opened_at" in df.columns:
        df["resolution_hours"] = (
            (df["resolved_at"] - df["opened_at"]).dt.total_seconds() / 3600
        )
        df["resolution_hours"] = df["resolution_hours"].where(df["resolution_hours"] >= 0, other=pd.NA)
    if "opened_at" in df.columns:
        df["month_year"] = df["opened_at"].dt.to_period("M")
    return df


# Function: _add_change_derived
def _add_change_derived(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "actual_end" in df.columns and "actual_start" in df.columns:
        df["implementation_hours"] = (
            (df["actual_end"] - df["actual_start"]).dt.total_seconds() / 3600
        )
        df["implementation_hours"] = df["implementation_hours"].where(
            df["implementation_hours"] >= 0, other=pd.NA
        )
    if "opened_at" in df.columns:
        df["month_year"] = df["opened_at"].dt.to_period("M")
    return df


# Function: _add_sr_derived
def _add_sr_derived(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "closed_at" in df.columns and "opened_at" in df.columns:
        df["closure_hours"] = (
            (df["closed_at"] - df["opened_at"]).dt.total_seconds() / 3600
        )
        df["closure_hours"] = df["closure_hours"].where(df["closure_hours"] >= 0, other=pd.NA)
    if "opened_at" in df.columns:
        df["month_year"] = df["opened_at"].dt.to_period("M")
    return df


# Function: _normalise_priority
def _normalise_priority(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure priority is a numeric-friendly string (1/2/3/4) where possible."""
    if "priority" not in df.columns:
        return df
    mapping = {
        "1 - critical": "1", "1-critical": "1", "critical": "1",
        "2 - high": "2", "2-high": "2", "high": "2",
        "3 - moderate": "3", "3-moderate": "3", "moderate": "3", "medium": "3",
        "4 - low": "4", "4-low": "4", "low": "4",
        "5 - planning": "5", "planning": "5",
    }
    df["priority"] = (
        df["priority"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda v: mapping.get(v, v.split(" ")[0] if v else v))
    )
    return df


# ---------------------------------------------------------------------------
# Singleton DataCache
# ---------------------------------------------------------------------------

class DataCache:
    """Thread-safe, in-memory cache for all ServiceNow DataFrames."""

    _instance: Optional["DataCache"] = None
    _creation_lock = threading.Lock()

    # Function: __new__
    def __new__(cls) -> "DataCache":
        if cls._instance is None:
            with cls._creation_lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._lock = threading.Lock()
                    inst._incidents_df: pd.DataFrame = pd.DataFrame()
                    inst._changes_df: pd.DataFrame = pd.DataFrame()
                    inst._service_requests_df: pd.DataFrame = pd.DataFrame()
                    inst._last_synced_at: Optional[datetime] = None
                    cls._instance = inst
        return cls._instance

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    # Function: incidents_df
    @property
    def incidents_df(self) -> pd.DataFrame:
        with self._lock:
            return self._incidents_df.copy()

    # Function: changes_df
    @property
    def changes_df(self) -> pd.DataFrame:
        with self._lock:
            return self._changes_df.copy()

    # Function: service_requests_df
    @property
    def service_requests_df(self) -> pd.DataFrame:
        with self._lock:
            return self._service_requests_df.copy()

    # Function: is_loaded
    @property
    def is_loaded(self) -> bool:
        with self._lock:
            return (
                not self._incidents_df.empty
                or not self._changes_df.empty
                or not self._service_requests_df.empty
            )

    # Function: last_synced_at
    @property
    def last_synced_at(self) -> Optional[datetime]:
        with self._lock:
            return self._last_synced_at

    # Function: record_counts
    @property
    def record_counts(self) -> dict:
        with self._lock:
            return {
                "incidents": len(self._incidents_df),
                "changes": len(self._changes_df),
                "service_requests": len(self._service_requests_df),
            }

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    # Function: load_from_servicenow
    def load_from_servicenow(self, client: ServiceNowClient) -> None:
        """Fetch all data from ServiceNow, transform, and store."""
        logger.info("Loading data from ServiceNow…")

        incidents_raw = client.fetch_incidents()
        changes_raw = client.fetch_changes()
        sr_raw = client.fetch_service_requests()

        inc_df = self._process_incidents(pd.DataFrame(incidents_raw))
        chg_df = self._process_changes(pd.DataFrame(changes_raw))
        sr_df = self._process_service_requests(pd.DataFrame(sr_raw))

        with self._lock:
            self._incidents_df = inc_df
            self._changes_df = chg_df
            self._service_requests_df = sr_df
            self._last_synced_at = datetime.now(tz=timezone.utc)

        logger.info(
            "Data loaded: %d incidents, %d changes, %d SRs",
            len(inc_df), len(chg_df), len(sr_df),
        )

    # Function: load_from_xlsx
    def load_from_xlsx(self, path: Path) -> None:
        """
        Load data from an XLSX workbook as an offline fallback.
        Expected sheets: Incidents, Changes, ServiceRequests.
        Any missing sheet is silently replaced with an empty DataFrame.
        """
        logger.info("Loading data from XLSX: %s", path)
        xl = pd.ExcelFile(path, engine="openpyxl")
        sheet_names_lower = {s.lower(): s for s in xl.sheet_names}

        # Function: _read_sheet
        def _read_sheet(key: str) -> pd.DataFrame:
            # Try exact name first, then case-insensitive lookup
            canonical = XLSX_SHEET_MAP[key]
            actual = sheet_names_lower.get(canonical.lower()) or sheet_names_lower.get(key)
            if actual:
                return xl.parse(actual)
            logger.warning("Sheet '%s' not found in %s – using empty DataFrame.", canonical, path)
            return pd.DataFrame()

        inc_df = self._process_incidents(_read_sheet("incidents"))
        chg_df = self._process_changes(_read_sheet("changes"))
        sr_df = self._process_service_requests(_read_sheet("service_requests"))

        with self._lock:
            self._incidents_df = inc_df
            self._changes_df = chg_df
            self._service_requests_df = sr_df
            self._last_synced_at = datetime.now(tz=timezone.utc)

        logger.info(
            "XLSX loaded: %d incidents, %d changes, %d SRs",
            len(inc_df), len(chg_df), len(sr_df),
        )

    # Function: clear
    def clear(self) -> None:
        """Reset the cache to an empty state."""
        with self._lock:
            self._incidents_df = pd.DataFrame()
            self._changes_df = pd.DataFrame()
            self._service_requests_df = pd.DataFrame()
            self._last_synced_at = None

    # Function: inject_rows
    def inject_rows(self, extra_df: pd.DataFrame) -> None:
        """
        Append synthetic/invoked incident rows into the incidents cache without
        overwriting existing data.  Duplicate numbers are skipped.
        """
        if extra_df.empty:
            return
        with self._lock:
            if self._incidents_df.empty:
                self._incidents_df = extra_df.copy()
                return
            existing_nums = set(self._incidents_df["number"].astype(str).tolist())
            new_rows = extra_df[~extra_df["number"].astype(str).isin(existing_nums)]
            if not new_rows.empty:
                self._incidents_df = pd.concat(
                    [self._incidents_df, new_rows], ignore_index=True
                )

    # ------------------------------------------------------------------
    # ETL helpers
    # ------------------------------------------------------------------

    # Function: _process_incidents
    @staticmethod
    def _process_incidents(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = _parse_dates(df, DATE_COLUMNS_INCIDENT)
        df = _normalise_priority(df)
        df = _add_incident_derived(df)
        return df.reset_index(drop=True)

    # Function: _process_changes
    @staticmethod
    def _process_changes(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = _parse_dates(df, DATE_COLUMNS_CHANGE)
        df = _normalise_priority(df)
        df = _add_change_derived(df)
        return df.reset_index(drop=True)

    # Function: _process_service_requests
    @staticmethod
    def _process_service_requests(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = _parse_dates(df, DATE_COLUMNS_SR)
        df = _normalise_priority(df)
        df = _add_sr_derived(df)
        return df.reset_index(drop=True)


# Module-level singleton
cache = DataCache()
