import sys
from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db

init_db()
state = {
    'user_input': 'hello',
    'history': [],
    'memories': [],
    'tool_results': [],
    'final_response': None,
    'retry_count': 0,
    'awaiting_confirm': None,
}

print("Invoking agent...", file=sys.stderr)
result = GRAPH.invoke(state)
print(f"Response: {result.get('final_response')}")
print(f"Tool results: {result.get('tool_results')}")
print("Done!")