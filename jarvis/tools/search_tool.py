from __future__ import annotations
from pathlib import Path
from jarvis.tools.base import BaseTool, ToolResult
import jarvis.memory as mem
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
WORKSPACE = Path(CFG["execution"]["workspace"])


class SearchTool(BaseTool):
    name = "search"
    description = "Semantically search memory, or do a text search across files in the workspace."
    works_offline = True

    def run(self, action: str, query: str, path: str = None) -> ToolResult:
        try:
            if action == "memory":
                results = mem.recall_memories(query)
                return ToolResult(success=True, output="\\n".join(f"- {r}" for r in results) or "Nothing found.")

            elif action == "files":
                search_root = Path(path).expanduser() if path else WORKSPACE
                matches = []
                for f in search_root.rglob("*"):
                    if f.is_file() and f.suffix in (".py", ".md", ".txt", ".toml", ".json", ".yaml", ".sh"):
                        try:
                            text = f.read_text(encoding="utf-8", errors="ignore")
                            if query.lower() in text.lower():
                                line_matches = [
                                    f"  L{i+1}: {line.strip()}"
                                    for i, line in enumerate(text.splitlines())
                                    if query.lower() in line.lower()
                                ]
                                matches.append(f"{f}\\n" + "\\n".join(line_matches[:3]))
                        except Exception:
                            pass
                if not matches:
                    return ToolResult(success=True, output=f"No files matched '{query}'.")
                return ToolResult(success=True, output="\\n\\n".join(matches[:10]))

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
