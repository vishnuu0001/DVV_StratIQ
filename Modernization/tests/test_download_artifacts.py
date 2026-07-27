import asyncio
import io
import json
import unittest
import zipfile

from api import server


async def _response_bytes(response) -> bytes:
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    return b"".join(chunks)


class DownloadArtifactTests(unittest.TestCase):
    def test_validation_failed_job_downloads_labeled_review_archive(self):
        job_id = "review-job"
        server._JOBS[job_id] = {
            "job_id": job_id,
            "status": "validation_failed",
            "folder_path": r"C:\source\legacy-app",
            "output": {"Demo/src/app.ts": "export const ok = true;"},
            "validation": {"failed": 1, "files": [{"path": "Demo/src/app.ts"}]},
        }
        try:
            response = asyncio.run(server.download_output(job_id))
            body = asyncio.run(_response_bytes(response))
        finally:
            server._JOBS.pop(job_id, None)

        self.assertEqual("validation_failed", response.headers["x-artifact-status"])
        self.assertIn("review_required_legacy-app.zip", response.headers["content-disposition"])
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            self.assertIn("Demo/src/app.ts", archive.namelist())
            self.assertIn("REVIEW_REQUIRED.md", archive.namelist())
            report = json.loads(archive.read("validation-report.json"))
            self.assertEqual(1, report["failed"])


if __name__ == "__main__":
    unittest.main()
