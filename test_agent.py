#!/usr/bin/env python3
"""Test the Jarvis agent directly"""

from jarvis.agent import GRAPH, AgentState
from jarvis.memory import init_db, add_episode

def test_agent():
    # Initialize database
    init_db()
    
    # Test state
    state: AgentState = {
        "user_input": "What files are in the current directory?",
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }
    
    print("Invoking agent...")
    result = GRAPH.invoke(state)
    print(f"Result: {result}")
    
    if result.get("final_response"):
        print(f"Response: {result['final_response']}")
    else:
        print("No final response")

if __name__ == "__main__":
    test_agent()