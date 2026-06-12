from abc import ABC, abstractmethod
from enum import Enum


class AgentStatus(Enum):
    RUNNING = 'running'
    STOPPED = 'stopped'


class ChatMsg(ABC):

    @abstractmethod
    def to_json(self) -> dict:
        raise NotImplementedError


class UserChatMsg(ChatMsg):
    def __init__(self, content: str):
        self.content = content

    def to_json(self) -> dict:
        return {"role": 'user', "content": self.content}


class AssistantChatMsg(ChatMsg):
    def __init__(self, content: str, tool_calls: list):
        self.content = content
        tool_calls = tool_calls if tool_calls else []
        self.tool_calls = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in tool_calls
        ]

    def to_json(self) -> dict:
        return {"role": 'assistant', "content": self.content}
        return {"role": 'assistant', "content": self.content, "tool_calls": self.tool_calls}


class SystemChatMsg(ChatMsg):
    def __init__(self, content: str):
        self.content = content

    def to_json(self) -> dict:
        return {"role": 'system', "content": self.content}


class ToolCallChatMsg(ChatMsg):
    def __init__(self, tool_call_id, function_name: str, function_arguments: dict, result: str):
        self.function_name = function_name
        self.tool_call_id = tool_call_id
        self.function_arguments = function_arguments
        self.result = result

    def to_json(self) -> dict:
        return {
            "role": 'tool',
            "content": self.result,
            "name": self.function_name,
            "tool_call_id": self.tool_call_id
        }
