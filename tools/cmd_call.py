import json
import subprocess
import streamlit as st
from tools.tools import AgentTool


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
                    "description": "Directory to run the command in",
                },
            },
            "required": ["command"],
        }

    def execute(self, parameters: dict) -> str:
        command: str | None = parameters.get("command")
        working_dir: str | None = parameters.get("working_dir")

        if not command:
            return "Error: `command` must be provided."

        if not working_dir:
            return "Error: `working_dir` must be provided."

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

            return json.dumps(
                {
                    "output": output,
                    "exit_code": error_code,
                }
            )

        except Exception as e:
            return f"Error happened: {e}"
