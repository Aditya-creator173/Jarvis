from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db
import json

# Initialize database
init_db()
print('Database initialized')

# Test state with a simple query that should trigger the fs tool
state: AgentState = {
    'user_input': 'List files in current directory',
    'history': [],
    'memories': [],
    'tool_results': [],
    'final_response': None,
    'retry_count': 0,
    'awaiting_confirm': None,
}

print('Invoking agent with query: List files in current directory')
result = GRAPH.invoke(state)
print('Result keys:', list(result.keys()))
print('Final response:', result.get('final_response'))
print('Tool results count:', len(result.get('tool_results', [])))
if result.get('tool_results'):
    for i, tool_result in enumerate(result['tool_results']):
        print(f'  Tool {i}: {tool_result.get("tool")} - Success: {tool_result.get("success")}')
        if tool_result.get('output'):
            print(f'    Output: {tool_result["output"][:100]}...')