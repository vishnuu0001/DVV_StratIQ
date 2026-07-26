# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Import incidents from an Excel file into a ServiceNow table.
# Date: 2026-05-31
# ---------------------------------------------------------------------------
"""Import incidents from an Excel file into a ServiceNow table.

Usage examples:
	python InsertData.py
	python InsertData.py --table incident --sheet-name "Sheet1"
	python InsertData.py --dry-run

By default this script reads:
	Novastra-ITSM/data/Closed incidents until 19April-26.xlsx

Credentials can be supplied via environment variables:
	SN_INSTANCE_URL, SN_USERNAME, SN_PASSWORD

If variables are not provided, the script falls back to DEFAULT_INSTANCE_URL,
DEFAULT_USERNAME, and DEFAULT_PASSWORD defined in this module.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
import httpx
import pandas as pd


DEFAULT_INSTANCE_URL = ""
DEFAULT_USERNAME = ""
DEFAULT_PASSWORD = ""
DEFAULT_EXCEL_PATH = Path(__file__).resolve().parent / "data" / "Closed incidents until 19April-26.xlsx"
DEFAULT_CLOSE_CODE = "Solution provided"

# Map legacy/source resolution values into choices valid for this instance.
CLOSE_CODE_NORMALIZATION: Dict[str, str] = {
	"solved (permanently)": "Solution provided",
	"solved (work around)": "Workaround provided",
	"solved (workaround)": "Workaround provided",
	"known error": "Known error",
	"duplicate": "Duplicate",
	"no resolution provided": "No resolution provided",
	"resolved by caller": "Resolved by caller",
	"resolved by change": "Resolved by change",
	"resolved by problem": "Resolved by problem",
	"resolved by request": "Resolved by request",
	"solution provided": "Solution provided",
	"workaround provided": "Workaround provided",
	"user error": "User error",
}


# Common label -> ServiceNow field translations.
COLUMN_MAP: Dict[str, str] = {
	"short description": "short_description",
	"description": "description",
	"state": "state",
	"priority": "priority",
	"urgency": "urgency",
	"impact": "impact",
	"category": "category",
	"subcategory": "subcategory",
	"caller": "caller_id",
	"caller id": "caller_id",
	"assignment group": "assignment_group",
	"assigned to": "assigned_to",
	"close code": "close_code",
	"resolution code": "close_code",
	"close notes": "close_notes",
	"resolution notes": "close_notes",
	"cmdb ci": "cmdb_ci",
	"business service": "business_service",
	"opened by": "opened_by",
}

# Fields that should usually not be directly inserted for new records.
EXCLUDED_FIELDS = {
	"number",
	"sys_id",
	"sys_created_on",
	"sys_updated_on",
	"closed_at",
	"resolved_at",
}


@dataclass
class ServiceNowCredentials:
	instance_url: str
	username: str
	password: str


# Function: normalize_column_name
def normalize_column_name(name: str) -> str:
	return " ".join(str(name).strip().replace("_", " ").split()).lower()


# Function: to_servicenow_field
def to_servicenow_field(column_name: str) -> str:
	normalized = normalize_column_name(column_name)
	if normalized in COLUMN_MAP:
		return COLUMN_MAP[normalized]
	return normalized.replace(" ", "_")


# Function: normalize_close_code
def normalize_close_code(value: str, default_close_code: str) -> str:
	normalized = " ".join(str(value).strip().split()).lower()
	if normalized in CLOSE_CODE_NORMALIZATION:
		return CLOSE_CODE_NORMALIZATION[normalized]
	if value in CLOSE_CODE_NORMALIZATION.values():
		return value
	return default_close_code


# Function: load_credentials
def load_credentials() -> ServiceNowCredentials:
	env_instance = os.getenv("SN_INSTANCE_URL", "").strip()
	env_username = os.getenv("SN_USERNAME", "").strip()
	env_password = os.getenv("SN_PASSWORD", "").strip()

	if env_instance and env_username and env_password:
		return ServiceNowCredentials(env_instance.rstrip("/"), env_username, env_password)

	return ServiceNowCredentials(
		instance_url=DEFAULT_INSTANCE_URL,
		username=DEFAULT_USERNAME,
		password=DEFAULT_PASSWORD,
	)


# Function: _to_source_value
def _to_source_value(raw_value: Any) -> Any:
	"""Convert DataFrame cell values into JSON-safe source snapshot values."""
	if pd.isna(raw_value):
		return None
	if hasattr(raw_value, "isoformat"):
		try:
			return raw_value.isoformat()
		except Exception:
			pass
	if isinstance(raw_value, (str, int, float, bool)):
		return raw_value
	return str(raw_value)


# Function: _collect_payload_fields
def _collect_payload_fields(row: pd.Series) -> Tuple[Dict[str, str], str, Dict[str, Any]]:
	"""Walk the row's raw columns, building the ServiceNow payload, the original
	incident number (if excluded), and a JSON-safe snapshot of every source cell."""
	payload: Dict[str, str] = {}
	original_inc_number: str = ""
	source_row_snapshot: Dict[str, Any] = {}
	for raw_col, raw_value in row.items():
		source_key = normalize_column_name(str(raw_col)).replace(" ", "_")
		source_row_snapshot[source_key] = _to_source_value(raw_value)

		if pd.isna(raw_value):
			continue

		value = str(raw_value).strip()
		if not value:
			continue

		field_name = to_servicenow_field(str(raw_col))
		if field_name in EXCLUDED_FIELDS:
			# Preserve the original incident number so the RAG can find it
			# after ServiceNow sync (ServiceNow assigns a new number on insert).
			if field_name == "number":
				original_inc_number = value
			continue

		payload[field_name] = value

	return payload, original_inc_number, source_row_snapshot


# Function: _apply_short_description_default
def _apply_short_description_default(payload: Dict[str, str], row_index: int) -> None:
	if "short_description" not in payload:
		if "description" in payload and payload["description"]:
			payload["short_description"] = payload["description"][:120]
		else:
			payload["short_description"] = f"Imported incident row {row_index}"


# Function: _apply_close_code_defaults
def _apply_close_code_defaults(payload: Dict[str, str], default_close_code: str) -> None:
	# Some instances enforce this via data policy on incident creation.
	if "close_code" not in payload and default_close_code:
		payload["close_code"] = default_close_code
	elif "close_code" in payload:
		payload["close_code"] = normalize_close_code(payload["close_code"], default_close_code)

	state_text = payload.get("state", "").strip().lower()
	if state_text in {"closed", "resolved", "6", "7"}:
		if "close_code" not in payload and default_close_code:
			payload["close_code"] = default_close_code
		if "close_notes" not in payload:
			payload["close_notes"] = "Imported historical incident"


# Function: build_payload_from_row
def build_payload_from_row(row: pd.Series, row_index: int, default_close_code: str) -> Dict[str, str]:
	payload, original_inc_number, source_row_snapshot = _collect_payload_fields(row)

	_apply_short_description_default(payload, row_index)

	# Preserve the original Excel INC number in work_notes so that after
	# ServiceNow assigns a new number, the RAG pipeline can still find this
	# incident when users query by the original INC reference.
	if original_inc_number:
		existing_notes = payload.get("work_notes", "")
		prefix = f"[Original Incident Number: {original_inc_number}]"
		payload["work_notes"] = f"{prefix}\n{existing_notes}".strip() if existing_notes else prefix

	source_json = json.dumps(source_row_snapshot, ensure_ascii=True, separators=(",", ":"))
	existing_notes = payload.get("work_notes", "")
	source_block = f"[Source Row JSON] {source_json}"
	payload["work_notes"] = f"{source_block}\n{existing_notes}".strip() if existing_notes else source_block

	_apply_close_code_defaults(payload, default_close_code)

	return payload


# Function: load_excel_rows
def load_excel_rows(
	excel_path: Path,
	sheet_name: str | int | None,
	default_close_code: str,
) -> Iterable[Tuple[int, Dict[str, str]]]:
	if not excel_path.exists():
		raise FileNotFoundError(f"Excel file not found: {excel_path}")

	read_sheet = sheet_name if sheet_name is not None else 0
	dataframe = pd.read_excel(excel_path, sheet_name=read_sheet)

	if isinstance(dataframe, dict):
		if not dataframe:
			raise ValueError("No sheets found in the Excel workbook.")
		first_sheet_name = next(iter(dataframe))
		dataframe = dataframe[first_sheet_name]

	for idx, row in dataframe.iterrows():
		payload = build_payload_from_row(row, row_index=idx + 2, default_close_code=default_close_code)
		yield idx + 2, payload


# Function: _post_incident_with_retry
def _post_incident_with_retry(
	client: httpx.Client,
	payload: Dict[str, str],
	row_number: int,
	*,
	api_url: str,
	headers: dict,
	params: dict,
	credentials: ServiceNowCredentials,
	max_retries: int,
	retry_backoff_seconds: float,
) -> httpx.Response | None:
	last_error: Exception | None = None
	for attempt in range(1, max_retries + 1):
		try:
			return client.post(
				api_url,
				auth=(credentials.username, credentials.password),
				headers=headers,
				params=params,
				json=payload,
			)
		except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError, httpx.RequestError) as exc:
			last_error = exc
			if attempt >= max_retries:
				print(f"[FAILED] Row {row_number} -> transport error after {attempt} attempts: {exc}")
				return None
			sleep_seconds = retry_backoff_seconds * attempt
			print(
				f"[RETRY] Row {row_number} -> transport error ({exc}); "
				f"retry {attempt}/{max_retries} in {sleep_seconds:.1f}s"
			)
			time.sleep(sleep_seconds)

	if last_error is not None:
		print(f"[FAILED] Row {row_number} -> unexpected transport error: {last_error}")
	return None


# Function: _process_incident_row
def _process_incident_row(
	client: httpx.Client,
	excel_row_number: int,
	payload: Dict[str, str],
	*,
	api_url: str,
	headers: dict,
	params: dict,
	credentials: ServiceNowCredentials,
	max_retries: int,
	retry_backoff_seconds: float,
) -> Tuple[bool, str]:
	retry_kwargs = dict(
		api_url=api_url, headers=headers, params=params, credentials=credentials,
		max_retries=max_retries, retry_backoff_seconds=retry_backoff_seconds,
	)
	response = _post_incident_with_retry(client, payload, excel_row_number, **retry_kwargs)
	if response is None:
		return False, f"[FAILED] Row {excel_row_number} -> transport failure"

	# Some instances reject incoming group assignments via custom business rules.
	if response.status_code == 403 and "abort changes on group" in response.text.lower():
		retry_payload = dict(payload)
		retry_payload.pop("assignment_group", None)
		retry_payload.pop("assigned_to", None)
		response = _post_incident_with_retry(client, retry_payload, excel_row_number, **retry_kwargs)
		if response is None:
			return False, f"[FAILED] Row {excel_row_number} -> transport failure on retry"

	if response.status_code in (200, 201):
		result = response.json().get("result", {})
		incident_number = result.get("number", "<unknown>")
		sys_id = result.get("sys_id", "<unknown>")
		return True, f"[OK] Row {excel_row_number} -> number={incident_number}, sys_id={sys_id}"

	return False, f"[FAILED] Row {excel_row_number} -> HTTP {response.status_code}: {response.text[:500]}"


# Function: _run_concurrent_inserts
def _run_concurrent_inserts(process_row_fn, client: httpx.Client, row_items, max_workers: int, batch_size: int) -> Tuple[int, int]:
	success_count = 0
	failure_count = 0
	with ThreadPoolExecutor(max_workers=max_workers) as pool:
		pending = {}
		row_iter = iter(row_items)

		while True:
			while len(pending) < batch_size:
				try:
					row_num, payload = next(row_iter)
				except StopIteration:
					break
				pending[pool.submit(process_row_fn, client, row_num, payload)] = row_num

			if not pending:
				break

			done_future = next(as_completed(pending))
			pending.pop(done_future, None)
			ok, message = done_future.result()
			print(message)
			if ok:
				success_count += 1
			else:
				failure_count += 1

	return success_count, failure_count


# Function: insert_records
def insert_records(
	credentials: ServiceNowCredentials,
	table_name: str,
	rows: Iterable[Tuple[int, Dict[str, str]]],
	dry_run: bool,
	timeout_seconds: int,
	max_retries: int,
	retry_backoff_seconds: float,
	max_workers: int,
	batch_size: int,
) -> Tuple[int, int]:
	api_url = f"{credentials.instance_url}/api/now/table/{table_name.strip('/')}"
	headers = {"Accept": "application/json", "Content-Type": "application/json"}
	params = {"sysparm_input_display_value": "true"}

	row_items: List[Tuple[int, Dict[str, str]]] = list(rows)
	if dry_run:
		success_count = 0
		for excel_row_number, payload in row_items:
			print(f"[DRY-RUN] Row {excel_row_number}: {json.dumps(payload, ensure_ascii=True)}")
			success_count += 1
		return success_count, 0

	max_workers = max(1, max_workers)
	batch_size = max(1, batch_size)

	print(
		f"Using concurrent insert: workers={max_workers}, batch_size={batch_size}, "
		f"rows={len(row_items)}"
	)

	process_row_fn = functools.partial(
		_process_incident_row,
		api_url=api_url, headers=headers, params=params, credentials=credentials,
		max_retries=max_retries, retry_backoff_seconds=retry_backoff_seconds,
	)

	with httpx.Client(timeout=timeout_seconds) as client:
		return _run_concurrent_inserts(process_row_fn, client, row_items, max_workers, batch_size)


# Function: build_arg_parser
def build_arg_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Import Excel incidents into ServiceNow.")
	parser.add_argument(
		"--excel",
		type=Path,
		default=DEFAULT_EXCEL_PATH,
		help=f"Path to source Excel file (default: {DEFAULT_EXCEL_PATH})",
	)
	parser.add_argument(
		"--table",
		default="incident",
		help="ServiceNow table name (default: incident)",
	)
	parser.add_argument(
		"--sheet-name",
		default=None,
		help="Optional sheet name/index from the Excel file.",
	)
	parser.add_argument(
		"--timeout",
		type=int,
		default=30,
		help="HTTP timeout in seconds (default: 30)",
	)
	parser.add_argument(
		"--default-close-code",
		default=DEFAULT_CLOSE_CODE,
		help=(
			"Fallback value for incident close_code when missing in Excel "
			f"(default: {DEFAULT_CLOSE_CODE})"
		),
	)
	parser.add_argument(
		"--max-rows",
		type=int,
		default=0,
		help="Only process first N rows (default: 0 means all rows).",
	)
	parser.add_argument(
		"--start-row",
		type=int,
		default=2,
		help="Start processing from this Excel row number (default: 2).",
	)
	parser.add_argument(
		"--max-retries",
		type=int,
		default=5,
		help="Max retries for transient network/protocol errors per request (default: 5).",
	)
	parser.add_argument(
		"--retry-backoff",
		type=float,
		default=1.0,
		help="Base backoff in seconds between retries (default: 1.0).",
	)
	parser.add_argument(
		"--workers",
		type=int,
		default=8,
		help="Number of concurrent workers for inserts (default: 8).",
	)
	parser.add_argument(
		"--batch-size",
		type=int,
		default=200,
		help="How many rows to submit per batch (default: 200).",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Preview generated payloads without creating records in ServiceNow.",
	)
	return parser


# Function: main
def main() -> None:
	parser = build_arg_parser()
	args = parser.parse_args()

	credentials = load_credentials()
	print(f"Using instance: {credentials.instance_url}")
	print(f"Source Excel: {args.excel}")
	print(f"Target table: {args.table}")

	rows = list(load_excel_rows(args.excel, args.sheet_name, args.default_close_code))
	if args.start_row and args.start_row > 2:
		rows = [row for row in rows if row[0] >= args.start_row]
	if args.max_rows and args.max_rows > 0:
		rows = rows[: args.max_rows]
	print(f"Rows discovered: {len(rows)}")

	success, failed = insert_records(
		credentials=credentials,
		table_name=args.table,
		rows=rows,
		dry_run=args.dry_run,
		timeout_seconds=args.timeout,
		max_retries=args.max_retries,
		retry_backoff_seconds=args.retry_backoff,
		max_workers=args.workers,
		batch_size=args.batch_size,
	)

	print(f"Completed. Success={success}, Failed={failed}")
	if failed > 0:
		raise SystemExit(1)


if __name__ == "__main__":
	main()
