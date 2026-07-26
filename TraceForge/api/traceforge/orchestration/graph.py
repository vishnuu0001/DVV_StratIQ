# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.1 state machine as a LangGraph StateGraph (spec's explicit [DEFAULT] — 'If you
# Date: 2026-06-28
# ---------------------------------------------------------------------------
"""§6.1 state machine as a LangGraph StateGraph (spec's explicit [DEFAULT] — 'If you
deviate, hand-roll an explicit state machine; do NOT use naive sequential chains').

INGEST -> EXTRACT -[Gate 1]-> BRD -[Gate 2]-> TEST_DESIGN -[Gate 3]-> SCRIPT_GEN -[Gate 4]-> RENDER

The gate check itself lives in orchestration/gates.py and is DB-backed (not LangGraph's
interrupt/resume machinery) — every node calls assert_stage_unblocked() (via the shared
task bodies in workers/tasks.py, which this graph's nodes delegate to) before doing real
work, so the block holds even if something calls this graph directly instead of going
through the API.

Note on the live execution path: in production, the API enqueues a stage's Arq job
directly (routers/runs.py's `_STAGE_JOB` map -> workers/tasks.py) rather than driving
this graph — Arq is the actual job *queue* (retries, worker-process isolation), while
this graph is the actual pipeline *shape* (used by the Overview page's DAG and as the
single source of truth for stage ordering). Both call the same task bodies, so they
can never drift into disagreeing about what stage comes next.
"""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from traceforge.workers.tasks import run_brd_stage, run_extract_stage, run_render_stage, run_script_gen_stage, run_test_design_stage


class PipelineState(TypedDict):
    project_id: str
    pipeline_run_id: str
    stage: str
    result: dict


# Function: _stage_node
def _stage_node(task_fn, next_stage: str | None):
    # Function: node
    async def node(state: PipelineState) -> PipelineState:
        result = await task_fn(None, state["pipeline_run_id"])
        return {**state, "stage": next_stage or state["stage"], "result": result}

    return node


# Function: build_graph
def build_graph():
    builder = StateGraph(PipelineState)
    builder.add_node("EXTRACT", _stage_node(run_extract_stage, "BRD"))
    builder.add_node("BRD", _stage_node(run_brd_stage, "TEST_DESIGN"))
    builder.add_node("TEST_DESIGN", _stage_node(run_test_design_stage, "SCRIPT_GEN"))
    builder.add_node("SCRIPT_GEN", _stage_node(run_script_gen_stage, "RENDER"))
    builder.add_node("RENDER", _stage_node(run_render_stage, None))

    builder.set_entry_point("EXTRACT")
    builder.add_edge("EXTRACT", "BRD")
    builder.add_edge("BRD", "TEST_DESIGN")
    builder.add_edge("TEST_DESIGN", "SCRIPT_GEN")
    builder.add_edge("SCRIPT_GEN", "RENDER")
    builder.add_edge("RENDER", END)

    # Gates 1-4 sit between every stage after EXTRACT — interrupt_before marks that
    # shape explicitly, even though the authoritative block is the DB check inside
    # each stage task (assert_stage_unblocked, called by every task body above).
    return builder.compile(interrupt_before=["BRD", "TEST_DESIGN", "SCRIPT_GEN", "RENDER"])
