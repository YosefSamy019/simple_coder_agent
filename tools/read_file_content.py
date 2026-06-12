import os.path

from tools.tools import AgentTool


class ReadFileContentTool(AgentTool):
    def get_name(self) -> str:
        return "read_file_content"

    def get_description(self) -> str:
        return "Read and return the full content of a file."

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to read",
                },
            },
            "required": ["filename"],
        }

    def execute(self, parameters: dict) -> str:
        filename: str | None = parameters.get("filename")

        if filename is None:
            return "Error: field `filename` must be provided."

        try:
            total_path = os.path.join(super().WORKING_DIR, filename)

            with open(total_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            return file_content

        except FileNotFoundError:
            return f"File {filename} not found."

        except Exception as e:
            return f"An error occurred while reading {filename}: {e}"
