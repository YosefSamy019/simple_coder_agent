import os
import streamlit as st

from agent_src.tools.tools import AgentTool
from agent_src.values.const import FILES_SYSTEM


class ListDirTool(AgentTool):
    def get_name(self) -> str:
        return "list_directory"

    def get_description(self) -> str:
        return """
List files currently tracked by the agent.

Useful for:
- checking project structure,
- finding created files,
- verifying file existence.

Returns structured data.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
        }

    def execute(self, parameters: dict) -> dict:
        try:
            files = st.session_state.get(
                FILES_SYSTEM,
                []
            )

            # Remove stale entries
            files = [
                f
                for f in files
                if os.path.exists(f)
            ]

            files = sorted(set(files))

            st.session_state[FILES_SYSTEM] = files

            return {
                "success": True,
                "count": len(files),
                "files": files,
            }

        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "message": str(e),
            }