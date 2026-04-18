#!/usr/bin/env python3
"""Debug the Jarvis agent directly"""

from jarvis.agent import GRAPH, AgentState, _extract_json
from jarvis.memory import init_db, add_episode
from jarvis.config import CFG

# Monkey patch to add debug prints
original_plan_node = None

def debug_plan_node(state: AgentState) -> AgentState:
    print(f"DEBUG: plan_node called with user_input: {state['user_input']}")
    from jarvis.agent import _get_llm, build_system_prompt
    
    llm = _get_llm()
    print(f"DEBUG: Using LLM: {llm}")
    
    system = build_system_prompt(state["user_input"])
    print(f"DEBUG: System prompt length: {len(system)}")
    
    context = state.get("tool_results", [])
    context_str = ""
    if context:
        last = context[-1]
        context_str = f"\n\nLast tool result ({last.get('tool','unknown')}):\n{last.get('output','')}"
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": state["user_input"] + context_str}
    ]
    print(f"DEBUG: Sending messages to LLM")
    
    response = llm.invoke(messages)
    print(f"DEBUG: LLM response: {response.content}")
    
    parsed = _extract_json(response.content)
    print(f"DEBUG: Parsed response: {parsed}")
    
    state["_plan"] = parsed
    return state

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
    print(f"Final result: {result}")
    
    if result.get("final_response"):
        print(f"Response: {result['final_response']}")
    else:
        print("No final response")

if __name__ == "__main__":
    test_agent()