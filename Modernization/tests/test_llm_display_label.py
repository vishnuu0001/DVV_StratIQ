import inspect
import re
import unittest

from services.modernizer import _shared, conversion_pipeline, prompt_pipeline


class LLMDisplayLabelTests(unittest.TestCase):
    """[PROGRESS] messages like "[llm] 67% LLM (qwen3.5:9b): ..." must show a
    generic "LLM (Open Source)" label instead of the raw Ollama model tag.
    This is purely cosmetic: the actual model string passed to
    services.llm.generate() is untouched everywhere except inside these
    display strings — see _shared._LLM_DISPLAY_LABEL."""

    def test_display_label_value(self):
        self.assertEqual(_shared._LLM_DISPLAY_LABEL, "Open Source")

    def test_no_progress_message_interpolates_the_raw_model_name(self):
        # Any f-string of the shape f"LLM ({llm_model})" or "'LLM (' + llm_model"
        # would leak the raw Ollama model tag (e.g. "qwen3.5:9b") straight into
        # a user-facing [PROGRESS] log line. Every such construction must use
        # _LLM_DISPLAY_LABEL instead.
        leaking_patterns = [
            re.compile(r"LLM \(\{llm_model\}"),
            re.compile(r"'LLM \(' \+ llm_model"),
            re.compile(r'"LLM \(" \+ llm_model'),
        ]
        for module in (conversion_pipeline, prompt_pipeline):
            source = inspect.getsource(module)
            for pattern in leaking_patterns:
                self.assertNotRegex(
                    source, pattern,
                    f"{module.__name__} still interpolates the raw llm_model "
                    f"into a progress message ({pattern.pattern})",
                )

    def test_known_call_sites_use_the_display_label(self):
        # The 6 sites that build "LLM (...)" progress text must all reference
        # _LLM_DISPLAY_LABEL rather than the raw model variable: 1 in
        # conversion_pipeline.py (_mp_run_domain_generation) and 5 in
        # prompt_pipeline.py (_pf_try_single_file x2, _pf_run_plan_generation,
        # _pf_validate_manifest_for_duplicates, generate_from_prompt).
        conv_source = inspect.getsource(conversion_pipeline)
        self.assertIn("'LLM (' + _LLM_DISPLAY_LABEL + ')'", conv_source)

        pp_source = inspect.getsource(prompt_pipeline)
        occurrences = pp_source.count("LLM ({_LLM_DISPLAY_LABEL})")
        self.assertEqual(
            occurrences, 5,
            "expected exactly 5 prompt_pipeline.py progress messages using "
            "the 'LLM ({_LLM_DISPLAY_LABEL})' display form",
        )


if __name__ == "__main__":
    unittest.main()
