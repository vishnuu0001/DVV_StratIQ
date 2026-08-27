import inspect
import unittest

from services.modernizer import _shared, conversion_pipeline


class DomainWorkerConcurrencyTests(unittest.TestCase):
    """Ollama serializes inference on this VM's single GPU — sending several
    domains concurrently, of any language, just makes requests queue behind
    the one Ollama is actually running until their client-side HTTP deadline
    fires, which counts as a failure and retries. Directly observed: a
    3-domain C# run defaulting to min(len(domains), 5) = 3 concurrent workers
    produced 69 "Ollama generate transient error ... retrying: timed out" log
    entries from exactly this pattern, even though only one job was active.
    Java was already capped to 1 worker for this reason; every language must
    be, not just Java, since the single-GPU constraint applies regardless of
    which language is being generated."""

    def test_domain_worker_default_is_one_for_every_language(self):
        source = inspect.getsource(conversion_pipeline)
        self.assertIn('worker_default = "1"', source)
        self.assertNotIn('worker_default = "1" if lang == "java" else "5"', source)

    def test_dead_shared_constant_is_kept_in_sync(self):
        # _shared._DEFAULT_DOM_WORKERS isn't read anywhere (the live default
        # is resolved inline in conversion_pipeline.py) but a stale value here
        # could mislead a future reader — exactly the class of bug this
        # session already found once (domain_generators/java.py wiring the
        # wrong budget constant because two similarly-named constants existed).
        self.assertEqual(_shared._DEFAULT_DOM_WORKERS, 1)


if __name__ == "__main__":
    unittest.main()
