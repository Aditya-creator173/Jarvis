from jarvis.agent import _get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json

llm = _get_llm()
print('LLM ready:', llm)

# Simple test
messages = [
    SystemMessage(content='You are a helpful assistant. Always respond with valid JSON.'),
    HumanMessage(content='Say hello in this format: {"message": "your text here"}')
]

print('Invoking LLM...')
response = llm.invoke(messages)
print('Response:', response.content)
try:
    parsed = json.loads(response.content)
    print('Parsed JSON:', parsed)
except:
    print('Not valid JSON')