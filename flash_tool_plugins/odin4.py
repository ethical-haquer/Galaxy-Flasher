# flash_tool_plugins/odin4.py
from flash_tool_plugins import FlashToolPlugin
import os


class Odin4(FlashToolPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.name = "odin4"
        self.displayed_name = "Odin4"
        self.prompt = ">> "
        self.tabs = ["Log", "Files"]
        self.buttons = [
            {
                "name": "flash_button",
                "text": "Flash!",
                "command": lambda _: main.flash(),
            },
        ]
        self.options_list = None
        self.strings_to_commands = {
            "Welcome to Interactive Odin4!": [
                lambda: main.set_widget_state(
                    main.flash_button,
                    state=True,
                )
            ]
        }

    def test(self):
        print(f"This is a test of the {self.name} plugin.")

    def initialise_buttons(self, main):
        main.set_widget_state(main.flash_button, state=False)

    def flash(self, main):
        args = []
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            slot_to_arg = {
                "BL": "-b",
                "AP": "-a",
                "CP": "-c",
                "CSC": "-s",
                "USERDATA": "-u",
            }
            entry = getattr(main, f"{slot}_entry")
            file = entry.get_text()
            if file:
                arg = slot_to_arg[slot]
                file_arg = f"{arg} {file}"
                args.append(file_arg)
        if len(args) == 0:
            print(main.strings["no_files_selected2"])
            main.create_alert_dialog(
                "Invalid files", main.strings["no_files_selected2"]
            )
        else:

            def run_flash_command(device):
                if not device:
                    message = "No devices were found - First connect a device that's in Download Mode"
                    print(message)
                    main.create_alert_dialog(
                        "No devices were found",
                        "First connect a device that's in Download Mode",
                    )
                else:
                    args.insert(0, f"-d {device}")
                    command = " ".join(["flash"] + args)
                    print(f"Running: {command}")
                    main.send_cmd(command)

            self.select_device(main, "odin4", run_flash_command)

    def select_device(self, main, function=None):
        def set_selected_device(btn, device):
            if btn.get_active:
                main.device = device

        def send_selected_device(cancel=False):
            if not cancel:
                if not main.device:
                    function(None)
                else:
                    print(f"Selected device: {main.device}")
                    function(main.device)

        def callback(dialog, result):
            response_id = dialog.choose_finish(result)
            if response_id == "ok":
                send_selected_device()
            elif response_id == "cancel":
                send_selected_device(cancel=True)

        def clean_devices(devices):
            """Returns a cleaned version of the given list of devices,
            to ensure that they all start with '> '.

            Adds a ' ' between each part of the device, if it was on multiple lines.
            This may or may not be necessary, depending on the specific case.

            Args:
                devices (list): A list of devices, which may or may not each be on one line.

            Returns:
                list: A cleaned list of devices, where each device is on one line.
            """
            cleaned_devices = []
            ongoing_device = ""

            for device in devices:
                if device.startswith("> "):
                    if ongoing_device:
                        cleaned_devices.append(ongoing_device.strip())
                    ongoing_device = device
                else:
                    ongoing_device += " " + device

            if ongoing_device:
                cleaned_devices.append(ongoing_device.strip())

            return cleaned_devices

        def display_devices():
            box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
            grid = Gtk.Grid()
            box.append(grid)
            group = None
            row = 1

            for i, device in enumerate(devices):
                checkbutton = main.create_checkbutton(device, 0, row, grid)
                if i == 0:
                    group = checkbutton
                    checkbutton.set_active(True)
                else:
                    checkbutton.set_group(group)
                checkbutton.connect("toggled", set_selected_device, device)
                row = row + 1

            responses = [
                {"id": "cancel", "label": "Cancel", "appearance": "0"},
                {"id": "ok", "label": "OK", "appearance": "0"},
            ]
            main.create_alert_dialog(
                main.strings["choose_a_device"], "", responses, callback, "ok", box
            )

        if not function:
            print(
                "The function arg must be passed to select_device if the flashtool is odin4."
            )
        else:
            devices = main.get_output("list")
            # TODO: I haven't actually tested this with two devices connected.
            # devices = ["/dev/bus/usb/device1", "/dev/bus/usb/device2"]
            if not devices[0] or devices[0] == "Timeout":
                function(None)
            else:
                if len(devices) == 1:
                    function(devices[0])
                else:
                    main.device = devices[0]
                    display_devices()

    def select_partitions(self, main, files, base_dir, auto):
        print("Odin4 has no working select_partitions function.")
