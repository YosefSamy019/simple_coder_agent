import os.path

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
            os.makedirs(super().WORKING_DIR, exist_ok=True)
            items = os.listdir(super().WORKING_DIR)

            if not items:
                return f"Directory is empty."

            result = f"Contents of directory:\n"
            for root, _, files in os.walk(super().WORKING_DIR):
                for file in files:
                    result = result + f"- {os.path.join(root, file)}\n"

            return result.strip()

        except Exception as e:
            return f"Error: {e}"
