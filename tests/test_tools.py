import pytest
from pathlib import Path
import tempfile

def test_fs_tool_write_and_read():
    from jarvis.tools.fs_tool import FsTool
    tool = FsTool()
    with tempfile.TemporaryDirectory() as d:
        p = str(Path(d) / "test.txt")
        r = tool.run(action="write", path=p, content="hello jarvis")
        assert r.success
        r2 = tool.run(action="read", path=p)
        assert r2.success
        assert "hello jarvis" in r2.output

def test_shell_tool_safe_command():
    from jarvis.tools.shell_tool import ShellTool
    tool = ShellTool()
    r = tool.run(command="echo hello", confirm=True)
    assert r.success
    assert "hello" in r.output

def test_shell_tool_unsafe_blocked():
    from jarvis.tools.shell_tool import ShellTool
    tool = ShellTool()
    r = tool.run(command="rm -rf /tmp/fakefile", confirm=False)
    assert not r.success

def test_memory_tool_store_recall():
    from jarvis.tools.memory_tool import MemoryTool
    import jarvis.memory as mem
    mem.init_db()
    tool = MemoryTool()
    r = tool.run(action="store", fact="The project workspace is at ~/projects/jarvis")
    assert r.success
    r2 = tool.run(action="recall", query="where is the project")
    assert r2.success
