import os
import subprocess

import streamlit as st

from agent_src.tools.tools import AgentTool
from agent_src.values.const import FILES_SYSTEM


class RunCommandTool(AgentTool):
    def get_name(self) -> str:
        return "run_command"

    def get_description(self) -> str:
        return """
Run a shell command and return its result.

Recommended workflow:
1. Create/Edit files.
2. Run the command.
3. Inspect the output.
4. Fix errors if needed.

Returns structured results for easier agent recovery.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute.",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory.",
                    "default": ".",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds.",
                    "default": 30,
                },
            },
            "required": ["command"],
        }

    def execute(self, parameters: dict) -> dict:
        command = parameters.get("command")
        working_dir = parameters.get("working_dir", ".")
        timeout = parameters.get("timeout", 30)

        if not command:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "command",
                "message": "command is required",
            }

        if not os.path.isdir(working_dir):
            return {
                "success": False,
                "error": "working_directory_not_found",
                "working_dir": working_dir,
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            stdout = result.stdout or ""
            stderr = result.stderr or ""

            MAX_OUTPUT = 4000

            clipped = False

            if len(stdout) > MAX_OUTPUT:
                stdout = (
                    stdout[:2000]
                    + "\n\n... OUTPUT CLIPPED ...\n\n"
                    + stdout[-2000:]
                )
                clipped = True

            if len(stderr) > MAX_OUTPUT:
                stderr = (
                    stderr[:2000]
                    + "\n\n... ERROR CLIPPED ...\n\n"
                    + stderr[-2000:]
                )
                clipped = True

            try:
                items = st.session_state.get(FILES_SYSTEM, [])
                items = [
                    item
                    for item in items
                    if os.path.exists(item)
                ]
                st.session_state[FILES_SYSTEM] = items
            except Exception:
                pass

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "command": command,
                "working_dir": working_dir,
                "stdout": stdout,
                "stderr": stderr,
                "output_clipped": clipped,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "command": command,
                "timeout": timeout,
            }

        except PermissionError:
            return {
                "success": False,
                "error": "permission_denied",
                "command": command,
            }

        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "command": command,
                "message": str(e),
            }