# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Supplier portal CSV drop adapter — watches a directory for new CSV files.
# Date: 2026-01-16
# ---------------------------------------------------------------------------
"""Supplier portal CSV drop adapter — watches a directory for new CSV files."""

from __future__ import annotations

import asyncio
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Coroutine

import structlog

from inspector.adapters.base import BaseAdapter
from inspector.envelope import AdapterEvent

logger = structlog.get_logger(__name__)

# Expected CSV columns for supplier PO delay files
_REQUIRED_COLUMNS = {"po_id", "supplier_id", "event_type"}


class SupplierPortalCsvAdapter(BaseAdapter):
    """Watches a drop directory for CSV files containing supplier events."""

    name = "supplier_portal_csv"

    # Function: __init__
    def __init__(
        self,
        config: dict[str, Any],
        on_event: Callable[[AdapterEvent], Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__(config)
        self._on_event = on_event
        self._drop_dir = Path(config.get("drop_dir", "/data/csv_drops"))
        self._running = False
        self._task: asyncio.Task[None] | None = None

    # Function: start
    async def start(self) -> None:
        if not self.enabled:
            return
        self._drop_dir.mkdir(parents=True, exist_ok=True)
        self._running = True
        self._task = asyncio.create_task(self._watch_loop(), name="csv_watcher")
        logger.info("csv_adapter.started", drop_dir=str(self._drop_dir))

    # Function: stop
    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("csv_adapter.stopped")

    # Function: _watch_loop
    async def _watch_loop(self) -> None:
        processed: set[str] = set()
        while self._running:
            try:
                for csv_file in sorted(self._drop_dir.glob("*.csv")):
                    if csv_file.name in processed:
                        continue
                    await self._process_file(csv_file)
                    processed.add(csv_file.name)
                    # Move to processed subdirectory
                    done_dir = self._drop_dir / "processed"
                    done_dir.mkdir(exist_ok=True)
                    csv_file.rename(done_dir / csv_file.name)
            except Exception:  # noqa: BLE001
                logger.exception("csv_adapter.watch_error")
            await asyncio.sleep(5)

    # Function: _process_file
    async def _process_file(self, path: Path) -> None:
        logger.info("csv_adapter.processing", file=path.name)
        text = path.read_text(encoding="utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        row_count = 0
        for row in reader:
            try:
                adapter_event = self._parse_row(dict(row))
                await self._on_event(adapter_event)
                self.record_event()
                row_count += 1
            except Exception:  # noqa: BLE001
                self.record_error(f"row parse error in {path.name}")
                logger.exception("csv_adapter.row_error", file=path.name)

        logger.info("csv_adapter.file_done", file=path.name, rows=row_count)

    # Function: _parse_row
    def _parse_row(self, row: dict[str, str]) -> AdapterEvent:
        event_type = row.get("event_type", "supplier.po.delayed")
        source_event_id = row.get("event_id") or row.get("id")

        raw_ts = row.get("event_timestamp") or row.get("timestamp")
        if raw_ts:
            source_timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            source_timestamp = datetime.now(timezone.utc)

        # Convert numeric strings for known numeric fields
        payload: dict[str, Any] = {}
        for k, v in row.items():
            if k in ("delay_days", "defect_rate", "short_pct", "spike_pct", "dwell_days"):
                try:
                    payload[k] = float(v) if "." in v else int(v)
                except (ValueError, TypeError):
                    payload[k] = v
            else:
                payload[k] = v

        return AdapterEvent(
            raw_payload=payload,
            source_system="supplier_portal",
            source_event_id=str(source_event_id) if source_event_id else None,
            event_type=event_type,
            source_timestamp=source_timestamp,
            adapter_name=self.name,
        )
