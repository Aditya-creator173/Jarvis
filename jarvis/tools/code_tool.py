from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
from jarvis.tools.base import BaseTool, ToolResult
from jarvis.tools.shell_tool import ShellTool
from jarvis.logger import get_logger

log = get_logger(__name__)
_shell = ShellTool()


class CodeTool(BaseTool):
    name = "code"
    description = "Scaffold code files, run Python scripts, lint with ruff, explain errors."
    works_offline = True

    def run(self, action: str, path: str = None, code: str = None,
            language: str = "python") -> ToolResult:
        try:
            if action == "scaffold":
                p = Path(path).expanduser()
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(code or "", encoding="utf-8")
                return ToolResult(success=True, output=f"Scaffolded: {p}")

            elif action == "run":
                if path:
                    return _shell.run(command=f"python {path}", confirm=True)
                elif code:
                    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
                        f.write(code)
                        tmp = f.name
                    result = _shell.run(command=f"python {tmp}", confirm=True)
                    Path(tmp).unlink(missing_ok=True)
                    return result
                return ToolResult(success=False, output="", error="Provide 'path' or 'code' to run.")

            elif action == "lint":
                target = path or "."
                return _shell.run(command=f"ruff check {target}", confirm=True)

            elif action == "format":
                target = path or "."
                return _shell.run(command=f"ruff format {target}", confirm=True)

            elif action == "read":
                p = Path(path).expanduser()
                if not p.exists():
                    return ToolResult(success=False, output="", error=f"File not found: {path}")
                return ToolResult(success=True, output=p.read_text())

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            log.error(f"code_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
