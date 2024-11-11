# flash_tool_plugins/pythor.py
from flash_tool_plugins import FlashToolPlugin


class PyThor(FlashToolPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.name = "pythor"
        self.displayed_name = "PyThor (in development)"
        self.prompt = ">> "
        self.tabs = ["Log", "Options", "Files"]
        self.buttons = [
            {
                "name": "help_button",
                "text": "Help",
                "command": lambda _: main.send_cmd("help"),
            },
            {
                "name": "connect_button",
                "text": "Connect",
                "command": lambda _: main.connect_device(),
            },
            {
                "name": "start_odin_button",
                "text": "Start Session",
                "command": lambda _: main.start_odin_session(),
            },
        ]
        self.options_list = None
        self.strings_to_commands = {
            ">>": [lambda: main.set_widget_state(main.connect_button, state=True)]
        }

    def test(self):
        print(f"This is a test of the {self.name} plugin.")

    def initialise_buttons(self, main):
        main.set_widget_state(main.connect_button, state=False)

    def flash(self, main):
        print("PyThor has no working flash function.")

    def select_device(self, main, function=None):
        print("PyThor has no working select_device function.")

    def select_partitions(self, main, files, base_dir, auto):
        print("PyThor has no working select_partitions function.")
