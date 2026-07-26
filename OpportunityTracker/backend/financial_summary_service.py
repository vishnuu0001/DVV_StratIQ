# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Deterministic Target/Actual/Gap financial summary for the Opportunity
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""Deterministic Target/Actual/Gap financial summary for the Opportunity
pipeline — pure functions, no LLM, no caching. Recomputed fresh from the live
`opportunities` table on every call, matching this module's existing "never
cache" convention (fy27_mn is a plain @property, Wave exports/rollups are
computed live per request) — row counts here are in the dozens, trivially
cheap to recompute on every request, so a create/update/delete on Opportunity
is reflected the instant the frontend re-fetches, with no invalidation logic
needed anywhere."""
from __future__ import annotations

import re
from collections import defaultdict

from sqlalchemy.orm import Session

from models import Opportunity

# Case/whitespace-tolerant — stage text is user-entered via the existing UI and
# will keep growing, so an exact string compare against "P5 Closed/Won" would
# silently stop matching the moment someone types the stage slightly differently.
_CLOSED_WON_PATTERN = re.compile(r"closed\s*/?\s*won", re.IGNORECASE)

# Rank used only to prioritize which OPEN deals to progress first when building
# the gap-closure plan — deals already further along the funnel are the
# cheapest/fastest to close, so they're offered first.
_STAGE_MATURITY_RANK = {
    "": 0,
    "p0-p2": 1,
    "p3 upside": 2,
    "p3.1 strong upside": 3,
}
_UNSPECIFIED_STAGE_LABEL = "Unspecified (data gap)"


# Function: is_closed_won_stage
def is_closed_won_stage(stage: str | None) -> bool:
    return bool(_CLOSED_WON_PATTERN.search(stage or ""))


# Function: _stage_rank
def _stage_rank(stage: str) -> int:
    return _STAGE_MATURITY_RANK.get((stage or "").strip().lower(), 1)  # unknown stages rank like early pipeline


# Function: _bucket_label
def _bucket_label(value: str) -> str:
    value = (value or "").strip()
    return value or _UNSPECIFIED_STAGE_LABEL


# Function: _group_totals
def _group_totals(opportunities: list[Opportunity], key_fn) -> list[dict]:
    target_by_key: dict[str, float] = defaultdict(float)
    actual_by_key: dict[str, float] = defaultdict(float)
    count_by_key: dict[str, int] = defaultdict(int)

    for opp in opportunities:
        key = key_fn(opp)
        target_by_key[key] += opp.fy27_mn
        count_by_key[key] += 1
        if is_closed_won_stage(opp.oppty_stage):
            actual_by_key[key] += opp.fy27_mn

    return [
        {
            "key": key,
            "count": count_by_key[key],
            "target_fy27_mn": round(target_by_key[key], 4),
            "actual_fy27_mn": round(actual_by_key[key], 4),
            "gap_fy27_mn": round(target_by_key[key] - actual_by_key[key], 4),
        }
        for key in target_by_key
    ]


# Function: compute_financial_summary
def compute_financial_summary(db: Session) -> dict:
    opportunities = db.query(Opportunity).all()

    target = sum(o.fy27_mn for o in opportunities)
    closed_won = [o for o in opportunities if is_closed_won_stage(o.oppty_stage)]
    actual = sum(o.fy27_mn for o in closed_won)
    gap = target - actual

    by_region = sorted(
        _group_totals(opportunities, lambda o: _bucket_label(o.region)),
        key=lambda r: -r["target_fy27_mn"],
    )
    by_stage = sorted(
        _group_totals(opportunities, lambda o: _bucket_label(o.oppty_stage)),
        key=lambda r: -r["target_fy27_mn"],
    )
    by_sub_vertical = sorted(
        _group_totals(opportunities, lambda o: _bucket_label(o.sub_vertical)),
        key=lambda r: -r["target_fy27_mn"],
    )

    blank_stage_count = sum(1 for o in opportunities if not (o.oppty_stage or "").strip())
    blank_region_count = sum(1 for o in opportunities if not (o.region or "").strip())
    blank_owner_count = sum(1 for o in opportunities if not (o.oppty_owner or "").strip())

    # Gap-closure plan: open (non-Closed/Won) deals ranked by stage maturity desc,
    # then value desc — i.e. prefer deals already furthest along — accumulated
    # until the running total covers the gap. This is the concrete, deterministic
    # answer to "what's required to achieve target," computed before any LLM call.
    open_deals = [o for o in opportunities if not is_closed_won_stage(o.oppty_stage) and o.fy27_mn > 0]
    open_deals.sort(key=lambda o: (-_stage_rank(o.oppty_stage), -o.fy27_mn))

    gap_closure_plan = []
    running_total = 0.0
    deals_needed = 0
    for opp in open_deals:
        if running_total >= gap > 0:
            break
        running_total += opp.fy27_mn
        deals_needed += 1
        gap_closure_plan.append({
            "id": opp.id,
            "opportunity_name": opp.opportunity_name,
            "customer_group": opp.customer_group,
            "oppty_stage": opp.oppty_stage or _UNSPECIFIED_STAGE_LABEL,
            "fy27_mn": round(opp.fy27_mn, 4),
            "running_total_fy27_mn": round(running_total, 4),
        })

    attainment_pct = round((actual / target) * 100, 1) if target > 0 else 0.0

    return {
        "target_fy27_mn": round(target, 4),
        "actual_fy27_mn": round(actual, 4),
        "gap_fy27_mn": round(gap, 4),
        # Pre-computed so the LLM narrative quotes this verbatim rather than
        # computing its own percentage — the one time this wasn't pre-supplied,
        # the model computed a noticeably wrong figure (36% vs the correct ~32%).
        "attainment_pct": attainment_pct,
        "opportunity_count": len(opportunities),
        "closed_won_count": len(closed_won),
        "by_region": by_region,
        "by_stage": by_stage,
        "by_sub_vertical": by_sub_vertical,
        "data_quality": {
            "blank_stage_count": blank_stage_count,
            "blank_region_count": blank_region_count,
            "blank_owner_count": blank_owner_count,
        },
        "gap_closure_plan": gap_closure_plan,
        "deals_needed_to_close_gap": deals_needed if gap > 0 else 0,
    }
