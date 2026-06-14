import os
import streamlit as st

from agent_src.tools.tools import AgentTool
from agent_src.values.const import FILES_SYSTEM


class CreateFileTool(AgentTool):
    def get_name(self) -> str:
        return "create_file"

    def get_description(self) -> str:
        return """
Create or overwrite a file.

The tool:
- creates parent directories if needed,
- writes UTF-8 text,
- overwrites existing files,
- tracks created files.

Returns structured results for agent recovery.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Path of the file to create.",
                },
                "content": {
                    "type": "string",
                    "description": "UTF-8 text to write.",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing file.",
                    "default": True,
                },
            },
            "required": [
                "filename",
                "content",
            ],
        }

    def execute(self, parameters: dict) -> dict:
        filename = parameters.get("filename")
        content = parameters.get("content")
        overwrite = parameters.get("overwrite", True)

        # --------------------
        # Validation
        # --------------------

        if not filename:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "filename",
                "message": "filename is required",
            }

        if content is None:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "content",
                "message": "content is required",
            }

        try:
            total_path = filename

            parent = os.path.dirname(total_path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            existed = os.path.exists(total_path)

            if existed and not overwrite:
                return {
                    "success": False,
                    "error": "file_exists",
                    "filename": total_path,
                }

            with open(
                total_path,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(content)

            try:
                files = st.session_state.get(
                    FILES_SYSTEM,
                    []
                )

                if total_path not in files:
                    files.append(total_path)

                st.session_state[FILES_SYSTEM] = files

            except Exception:
                pass

            return {
                "success": True,
                "filename": total_path,
                "created": not existed,
                "overwritten": existed,
                "bytes_written": len(
                    content.encode("utf-8")
                ),
                "characters_written": len(content),
            }

        except PermissionError:
            return {
                "success": False,
                "error": "permission_denied",
                "filename": filename,
            }

        except UnicodeEncodeError:
            return {
                "success": False,
                "error": "encoding_error",
                "filename": filename,
            }

        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "filename": filename,
                "message": str(e),
            }