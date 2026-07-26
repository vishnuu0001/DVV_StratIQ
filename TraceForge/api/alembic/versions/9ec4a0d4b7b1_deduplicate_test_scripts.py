# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Deduplicate generated scripts and enforce one row per test-case target.
# Date: 2025-11-08
# ---------------------------------------------------------------------------
"""Deduplicate generated scripts and enforce one row per test-case target.

Revision ID: 9ec4a0d4b7b1
Revises: 1c09d22c8873
"""
from alembic import op

revision = "9ec4a0d4b7b1"
down_revision = "1c09d22c8873"
branch_labels = None
depends_on = None


# Function: upgrade
def upgrade() -> None:
    op.execute(
        """
        DELETE FROM test_script AS older
        USING test_script AS newer
        WHERE older.test_case_id = newer.test_case_id
          AND older.target = newer.target
          AND older.ts_id < newer.ts_id
        """
    )
    op.create_unique_constraint(
        "uq_testscript_case_target", "test_script", ["test_case_id", "target"]
    )


# Function: downgrade
def downgrade() -> None:
    op.drop_constraint("uq_testscript_case_target", "test_script", type_="unique")
