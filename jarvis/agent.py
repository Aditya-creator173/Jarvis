from __future__ import annotations
import json
import re
import os
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import jarvis.memory as mem
from jarvis.tools import TOOL_REGISTRY, list_tools
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)


def _get_llm():
    provider = CFG["model"].get("provider", "ollama")
    if provider == "openrouter":
        cfg = CFG["model"]["openrouter"]
        api_key = cfg.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            log.warning("OpenRouter API key not set, falling back to Ollama")
            provider = "ollama"
        else:
            return ChatOpenAI(
                model=cfg.get("model", "anthropic/claude-3.5-sonnet"),
                base_url=cfg.get("base_url", "https://openrouter.ai/api/v1"),
                api_key=api_key,
                temperature=CFG["model"].get("temperature", 0.1),
                max_tokens=CFG["model"].get("max_tokens", 2048),
            )

    if provider == "ollama":
        return ChatOllama(
            model=CFG["model"]["primary"],
            base_url=CFG["model"].get("base_url", "http://localhost:11434"),
            temperature=CFG["model"].get("temperature", 0.1),
            format="json"
        )

    raise ValueError(f"Unknown model provider: {provider}")

SYSTEM_PROMPT_TEMPLATE = """You are Jarvis, an offline-first personal AI operator. You execute real system tasks.

## YOUR TOOLS
{tools}

## RECENT CONVERSATION
{history}

## RELEVANT MEMORIES
{memories}

## WORKSPACE
{workspace}

## HOW TO RESPOND
Always respond with a valid JSON object. Choose ONE of:

1. Execute a tool:
{{"action": "tool", "tool": "<tool_name>", "params": {{...}}, "reasoning": "<why>"}}

2. Ask for confirmation (destructive ops only):
{{"action": "confirm", "message": "<what you're about to do and why>"}}

3. Respond to the user (task complete or no tool needed):
{{"action": "respond", "message": "<your response to the user>"}}

## RULES
- ALWAYS use a tool if the user's request can be fulfilled by one
- NEVER make up file contents or command outputs — run the tool and use real results
- For multi-step tasks, execute one tool at a time and chain the results
- If a tool fails, retry with corrected parameters up to 3 times, then respond with the error
- Destructive operations (delete, overwrite, shell commands outside allowlist) require action="confirm" first
- Do NOT go online unless the user explicitly says "search the web" or "look this up online"
- Be terse. One sentence max per response. The user is a developer who values clarity.
"""


class AgentState(TypedDict):
    user_input: str
    history: List[dict]
    memories: List[str]
    tool_results: List[dict]
    final_response: Optional[str]
    retry_count: int
    awaiting_confirm: Optional[str]


def build_system_prompt(user_input: str) -> str:
    memories = mem.recall_memories(user_input)
    history = mem.format_history_for_prompt(10)
    return SYSTEM_PROMPT_TEMPLATE.format(
        tools=list_tools(),
        history=history or "No prior history.",
        memories="\\n".join(f"- {m}" for m in memories) if memories else "No relevant memories.",
        workspace=CFG["execution"]["workspace"]
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from markdown code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try finding first { } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {"action": "respond", "message": text}


def _call_gemini_fallback(prompt: str, system: str) -> str:
    import os
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return '{"action": "respond", "message": "Gemini API key not set."}'

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.1,
            max_output_tokens=1024,
        )
    )
    return response.text


def plan_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    system = build_system_prompt(state["user_input"])
    context = state.get("tool_results", [])
    context_str = ""
    if context:
        last = context[-1]
        context_str = f"\\n\\nLast tool result ({last.get('tool','unknown')}):\\n{last.get('output','')}"

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=state["user_input"] + context_str)
    ]
    try:
        response = llm.invoke(messages)
        parsed = _extract_json(response.content)
        # If parsed is just a plain respond with no real content, treat as failure
        if not parsed or parsed.get("action") == "respond" and not parsed.get("message"):
            raise ValueError("Empty response from local model")
    except Exception as e:
        log.warning(f"Local model failed ({e}), falling back to Gemini...")
        raw = _call_gemini_fallback(
            prompt=state["user_input"],
            system=build_system_prompt(state["user_input"])
        )
        parsed = _extract_json(raw)
    log.info(f"Plan: {parsed}")
    # Store plan in tool_results as a special entry (langgraph may copy state)
    state["_plan"] = dict(parsed)  # Make a copy
    state["tool_results"] = state.get("tool_results", []) + [{"_plan": dict(parsed)}]
    return state


def execute_node(state: AgentState) -> AgentState:
    plan = state.get("_plan", {})
    if not plan:
        tool_results = state.get("tool_results", [])
        for tr in reversed(tool_results):
            if "_plan" in tr:
                plan = tr["_plan"]
                break
    action = plan.get("action", "respond")

    if action == "respond":
        state["final_response"] = plan.get("message", "Done.")
        return state

    if action == "confirm":
        state["awaiting_confirm"] = plan.get("message", "Confirm?")
        state["final_response"] = None
        return state

    # Handle action="tool" or when action IS the tool name (e.g., {"action": "fs", "params": {...}})
    tool_name = plan.get("tool") or (action if action != "tool" and action != "respond" and action != "confirm" else None)
    if tool_name:
        params = plan.get("params", {}).copy()
        # Auto-add action if tool expects it but it's not in params
        if "action" not in params and tool_name == "fs":
            # Infer action from params keys
            if "path" in params and "content" in params:
                params["action"] = "write"
            elif "path" in params:
                params["action"] = "read"
            elif "command" in params:
                # Shell command - use shell tool instead
                tool_name = "shell"
                params = {"command": params.pop("command")}
        tool = TOOL_REGISTRY.get(tool_name)
        if not tool:
            state["final_response"] = f"Unknown tool: {tool_name}"
            return state

        result = tool.run(**params)
        log.info(f"Tool '{tool_name}' result: success={result.success}")

        state["tool_results"] = state.get("tool_results", []) + [{
            "tool": tool_name,
            "params": params,
            "output": str(result),
            "success": result.success
        }]

        if not result.success:
            # If tool failed, respond with error instead of retrying blindly
            state["final_response"] = f"Tool '{tool_name}' failed: {result.error}"
            return state

    return state


def reflect_node(state: AgentState) -> AgentState:
    if state.get("final_response") or state.get("awaiting_confirm"):
        return state
    tool_results = state.get("tool_results", [])
    # If tool succeeded, we're done unless more work is needed
    if tool_results and tool_results[-1].get("success"):
        # Check if the result indicates more work needed
        last_output = tool_results[-1].get("output", "")
        if not any(x in last_output.lower() for x in ["error", "failed", "permission denied"]):
            state["final_response"] = "Done."
    return state


def should_continue(state: AgentState) -> str:
    if state.get("final_response") or state.get("awaiting_confirm"):
        return END
    if state.get("retry_count", 0) >= CFG["execution"]["max_retry_attempts"]:
        state["final_response"] = "Max retries reached. Could not complete the task."
        return END
    if len(state.get("tool_results", [])) >= 10:
        state["final_response"] = "Task execution limit reached."
        return END
    return "plan"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("plan", plan_node)
    g.add_node("execute", execute_node)
    g.add_node("reflect", reflect_node)
    g.set_entry_point("plan")
    g.add_edge("plan", "execute")
    g.add_edge("execute", "reflect")
    g.add_conditional_edges("reflect", should_continue, {"plan": "plan", END: END})
    return g.compile()

GRAPH = build_graph()
