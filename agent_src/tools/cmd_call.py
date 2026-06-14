import json
import os
import subprocess

from agent_src.values.const import FILES_SYSTEM
from agent_src.tools.tools import AgentTool
import streamlit as st


class RunCommandTool(AgentTool):
    def get_name(self) -> str:
        return "run_command"

    def get_description(self) -> str:
        return "Run a shell command in a working directory and return its output."

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Directory to run the command in (defaults to '.')",
                    "default": ".",
                },
            },
            "required": ["command"],
        }

    def execute(self, parameters: dict) -> str:
        command: str | None = parameters.get("command")
        working_dir: str = parameters.get("working_dir") or "."

        if not command:
            return "Error: `command` must be provided."

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=working_dir,
            )

            output, _ = process.communicate()
            error_code = process.returncode

            # Clip long output
            if output and len(output) > 2000:
                output = (
                        output[:1000]
                        + "\n\n[...content clipped...]\n\n"
                        + output[-1000:]
                )

            # filter files
            items = st.session_state[FILES_SYSTEM]
            items = list(filter(lambda item: os.path.exists(item), items))
            st.session_state[FILES_SYSTEM] = items

            return f"""
Exit_Code: {error_code}
Output: {output}
            """.strip()

        except Exception as e:
            return f"Error happened: {e}"
