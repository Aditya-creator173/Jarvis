from __future__ import annotations
import httpx
from jarvis.tools.base import BaseTool, ToolResult
from jarvis.logger import get_logger

log = get_logger(__name__)


class WebTool(BaseTool):
    name = "web"
    description = "Fetch a URL or search the web. ONLY use when user explicitly requests online access."
    works_offline = False
    requires_confirm = True

    def run(self, action: str, url: str = None, query: str = None) -> ToolResult:
        try:
            if action == "fetch":
                resp = httpx.get(url, timeout=15, follow_redirects=True)
                resp.raise_for_status()
                # Strip HTML tags naively
                import re
                text = re.sub(r"<[^>]+>", " ", resp.text)
                text = re.sub(r"\s+", " ", text).strip()
                return ToolResult(success=True, output=text[:4000])

            elif action == "search":
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                lines = [f"{r['title']}\\n{r['href']}\\n{r['body']}" for r in results]
                return ToolResult(success=True, output="\\n\\n".join(lines))

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            log.error(f"web_tool error: {e}")
            return ToolResult(success=False, output="", error=str(e))
