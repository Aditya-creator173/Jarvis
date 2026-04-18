from __future__ import annotations
import time
import json
from jarvis.tools.base import BaseTool, ToolResult
import jarvis.memory as mem
from jarvis.logger import get_logger

log = get_logger(__name__)


class TaskTool(BaseTool):
    name = "task"
    description = "Create, list, update, complete and delete tasks stored in SQLite."
    works_offline = True

    def run(self, action: str, title: str = None, task_id: int = None,
            description: str = None, priority: str = "medium",
            due_date: str = None, tags: str = None, status: str = None) -> ToolResult:
        try:
            conn = mem.get_conn()
            now = time.time()

            if action == "create":
                if not title:
                    return ToolResult(success=False, output="", error="'title' is required.")
                conn.execute(
                    "INSERT INTO tasks (created_ts,updated_ts,title,description,status,priority,due_date,tags) VALUES (?,?,?,?,?,?,?,?)",
                    (now, now, title, description, "todo", priority, due_date, tags)
                )
                conn.commit()
                return ToolResult(success=True, output=f"Task created: {title}")

            elif action == "list":
                rows = conn.execute(
                    "SELECT id,title,status,priority,due_date FROM tasks ORDER BY created_ts DESC"
                ).fetchall()
                if not rows:
                    return ToolResult(success=True, output="No tasks found.")
                lines = [f"[{r['id']}] {r['status'].upper()} | {r['priority']} | {r['title']} | due:{r['due_date'] or 'none'}" for r in rows]
                return ToolResult(success=True, output="\\n".join(lines))

            elif action == "done":
                conn.execute("UPDATE tasks SET status='done', updated_ts=? WHERE id=?", (now, task_id))
                conn.commit()
                return ToolResult(success=True, output=f"Task {task_id} marked done.")

            elif action == "delete":
                conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn.commit()
                return ToolResult(success=True, output=f"Task {task_id} deleted.")

            elif action == "update":
                fields, vals = [], []
                if title:     fields.append("title=?");       vals.append(title)
                if status:    fields.append("status=?");      vals.append(status)
                if priority:  fields.append("priority=?");    vals.append(priority)
                if due_date:  fields.append("due_date=?");    vals.append(due_date)
                if not fields:
                    return ToolResult(success=False, output="", error="No fields to update.")
                fields.append("updated_ts=?"); vals.append(now)
                vals.append(task_id)
                conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", vals)
                conn.commit()
                return ToolResult(success=True, output=f"Task {task_id} updated.")

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            log.error(f"task_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
