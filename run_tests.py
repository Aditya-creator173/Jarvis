import sys
sys.stdout.reconfigure(line_buffering=True)

from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db

init_db()

queries = [
    "What is 5 + 3?",
    "Who are you?",
    "Create a file called hello.txt with content 'Hello Jarvis'",
    "Read the hello.txt file",
]

print("=== Jarvis Agent Tests ===\n")

for query in queries:
    state: AgentState = {
        "user_input": query,
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }
    result = GRAPH.invoke(state)
    print(f"Q: {query}")
    print(f"A: {result.get('final_response')}")
    print()

print("=== Tests Complete ===")