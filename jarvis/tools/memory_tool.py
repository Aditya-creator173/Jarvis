from __future__ import annotations
from jarvis.tools.base import BaseTool, ToolResult
import jarvis.memory as mem
from jarvis.logger import get_logger

log = get_logger(__name__)


class MemoryTool(BaseTool):
    name = "memory"
    description = "Store a fact for future recall, or query stored memories by natural language."
    works_offline = True

    def run(self, action: str, fact: str = None, query: str = None) -> ToolResult:
        try:
            if action == "store":
                if not fact:
                    return ToolResult(success=False, output="", error="'fact' is required for store.")
                mem.store_memory(fact)
                return ToolResult(success=True, output=f"Stored: {fact}")

            elif action == "recall":
                if not query:
                    return ToolResult(success=False, output="", error="'query' is required for recall.")
                results = mem.recall_memories(query)
                if not results:
                    return ToolResult(success=True, output="No relevant memories found.")
                return ToolResult(success=True, output="\\n".join(f"- {r}" for r in results))

            elif action == "list_recent":
                eps = mem.get_recent_episodes(20)
                lines = [f"[{e['role']}] {e['content'][:80]}" for e in eps]
                return ToolResult(success=True, output="\\n".join(lines) or "No recent history.")

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            log.error(f"memory_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
