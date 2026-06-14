import os
from agent_src.tools.tools import AgentTool


class EditFileTool(AgentTool):
    def get_name(self) -> str:
        return "edit_file"

    def get_description(self) -> str:
        return """
Edit a file by replacing EXACTLY ONE occurrence of old_text with new_text.

Recommended workflow:
1. Read the file first.
2. Copy the target text exactly.
3. Call edit_file.

The tool will fail if:
- the file does not exist,
- the text is not found,
- multiple matches are found.
"""

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Path of the file to edit.",
                },
                "find_str": {
                    "type": "string",
                    "description": "Exact text to replace.",
                },
                "replace_str": {
                    "type": "string",
                    "description": "Replacement text.",
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences. Defaults to false.",
                    "default": False,
                },
            },
            "required": [
                "filename",
                "find_str",
                "replace_str",
            ],
        }

    def execute(self, parameters: dict) -> dict:
        filename = parameters.get("filename")
        find_str = parameters.get("find_str")
        replace_str = parameters.get("replace_str")
        replace_all = parameters.get("replace_all", False)

        # ------------------------
        # Parameter validation
        # ------------------------

        if not filename:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "filename",
                "message": "filename is required",
            }

        if find_str is None:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "find_str",
                "message": "find_str is required",
            }

        if replace_str is None:
            return {
                "success": False,
                "error": "missing_required_field",
                "field": "replace_str",
                "message": "replace_str is required",
            }

        # ------------------------
        # File validation
        # ------------------------

        if not os.path.isfile(filename):
            return {
                "success": False,
                "error": "file_not_found",
                "filename": filename,
            }

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            matches = content.count(find_str)

            if matches == 0:
                return {
                    "success": False,
                    "error": "text_not_found",
                    "filename": filename,
                    "matches": 0,
                    "hint": "Read the file and copy the text exactly.",
                }

            if matches > 1 and not replace_all:
                return {
                    "success": False,
                    "error": "ambiguous_match",
                    "filename": filename,
                    "matches": matches,
                    "hint": (
                        "The target text appears multiple times. "
                        "Provide a larger unique context or set "
                        "replace_all=True."
                    ),
                }

            if replace_all:
                new_content = content.replace(find_str, replace_str)
                edits = matches
            else:
                new_content = content.replace(
                    find_str,
                    replace_str,
                    1,
                )
                edits = 1

            with open(filename, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "success": True,
                "filename": filename,
                "matches_found": matches,
                "replacements_made": edits,
                "replace_all": replace_all,
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "encoding_error",
                "filename": filename,
                "message": "Could not decode file as UTF-8.",
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