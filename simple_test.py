from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db

# Initialize database
init_db()

# Test the agent with a simple file creation request
state: AgentState = {
    'user_input': 'Create a file named agent_test.txt with content "Agent test successful"',
    'history': [],
    'memories': [],
    'tool_results': [],
    'final_response': None,
    'retry_count': 0,
    'awaiting_confirm': None,
}

print('Invoking agent...')
result = GRAPH.invoke(state)
print('Final response:', result.get('final_response'))
print('Tool used:', result.get('tool_results', [])[0]['tool'] if result.get('tool_results') else 'None')