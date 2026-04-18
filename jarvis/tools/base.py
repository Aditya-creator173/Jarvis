from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __str__(self):
        if self.success:
            return self.output
        return f"[ERROR] {self.error}\nOutput: {self.output}"


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    requires_confirm: bool = False
    works_offline: bool = True

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        """Execute the tool. Must never raise — catch all exceptions and return ToolResult(success=False)."""
        pass

    def schema(self) -> dict:
        """Returns JSON schema for the LLM to understand this tool's parameters."""
        return {
            "name": self.name,
            "description": self.description,
            "requires_confirm": self.requires_confirm,
            "works_offline": self.works_offline,
        }
