# Test the full pipeline
from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db
from jarvis.config import CFG

# Initialize database
init_db()
print('=== Jarvis Agent Test ===')
print('Model provider:', CFG["model"].get("provider", "ollama"))
if CFG["model"].get("provider") == "ollama":
    print('Ollama model:', CFG["model"]["primary"], 'at', CFG["model"].get("base_url", "http://localhost:11434"))
else:
    print('OpenRouter model:', CFG["model"]["openrouter"]["model"])

# Test 1: Simple query that should use fs tool
print('\n--- Test 1: List files ---')
state1: AgentState = {
    "user_input": "What files are in the current directory?",
    "history": [],
    "memories": [],
    "tool_results": [],
    "final_response": None,
    "retry_count": 0,
    "awaiting_confirm": None,
}

result1 = GRAPH.invoke(state1)
print('Response:', result1.get("final_response"))
print('Tools used:', [r.get("tool") for r in result1.get("tool_results", [])])

# Test 2: Create a file
print('\n--- Test 2: Create file ---')
state2: AgentState = {
    "user_input": "Create a file called test_jarvis.txt with content 'Jarvis is working!'",
    "history": [],
    "memories": [],
    "tool_results": [],
    "final_response": None,
    "retry_count": 0,
    "awaiting_confirm": None,
}

result2 = GRAPH.invoke(state2)
print('Response:', result2.get("final_response"))
print('Tools used:', [r.get("tool") for r in result2.get("tool_results", [])])

# Test 3: Read the file
print('\n--- Test 3: Read file ---')
state3: AgentState = {
    "user_input": "Read the test_jarvis.txt file",
    "history": [],
    "memories": [],
    "tool_results": [],
    "final_response": None,
    "retry_count": 0,
    "awaiting_confirm": None,
}

result3 = GRAPH.invoke(state3)
print('Response:', result3.get("final_response"))
print('Tools used:', [r.get("tool") for r in result3.get("tool_results", [])])

print('\n=== Test Complete ===')