# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: add governance baselines
# Date: 2026-03-27
# ---------------------------------------------------------------------------
"""add governance baselines

Revision ID: 7f38b1a9c2d4
Revises: 9ec4a0d4b7b1
Create Date: 2026-07-23 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "7f38b1a9c2d4"
down_revision: Union[str, None] = "9ec4a0d4b7b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Function: upgrade
def upgrade() -> None:
    op.create_table(
        "baseline",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_baseline_project_name"),
        sa.UniqueConstraint("project_id", "sha256", name="uq_baseline_project_sha256"),
    )


# Function: downgrade
def downgrade() -> None:
    op.drop_table("baseline")
