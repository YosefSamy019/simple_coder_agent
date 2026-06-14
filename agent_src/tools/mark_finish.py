import streamlit as st

from agent_src.models.models import AgentStatus
from agent_src.tools.tools import AgentTool
from agent_src.values.const import AGENT_STATUS


class MarkFinishTool(AgentTool):
    def get_name(self) -> str:
        return "deliver_task"

    def get_description(self) -> str:
        return """
Call this tool exactly once when the task has been completed.

Use this tool only when:
- all requested files have been created or modified,
- any required commands have been executed,
- no additional tool calls are needed.

Calling this tool signals that the agent should terminate.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": (
                        "Brief summary of what was accomplished."
                    ),
                    "default": "",
                }
            },
        }

    def execute(self, parameters: dict) -> dict:
        summary = parameters.get("summary", "")

        try:
            previous_status = st.session_state.get(
                AGENT_STATUS,
                None,
            )

            st.session_state[
                AGENT_STATUS
            ] = AgentStatus.STOPPED

            return {
                "success": True,
                "task_delivered": True,
                "previous_status": (
                    str(previous_status)
                    if previous_status is not None
                    else None
                ),
                "current_status": str(
                    AgentStatus.STOPPED
                ),
                "summary": summary,
            }

        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "message": str(e),
            }