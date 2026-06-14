from abc import ABC, abstractmethod
from typing import List, Dict
import streamlit as st

from const import AGENT_STATUS
from models import AgentStatus


class AgentTool(ABC):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_parameters(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def execute(self, parameters: dict) -> str:
        raise NotImplementedError


def get_all_tools_list():
    tools_child = [x() for x in AgentTool.__subclasses__()]

    tools = [
        {
            "type": "function",
            "function": {
                "name": t.get_name(),
                "description": t.get_description(),
                "parameters": t.get_parameters(),
            }
        }
        for t in tools_child
    ]

    return tools
