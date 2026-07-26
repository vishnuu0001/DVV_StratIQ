# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the deduplication stage.
# Date: 2025-11-07
# ---------------------------------------------------------------------------
"""Tests for the deduplication stage."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from inspector.normalizer.dedupe import is_duplicate


class TestIsDuplicate:
    # Function: test_first_occurrence_not_duplicate
    @pytest.mark.asyncio
    async def test_first_occurrence_not_duplicate(self, mock_redis: AsyncMock) -> None:
        mock_redis.set.return_value = True  # SET NX succeeded = new key
        result = await is_duplicate(mock_redis, "erp", "event-001")
        assert result is False
        mock_redis.set.assert_called_once_with(
            "inspector:dedupe:erp:event-001", "1", ex=86400, nx=True
        )

    # Function: test_second_occurrence_is_duplicate
    @pytest.mark.asyncio
    async def test_second_occurrence_is_duplicate(self, mock_redis: AsyncMock) -> None:
        mock_redis.set.return_value = None  # SET NX failed = key existed
        result = await is_duplicate(mock_redis, "erp", "event-001")
        assert result is True

    # Function: test_none_source_event_id_skips_dedupe
    @pytest.mark.asyncio
    async def test_none_source_event_id_skips_dedupe(self, mock_redis: AsyncMock) -> None:
        result = await is_duplicate(mock_redis, "erp", None)
        assert result is False
        mock_redis.set.assert_not_called()

    # Function: test_empty_source_event_id_skips_dedupe
    @pytest.mark.asyncio
    async def test_empty_source_event_id_skips_dedupe(self, mock_redis: AsyncMock) -> None:
        result = await is_duplicate(mock_redis, "erp", "")
        assert result is False
        mock_redis.set.assert_not_called()

    # Function: test_different_source_systems_independent
    @pytest.mark.asyncio
    async def test_different_source_systems_independent(self, mock_redis: AsyncMock) -> None:
        """Events with same ID from different systems should get different keys."""
        mock_redis.set.return_value = True

        await is_duplicate(mock_redis, "erp", "shared-id")
        await is_duplicate(mock_redis, "wms", "shared-id")

        calls = mock_redis.set.call_args_list
        assert calls[0][0][0] == "inspector:dedupe:erp:shared-id"
        assert calls[1][0][0] == "inspector:dedupe:wms:shared-id"
