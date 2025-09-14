import requests

from ..monitoring import LoggedComponent
from .action_menu import Binding


class Controller(LoggedComponent):
    """Can control any prompt that uses --listen option including the one it's attached to"""

    def execute(self, port: int, binding: Binding):
        """Executes a binding"""
        try:
            response = requests.post(f"http://localhost:{port}", data=binding.action_string())
            if message := response.text:
                if not message.startswith("unknown action:"):
                    self.logger.log("WEIRDNESS", message)
                raise RuntimeError(message)
        except Exception as e:
            self.logger.exception(str(e), trace_point="error_executing_binding")
