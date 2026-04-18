from __future__ import annotations
import subprocess
import shlex
from jarvis.tools.base import BaseTool, ToolResult
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
ALLOWLIST = CFG["execution"]["command_allowlist"]
WORKSPACE = CFG["execution"]["workspace"]


def _is_allowed(cmd: str) -> bool:
    first_word = shlex.split(cmd)[0] if cmd.strip() else ""
    return any(first_word == allowed or first_word.endswith(f"/{allowed}") for allowed in ALLOWLIST)


class ShellTool(BaseTool):
    name = "shell"
    description = "Execute a shell command. Captures stdout and stderr. Dangerous commands require confirm=True."
    requires_confirm = False
    works_offline = True

    def run(self, command: str, cwd: str = None, confirm: bool = False,
            timeout: int = 30) -> ToolResult:
        try:
            is_safe = _is_allowed(command)
            needs_confirm = CFG["execution"]["require_confirm_destructive"] and not is_safe

            if needs_confirm and not confirm:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command '{command}' is not in the allowlist and requires confirm=True to execute."
                )

            working_dir = cwd or WORKSPACE
            log.info(f"Executing shell: {command} (cwd={working_dir})")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=timeout
            )

            combined = ""
            if result.stdout:
                combined += result.stdout
            if result.stderr:
                combined += f"\\n[stderr]\\n{result.stderr}"

            success = result.returncode == 0
            log.info(f"Shell exit code: {result.returncode}")

            return ToolResult(
                success=success,
                output=combined.strip(),
                error=None if success else f"Exit code {result.returncode}",
                metadata={"returncode": result.returncode, "command": command}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output="", error=f"Command timed out after {timeout}s")
        except Exception as e:
            log.error(f"shell_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
