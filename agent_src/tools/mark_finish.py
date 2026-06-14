import os.path
import streamlit as st

from agent_src.values.const import AGENT_STATUS
from agent_src.models.models import AgentStatus
from agent_src.tools.tools import AgentTool


class MarkFinishTool(AgentTool):
    def get_name(self) -> str:
        return "deliver_task"

    def get_description(self) -> str:
        return "Must be called when task is done"

    def get_parameters(self) -> dict:
        return None

    def execute(self, parameters: dict) -> str:

        try:
            st.session_state[AGENT_STATUS] = AgentStatus.STOPPED
            return "Task is delivered successfully"

        except Exception as e:
            return f"Error: {e}"
