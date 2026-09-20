from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolCallRecord:
    step: int
    tool: str
    arguments: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"step": self.step, "tool": self.tool, "arguments": self.arguments}


@dataclass
class ToolResultRecord:
    step: int
    tool: str
    result: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"step": self.step, "tool": self.tool, "result": self.result}


@dataclass
class AgentState:
    user_query: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    tool_results: List[ToolResultRecord] = field(default_factory=list)
    final_response: Optional[str] = None
    status: str = "running"
    error: Optional[str] = None

    def add_tool_call(self, step: int, tool: str, arguments: Dict[str, Any]) -> None:
        self.tool_calls.append(ToolCallRecord(step=step, tool=tool, arguments=arguments))

    def add_tool_result(self, step: int, tool: str, result: Dict[str, Any]) -> None:
        self.tool_results.append(ToolResultRecord(step=step, tool=tool, result=result))

    def finish(self, response: str) -> None:
        self.final_response = response
        self.status = "completed"

    def fail(self, error: str) -> None:
        self.error = error
        self.status = "failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_query": self.user_query,
            "current_step": self.current_step,
            "tool_calls": [c.to_dict() for c in self.tool_calls],
            "tool_results": [r.to_dict() for r in self.tool_results],
            "final_response": self.final_response,
            "status": self.status,
            "error": self.error,
        }