# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_java_repair_round_hardening.py)
# Date: 2026-08-14
# ---------------------------------------------------------------------------
"""Regression coverage for a job that ran without ever reaching closure.

A real Java generation job stalled forever mid-"repairing" phase: a
`ThreadPoolExecutor` batch used `with ThreadPoolExecutor(...) as executor:`
(which joins every submitted thread on exit) together with an unbounded
`as_completed()` wait, and the `generate()` call each worker made had no
wall-clock ceiling of its own. One slow/stuck Ollama call for a single file
was therefore enough to block the entire compiler-repair round — and with
it, the whole job — from ever completing.

These tests exercise `_pf_repair_build_round`, `_pf_repair_java_module_
boundaries`, and `_run_bounded_round` directly with a worker that never
returns, and assert the caller still gets control back within a bounded
time, with the stuck file reported as a (recoverable) failure rather than
the whole call hanging.
"""
import threading
import time
import unittest
from unittest.mock import patch

from services.modernizer._shared import _round_budget_seconds, _run_bounded_round
from services.modernizer.prompt_pipeline import (
    _pf_repair_build_round,
    _pf_repair_java_module_boundaries,
)


class RunBoundedRoundTests(unittest.TestCase):
    # Function: test_hung_future_does_not_block_the_round
    def test_hung_future_does_not_block_the_round(self):
        from concurrent.futures import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="hardening-test")
        try:
            fast = executor.submit(lambda: "ok")
            # Long enough to prove the round didn't wait for it, short enough
            # not to hang pytest's own process exit.
            stuck = executor.submit(lambda: time.sleep(2.0))
            futures = {fast: "fast.txt", stuck: "stuck.txt"}

            started = time.monotonic()
            done, timed_out = _run_bounded_round(
                executor, futures, round_budget_seconds=0.2, label="test round",
            )
            elapsed = time.monotonic() - started

            self.assertLess(elapsed, 1.5, "round wait should be bounded near the budget, not the hang")
            self.assertEqual({futures[f] for f in done}, {"fast.txt"})
            self.assertEqual(list(timed_out), ["stuck.txt"])
            self.assertIn("stuck.txt", timed_out)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    # Function: test_round_budget_scales_with_batches_not_item_count
    def test_round_budget_scales_with_batches_not_item_count(self):
        # 5 items / 2 workers -> 3 sequential batches worst case.
        self.assertAlmostEqual(_round_budget_seconds(5, 2, 100), 3 * 100 + 60)
        # Never smaller than the margin, even with no items.
        self.assertEqual(_round_budget_seconds(0, 2, 100), 60)


class RepairBuildRoundHardeningTests(unittest.TestCase):
    # Function: test_one_hung_repair_call_does_not_block_the_others
    def test_one_hung_repair_call_does_not_block_the_others(self):
        fixable = {
            "Demo/Fast.java": ["cannot find symbol: foo"],
            "Demo/Stuck.java": ["cannot find symbol: bar"],
        }
        output = {
            "Demo/Fast.java": "class Fast {}",
            "Demo/Stuck.java": "class Stuck {}",
        }

        # Function: fake_generate
        def fake_generate(prompt, **kwargs):
            # The repair prompt also lists every other project file by name
            # (the "AVAILABLE LOCAL SOURCE FILES" manifest), so match on the
            # precise "FILE PATH: <target>" line instead of a bare substring
            # to make sure only the call actually repairing Stuck.java hangs.
            if "FILE PATH: Demo/Stuck.java" in prompt:
                time.sleep(2.0)  # longer than the test's round budget below
            return "class Fast { void fixed() {} }"

        with patch("services.llm.generate", side_effect=fake_generate), \
             patch("services.modernizer._shared._REPAIR_CALL_MAX_SECONDS", 0.05), \
             patch(
                 "services.modernizer._shared._round_budget_seconds",
                 lambda *a, **k: 0.3,
             ):
            started = time.monotonic()
            failures = _pf_repair_build_round(
                fixable, 1, 2, output,
                synthesized_contracts="", namespace_map_text="",
                llm_model="test-model", system="system prompt",
                progress=lambda *a, **k: None,
            )
            elapsed = time.monotonic() - started

        self.assertLess(elapsed, 2.0, "a hung file must not block the whole repair round")
        self.assertIn("Demo/Stuck.java", failures)
        self.assertNotIn("Demo/Fast.java", failures)
        self.assertIn("fixed", output["Demo/Fast.java"])
        # The stuck file's pre-repair content is preserved, not clobbered.
        self.assertEqual(output["Demo/Stuck.java"], "class Stuck {}")


class BoundaryRepairHardeningTests(unittest.TestCase):
    # Function: test_empty_llm_response_does_not_crash_the_whole_repair
    def test_empty_llm_response_does_not_crash_the_whole_repair(self):
        """A single unparsable/empty repair response used to propagate
        uncaught out of the whole function (no try/except around
        future.result()), aborting the entire generation job over one bad
        response for one file. It must instead be recorded and skipped."""
        output = {
            "service-a/src/main/java/com/a/A.java": (
                "package com.a;\nimport com.b.B;\nclass A { B b; }\n"
            ),
            "service-b/src/main/java/com/b/B.java": "package com.b;\nclass B {}\n",
        }

        with patch("services.llm.generate", return_value=""), \
             patch("services.modernizer._shared._REPAIR_CALL_MAX_SECONDS", 5):
            # Must return normally (0 successful repairs), not raise.
            repaired = _pf_repair_java_module_boundaries(
                output, "test-model", "system prompt", progress=lambda *a, **k: None,
            )
        self.assertEqual(repaired, 0)


if __name__ == "__main__":
    unittest.main()
