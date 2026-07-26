# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: fix_stale_check_constraints
# Date: 2026-04-14
# ---------------------------------------------------------------------------
"""fix_stale_check_constraints

Migration 0002 (full_sdlc) added new ArtifactKind/TemplateKind/ScriptTarget
enum members to models.py but never updated the corresponding Postgres CHECK
constraints, which were still enforcing the pre-0002 value lists. This left
artifact.ck_kind rejecting FSD_DOCX/SOLUTION_DOC_DOCX/TEST_PLAN_DOCX,
template.ck_kind rejecting FSD/SOLUTION_DOC/TEST_PLAN, and test_script.ck_target
rejecting SELENIUM_TS -- silently failing every FSD/SolutionDoc/TestPlan/
Selenium-script insert with a CheckViolationError.

Revision ID: 1c09d22c8873
Revises: 9ccc5f1342c6
Create Date: 2026-07-12 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = '1c09d22c8873'
down_revision: Union[str, None] = '9ccc5f1342c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Function: upgrade
def upgrade() -> None:
    op.drop_constraint('ck_kind', 'artifact', type_='check')
    op.create_check_constraint(
        'ck_kind', 'artifact',
        "kind IN ('BRD_DOCX', 'FRD_DOCX', 'FSD_DOCX', 'SOLUTION_DOC_DOCX', 'TEST_PLAN_DOCX', "
        "'RTM_XLSX', 'TEST_PACK_ZIP', 'SCRIPT_BUNDLE_ZIP')",
    )

    op.drop_constraint('ck_kind', 'template', type_='check')
    op.create_check_constraint(
        'ck_kind', 'template',
        "kind IN ('BRD', 'FRD', 'FSD', 'SOLUTION_DOC', 'RTM', 'TEST_PLAN', 'TEST_CASE')",
    )

    op.drop_constraint('ck_target', 'test_script', type_='check')
    op.create_check_constraint(
        'ck_target', 'test_script',
        "target IN ('PLAYWRIGHT_TS', 'SELENIUM_TS', 'PYTEST', 'KARATE', 'TOSCA_XML', 'ROBOT')",
    )


# Function: downgrade
def downgrade() -> None:
    op.drop_constraint('ck_target', 'test_script', type_='check')
    op.create_check_constraint(
        'ck_target', 'test_script',
        "target IN ('PLAYWRIGHT_TS', 'PYTEST', 'KARATE', 'TOSCA_XML', 'ROBOT')",
    )

    op.drop_constraint('ck_kind', 'template', type_='check')
    op.create_check_constraint(
        'ck_kind', 'template',
        "kind IN ('BRD', 'FRD', 'RTM', 'TEST_CASE')",
    )

    op.drop_constraint('ck_kind', 'artifact', type_='check')
    op.create_check_constraint(
        'ck_kind', 'artifact',
        "kind IN ('BRD_DOCX', 'FRD_DOCX', 'RTM_XLSX', 'TEST_PACK_ZIP', 'SCRIPT_BUNDLE_ZIP')",
    )
