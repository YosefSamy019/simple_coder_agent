import os.path

from agent_src.tools.tools import AgentTool


class EditFileTool(AgentTool):
    def get_name(self) -> str:
        return "edit_file"

    def get_description(self) -> str:
        return "Apply a diff to a file by replacing occurrences of find_str with replace_str."

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to modify.",
                },
                "find_str": {
                    "type": "string",
                    "description": "The string to find in the file.",
                },
                "replace_str": {
                    "type": "string",
                    "description": "The string to replace with.",
                },
            },
            "required": ["filename", "find_str", "replace_str"],
        }

    def execute(self, parameters: dict) -> str:
        filename: str | None = parameters.get("filename")
        find_str: str | None = parameters.get("find_str")
        replace_str: str | None = parameters.get("replace_str")

        if filename is None:
            return "Error: field `filename` must be provided."

        if find_str is None:
            return "Error: field `find_str` must be provided."

        if replace_str is None:
            return "Error: field `replace_str` must be provided."

        try:
            total_path = filename

            with open(total_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            if find_str in file_content:
                new_content = file_content.replace(find_str, replace_str)

                with open(total_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                return f"File {filename} successfully edited."
            else:
                return f"'''{find_str}''' not found in {filename}."

        except FileNotFoundError:
            return f"File {filename} not found."

        except Exception as e:
            return f"An error occurred while editing {filename}: {e}"
