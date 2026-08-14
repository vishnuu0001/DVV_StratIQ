# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_job_stream_event_loop.py)
# Date: 2026-08-14
# ---------------------------------------------------------------------------
"""Regression test for the SSE job-stream endpoint's event-loop behaviour.

`GET /api/modernize/jobs/{job_id}/stream` used to call the synchronous
`queue.Queue.get(timeout=0.5)` directly inside an `async def` generator.
Because uvicorn runs a single-threaded asyncio event loop, that blocked the
*entire* process for up to 500ms on every idle poll — for as long as a
generation job's stream stayed open, every other request this process
served (the frontend's 2s job-status poll, health checks, other jobs'
streams) queued up behind it. That produced exactly the "connection is
unstable (transient network or upstream 502)" symptom reported against
long-running Java generation jobs, and made otherwise-successful jobs look
stuck to the frontend.

These tests assert the event loop stays responsive while the stream is
idle-waiting on an empty queue, and that queued events / terminal events
still make it out promptly. They exercise the endpoint directly rather than
via a real network client, since the real defect only manifests as event
loop starvation, not as an incorrect stream payload.
"""
import asyncio
import queue
import time
import unittest

from api import server


class JobStreamEventLoopTests(unittest.IsolatedAsyncioTestCase):
    # Function: _register_job
    def _register_job(self, job_id: str) -> queue.Queue:
        q = queue.Queue(maxsize=8)
        server._JOBS[job_id] = {
            "job_id": job_id, "status": "running", "phase": "llm", "events": [],
        }
        server._JOB_QUEUES[job_id] = q
        return q

    def tearDown(self):
        for job_id in list(server._JOBS):
            if job_id.startswith("stream-loop-test-"):
                server._JOBS.pop(job_id, None)
                server._JOB_QUEUES.pop(job_id, None)

    # Function: test_idle_stream_does_not_starve_the_event_loop
    async def test_idle_stream_does_not_starve_the_event_loop(self):
        """The idle 0.5s queue wait and an unrelated coroutine must overlap.

        If `queue.Queue.get(timeout=0.5)` still ran synchronously inside the
        generator, the event loop's single thread could not advance the
        heartbeat coroutine at all until that call returned: the two waits
        would serialize (~0.5s + ~0.6s). Offloaded via `asyncio.to_thread`,
        both waits run concurrently and the total is close to the longer of
        the two (~0.6s), not their sum. This is the same starvation that let
        one open generation-job stream stall the frontend's 2s status poll.
        """
        job_id = "stream-loop-test-idle"
        self._register_job(job_id)

        response = await server.stream_job(job_id)
        agen = response.body_iterator

        # Function: heartbeat
        async def heartbeat():
            for _ in range(30):
                await asyncio.sleep(0.02)  # 30 * 0.02s = 0.6s total

        # Function: consume_one_chunk
        async def consume_one_chunk():
            return await agen.__anext__()

        started = time.monotonic()
        chunk, _ = await asyncio.wait_for(
            asyncio.gather(consume_one_chunk(), heartbeat()), timeout=3.0,
        )
        elapsed = time.monotonic() - started

        self.assertIn(b"keepalive", chunk if isinstance(chunk, bytes) else chunk.encode())
        # Concurrent: ~max(0.5, 0.6) = 0.6s. Serialized (the bug): ~0.5 + 0.6
        # = 1.1s. 0.9s cleanly separates the two without being flaky.
        self.assertLess(elapsed, 0.9)

    # Function: test_queued_event_is_delivered_without_waiting_out_the_poll_interval
    async def test_queued_event_is_delivered_without_waiting_out_the_poll_interval(self):
        job_id = "stream-loop-test-fast-delivery"
        q = self._register_job(job_id)
        q.put_nowait({"type": "progress", "phase": "llm", "progress": 42})

        response = await server.stream_job(job_id)
        agen = response.body_iterator

        started = time.monotonic()
        chunk = await asyncio.wait_for(agen.__anext__(), timeout=1.0)
        elapsed = time.monotonic() - started

        self.assertIn("progress", chunk if isinstance(chunk, str) else chunk.decode())
        # A ready event must not be held back for the 0.5s idle-poll timeout.
        self.assertLess(elapsed, 0.4)

    # Function: test_terminal_event_closes_the_stream
    async def test_terminal_event_closes_the_stream(self):
        job_id = "stream-loop-test-terminal"
        q = self._register_job(job_id)
        q.put_nowait({"type": "complete", "progress": 100})

        response = await server.stream_job(job_id)
        agen = response.body_iterator

        chunk = await asyncio.wait_for(agen.__anext__(), timeout=1.0)
        self.assertIn("complete", chunk if isinstance(chunk, str) else chunk.decode())

        # Function: advance_past_terminal_event
        async def advance_past_terminal_event():
            await asyncio.wait_for(agen.__anext__(), timeout=1.0)

        with self.assertRaises(StopAsyncIteration):
            await advance_past_terminal_event()


if __name__ == "__main__":
    unittest.main()
