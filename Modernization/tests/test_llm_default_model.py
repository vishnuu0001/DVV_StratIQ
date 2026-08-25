import unittest
from unittest.mock import patch

from services import llm
from services.requirements_documentation import REQUIREMENTS_PREFERRED_MODELS


class _Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "models": [
                {"name": "qwen3.5:9b"},
                {"name": "deepseek-coder:6.7b"},
            ]
        }


class ModernizationDefaultModelTests(unittest.TestCase):
    def test_deepseek_coder_is_the_shared_default(self):
        self.assertEqual(llm.DEEPSEEK_CODER_67B_MODEL, "deepseek-coder:6.7b")
        self.assertEqual(llm.PREFERRED_MODELS[0], llm.DEEPSEEK_CODER_67B_MODEL)
        self.assertEqual(llm.CODEGEN_PREFERRED_MODELS[0], llm.DEEPSEEK_CODER_67B_MODEL)
        self.assertEqual(REQUIREMENTS_PREFERRED_MODELS[0], llm.DEEPSEEK_CODER_67B_MODEL)

    def test_status_and_generation_select_deepseek_when_multiple_models_exist(self):
        with patch.object(llm._httpx, "get", return_value=_Response()):
            status = llm.check_status()
            selected = llm.pick_codegen_model()

        self.assertEqual(status["recommended"], "deepseek-coder:6.7b")
        self.assertEqual(status["active_model"], "deepseek-coder:6.7b")
        self.assertEqual(selected, "deepseek-coder:6.7b")


if __name__ == "__main__":
    unittest.main()
