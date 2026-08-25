import sys
from types import SimpleNamespace

sys.modules.setdefault("ollama", SimpleNamespace(Client=object))

from services import ollama_client


class _FakeOllamaSdkClient:
    def list(self):
        return SimpleNamespace(models=[
            SimpleNamespace(model="qwen3.5:9b"),
            SimpleNamespace(model="qwen2.5-coder:3b"),
            SimpleNamespace(model="deepseek-coder:6.7b"),
        ])


def _client():
    client = ollama_client.OllamaClient.__new__(ollama_client.OllamaClient)
    client._client = _FakeOllamaSdkClient()
    return client


def test_deepseek_coder_is_code_analysis_default():
    assert ollama_client.DEFAULT_CODE_ANALYSIS_MODEL == "deepseek-coder:6.7b"
    assert ollama_client.RECOMMENDED_MODELS[0]["id"] == "deepseek-coder:6.7b"
    assert ollama_client.FAST_PREDICTION_MODELS[0] == "deepseek-coder:6.7b"


def test_general_and_prediction_selection_both_choose_deepseek():
    ollama_client._model_cache = {"model": None, "expires": 0.0}
    client = _client()

    assert client.best_available_model() == "deepseek-coder:6.7b"
    assert client.fast_prediction_model() == "deepseek-coder:6.7b"
