const HIDDEN_MODEL_NAMES = /qwen\s*3\.5\s*[:\- ]?\s*9b/i;

export const modelDisplayName = (value, fallback = 'OpenSource LLM') => {
  const text = String(value || '').trim();
  if (!text || HIDDEN_MODEL_NAMES.test(text)) return fallback;
  return text;
};
