import os.path
import streamlit as st

from src.values.const import FILES_SYSTEM
from src.tools.tools import AgentTool


class CreateFileTool(AgentTool):
    def get_name(self) -> str:
        return "create_file"

    def get_description(self) -> str:
        return "Create a new file with the provided content or replace an existing one."

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to create.",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write into the file.",
                },
            },
            "required": ["filename", "content"],
        }

    def execute(self, parameters: dict) -> str:
        filename: str | None = parameters.get("filename")
        content: str | None = parameters.get("content")

        if filename is None:
            return "Error: field `filename` must be provided."

        if content is None:
            return "Error: field `content` must be provided."

        try:
            total_path = filename

            # Create parent directories if necessary
            parent_dir = os.path.dirname(total_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # if os.path.exists(total_path):
            #     return f"File {filename} already exists."

            with open(total_path, "w", encoding="utf-8") as f:
                f.write(content)

            st.session_state[FILES_SYSTEM].append(total_path)
            st.session_state[FILES_SYSTEM] = list(set(st.session_state[FILES_SYSTEM]))


            return f"File {filename} successfully created."

        except Exception as e:
            return f"An error occurred while creating {filename}: {e}"
