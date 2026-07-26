"""Initial schema: canonical_events, event_replays, adapter_health_snapshots.

Revision ID: 001
Revises:
Create Date: 2026-06-27 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── canonical_events ────────────────────────────────────────────────────
    op.create_table(
        "canonical_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("correlation_id", sa.Text(), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("original_event_type", sa.Text(), nullable=True),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("source_system", sa.Text(), nullable=False),
        sa.Column("source_event_id", sa.Text(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("root_node_id", sa.Text(), nullable=True),
        sa.Column(
            "related_node_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("stream_name", sa.Text(), nullable=True),
        sa.Column("publish_status", sa.Text(), nullable=True),
        sa.Column("validation_status", sa.Text(), nullable=True),
        sa.Column(
            "validation_errors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("replay_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_canonical_events_event_id",
        "canonical_events",
        ["event_id"],
        unique=True,
    )
    op.create_index(
        "ix_canonical_events_event_type",
        "canonical_events",
        ["event_type"],
    )
    op.create_index(
        "ix_canonical_events_source_system",
        "canonical_events",
        ["source_system"],
    )
    op.create_index(
        "ix_canonical_events_severity",
        "canonical_events",
        ["severity"],
    )
    op.create_index(
        "ix_canonical_events_ingested_at",
        "canonical_events",
        ["ingested_at"],
    )
    op.create_index(
        "ix_canonical_events_root_node_id",
        "canonical_events",
        ["root_node_id"],
    )

    # ── event_replays ───────────────────────────────────────────────────────
    op.create_table(
        "event_replays",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("replayed_by", sa.Text(), nullable=True),
        sa.Column(
            "replayed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column("target_stream", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_event_replays_event_id",
        "event_replays",
        ["event_id"],
    )

    # ── adapter_health_snapshots ────────────────────────────────────────────
    op.create_table(
        "adapter_health_snapshots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("adapter_name", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("events_last_5m", sa.Integer(), nullable=True),
        sa.Column("error_rate_5m", sa.Numeric(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_adapter_health_snapshots_adapter_name",
        "adapter_health_snapshots",
        ["adapter_name"],
    )


def downgrade() -> None:
    op.drop_table("adapter_health_snapshots")
    op.drop_table("event_replays")
    op.drop_table("canonical_events")
