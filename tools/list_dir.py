import os.path
import streamlit as st

from const import FILES_SYSTEM
from tools.tools import AgentTool


class ListDirTool(AgentTool):
    def get_name(self) -> str:
        return "list_directory"

    def get_description(self) -> str:
        return "List the contents of the directory."

    def get_parameters(self) -> dict:
        return None

    def execute(self, parameters: dict) -> str:

        try:
            items = st.session_state[FILES_SYSTEM]

            if not items:
                return f"Directory is empty."

            result = f"Contents of directory:\n"

            result += '\n'.join([f"- " + x for x in items])

            return result.strip()

        except Exception as e:
            return f"Error: {e}"
