#!/usr/bin/env python3
"""Final test of Jarvis agent"""

from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db

def test_agent():
    # Initialize database
    init_db()
    
    # Test 1: Simple query
    print("=== Test 1: List files ===")
    state: AgentState = {
        "user_input": "What files are in the current directory?",
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }
    
    result = GRAPH.invoke(state)
    print(f"Response: {result.get('final_response')}")
    print(f"Tool results: {len(result.get('tool_results', []))} tools used")
    
    # Test 2: Create a file
    print("\n=== Test 2: Create file ===")
    state2: AgentState = {
        "user_input": "Create a file called test.txt with content 'Hello from Jarvis'",
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }
    
    result2 = GRAPH.invoke(state2)
    print(f"Response: {result2.get('final_response')}")
    print(f"Tool results: {len(result2.get('tool_results', []))} tools used")
    
    # Test 3: Read the file
    print("\n=== Test 3: Read file ===")
    state3: AgentState = {
        "user_input": "Read the test.txt file",
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }
    
    result3 = GRAPH.invoke(state3)
    print(f"Response: {result3.get('final_response')}")
    print(f"Tool results: {len(result3.get('tool_results', []))} tools used")

if __name__ == "__main__":
    test_agent()