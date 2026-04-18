from jarvis.agent import _get_llm
import json

llm = _get_llm()
print('Testing LLM...')
try:
    # Test with a simple prompt that should return JSON
    response = llm.invoke("Respond with valid JSON only: {\"message\": \"hello\"}")
    print('Raw response:', repr(response.content))
    # Try to parse
    parsed = json.loads(response.content)
    print('Parsed:', parsed)
except json.JSONDecodeError as e:
    print('JSON decode error:', e)
    print('Content:', response.content)
except Exception as e:
    print('Other error:', type(e).__name__, str(e))