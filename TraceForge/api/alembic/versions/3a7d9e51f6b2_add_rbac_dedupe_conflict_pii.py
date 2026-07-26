# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Production hardening pass — dedup/conflict-detection columns on requirement,
#   PII-safe LLM I/O persistence columns on llm_call. Gate RBAC needs no schema change
#   (it reads project.config, already JSONB).
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""add rbac dedupe conflict pii columns

Revision ID: 3a7d9e51f6b2
Revises: 7f38b1a9c2d4
Create Date: 2026-07-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "3a7d9e51f6b2"
down_revision: Union[str, None] = "7f38b1a9c2d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Function: upgrade
def upgrade() -> None:
    op.add_column("requirement", sa.Column("merged_into_id", sa.UUID(), nullable=True))
    op.add_column(
        "requirement",
        sa.Column("conflict_flags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )
    op.create_foreign_key(
        "fk_requirement_merged_into_id", "requirement", "requirement", ["merged_into_id"], ["id"],
    )

    op.add_column("llm_call", sa.Column("prompt_text", sa.Text(), nullable=True))
    op.add_column("llm_call", sa.Column("completion_text", sa.Text(), nullable=True))
    op.add_column(
        "llm_call",
        sa.Column("pii_entity_map", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
    )


# Function: downgrade
def downgrade() -> None:
    op.drop_column("llm_call", "pii_entity_map")
    op.drop_column("llm_call", "completion_text")
    op.drop_column("llm_call", "prompt_text")

    op.drop_constraint("fk_requirement_merged_into_id", "requirement", type_="foreignkey")
    op.drop_column("requirement", "conflict_flags")
    op.drop_column("requirement", "merged_into_id")
