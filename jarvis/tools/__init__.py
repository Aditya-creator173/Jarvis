from jarvis.tools.fs_tool import FsTool
from jarvis.tools.shell_tool import ShellTool
from jarvis.tools.code_tool import CodeTool
from jarvis.tools.memory_tool import MemoryTool
from jarvis.tools.task_tool import TaskTool
from jarvis.tools.search_tool import SearchTool
from jarvis.tools.web_tool import WebTool

TOOL_REGISTRY = {
    t.name: t for t in [
        FsTool(), ShellTool(), CodeTool(), MemoryTool(),
        TaskTool(), SearchTool(), WebTool()
    ]
}

def get_tool(name: str):
    return TOOL_REGISTRY.get(name)

def list_tools() -> str:
    return "\n".join(f"- {name}: {t.description}" for name, t in TOOL_REGISTRY.items())
