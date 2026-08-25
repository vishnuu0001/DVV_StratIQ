const HIDDEN_MODEL_NAMES = /qwen\s*3\.5\s*[:\- ]?\s*9b/i;
const DEEPSEEK_CODER_67B = /deepseek[\s-]*coder\s*[:\- ]?\s*6\.7b/i;

export const modelDisplayName = (value, fallback = 'OpenSource LLM') => {
  const text = String(value || '').trim();
  if (!text || HIDDEN_MODEL_NAMES.test(text)) return fallback;
  if (DEEPSEEK_CODER_67B.test(text)) return 'DeepSeek-Coder 6.7B';
  return text;
};
