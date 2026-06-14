import os

from agent_src.tools.tools import AgentTool


class ReadFileContentTool(AgentTool):
    def get_name(self) -> str:
        return "read_file_content"

    def get_description(self) -> str:
        return """
Read a UTF-8 text file.

Useful for:
- inspecting code,
- verifying edits,
- debugging.

Large files are automatically clipped.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "File to read.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "1-based starting line.",
                    "default": 1,
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum number of lines.",
                    "default": 200,
                },
            },
            "required": [
                "filename",
            ],
        }

    def execute(self, parameters: dict) -> dict:
        filename = parameters.get("filename")
        start_line = parameters.get("start_line", 1)
        max_lines = parameters.get("max_lines", 200)

        if not filename:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "filename",
            }

        if not os.path.isfile(filename):
            return {
                "success": False,
                "error": "file_not_found",
                "filename": filename,
            }

        if start_line < 1:
            start_line = 1

        if max_lines < 1:
            max_lines = 1

        try:
            with open(
                filename,
                "r",
                encoding="utf-8",
            ) as f:
                lines = f.readlines()

            total_lines = len(lines)

            begin = start_line - 1
            end = min(begin + max_lines, total_lines)

            selected = []

            for i in range(begin, end):
                selected.append(
                    f"{i+1:4d}: {lines[i].rstrip()}"
                )

            return {
                "success": True,
                "filename": filename,
                "total_lines": total_lines,
                "returned_lines": end - begin,
                "start_line": start_line,
                "end_line": end,
                "has_more": end < total_lines,
                "content": "\n".join(selected),
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "encoding_error",
                "filename": filename,
                "message": "File is not valid UTF-8.",
            }

        except PermissionError:
            return {
                "success": False,
                "error": "permission_denied",
                "filename": filename,
            }

        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "filename": filename,
                "message": str(e),
            }