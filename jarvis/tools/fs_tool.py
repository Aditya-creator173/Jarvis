from __future__ import annotations
import shutil
from pathlib import Path
from jarvis.tools.base import BaseTool, ToolResult
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
WORKSPACE = Path(CFG["execution"]["workspace"])


def _safe_path(p: str) -> Path:
    return Path(p).expanduser()


class FsTool(BaseTool):
    name = "fs"
    description = "Read, write, list, copy, move, delete files and directories."
    works_offline = True

    def run(self, action: str, path: str, content: str = None,
            destination: str = None, confirm: bool = False) -> ToolResult:
        try:
            target = _safe_path(path)
            is_destructive = action in ("delete", "move", "overwrite")

            if is_destructive and CFG["execution"]["require_confirm_destructive"] and not confirm:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Action '{action}' on '{path}' is destructive and requires confirm=True."
                )

            if action == "read":
                if not target.exists():
                    return ToolResult(success=False, output="", error=f"File not found: {path}")
                text = target.read_text(encoding="utf-8", errors="replace")
                return ToolResult(success=True, output=text)

            elif action == "write":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content or "", encoding="utf-8")
                log.info(f"Wrote file: {target}")
                return ToolResult(success=True, output=f"Written: {target}")

            elif action == "overwrite":
                target.write_text(content or "", encoding="utf-8")
                return ToolResult(success=True, output=f"Overwritten: {target}")

            elif action == "list":
                if not target.exists():
                    return ToolResult(success=False, output="", error=f"Path not found: {path}")
                if target.is_file():
                    return ToolResult(success=True, output=str(target))
                entries = sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name))
                lines = [f"{'D' if e.is_dir() else 'F'}  {e.name}" for e in entries]
                return ToolResult(success=True, output="\\n".join(lines))

            elif action == "delete":
                if not target.exists():
                    return ToolResult(success=False, output="", error=f"Not found: {path}")
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                log.info(f"Deleted: {target}")
                return ToolResult(success=True, output=f"Deleted: {target}")

            elif action == "move":
                dest = _safe_path(destination)
                shutil.move(str(target), str(dest))
                log.info(f"Moved: {target} -> {dest}")
                return ToolResult(success=True, output=f"Moved {target} to {dest}")

            elif action == "copy":
                dest = _safe_path(destination)
                if target.is_dir():
                    shutil.copytree(str(target), str(dest))
                else:
                    shutil.copy2(str(target), str(dest))
                return ToolResult(success=True, output=f"Copied {target} to {dest}")

            elif action == "mkdir":
                target.mkdir(parents=True, exist_ok=True)
                return ToolResult(success=True, output=f"Created directory: {target}")

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            log.error(f"fs_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
