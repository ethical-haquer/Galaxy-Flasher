# flash_tool_plugins/thor.py
from flash_tool_plugins import FlashToolPlugin
import os


class Thor(FlashToolPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.glib = main.glib
        self.time = main.time
        self.shared_utils = main.shared_utils
        self.gtk = main.gtk
        self.re = main.re
        self.name = "thor"
        self.displayed_name = "Thor"
        self.prompt = "shell> "
        self.tabs = ["Log", "Options", "Files"]
        self.buttons = [
            {
                "name": "connect_button",
                "text": main.strings["connect"],
                "command": lambda _: self.select_device(main),
            },
            {
                "name": "start_odin_button",
                "text": main.strings["start_odin_protocol"],
                "command": lambda _: main.start_odin_session(),
            },
            {
                "name": "flash_button",
                "text": "Flash!",
                "command": lambda _: self.flash(main),
            },
        ]
        self.options_list = None
        """
        [
            {
                "title": None,
                "section_sensitive": False,
                "section_function": main.burner,
                "section_commands": [
                    (main.connect_option_switch, ["$switch_row"]),
                ],
                "rows": [
                    {
                        "type": "switch",
                        "title": "T Flash",
                        "subtitle": "Writes the boot-loader of the device to the SD card.",
                        "setting": "t_flash",
                        "default_value": False,
                    },
                    {
                        "type": "switch",
                        "title": "EFS Clear",
                        "subtitle": "Wipes phone/network-related stuff from the device.",
                        "setting": "efs_clear",
                        "default_value": False,
                    },
                    {
                        "type": "switch",
                        "title": "Bootloader Update",
                        "setting": "bootloader_update",
                        "default_value": False,
                    },
                    {
                        "type": "switch",
                        "title": "Reset Flash Count",
                        "setting": "reset_flash_count",
                        "default_value": False,
                    },
                ],
            }
        ]
        """
        self.strings_to_commands = {
            "Welcome to Thor Shell": [
                lambda: main.set_widget_state(main.connect_button, state=True),
            ],
            "Successfully connected to the device!": [
                lambda: print("Successfully connected to the device!"),
                lambda: main.set_widget_state(main.start_odin_button, state=True),
                lambda: main.connect_button.set_label("Disconnect"),
                lambda: main.change_button_command(
                    main.connect_button, lambda _: main.send_cmd("disconnect")
                ),
            ],
            "Successfully disconnected the device!": [
                lambda: print("Successfully disconnected the device!"),
                lambda: main.start_odin_button.set_label("Start Odin Session"),
                lambda: main.change_button_command(
                    main.start_odin_button,
                    lambda _: main.send_cmd_entry("begin odin"),
                ),
                lambda: main.set_widget_state(
                    main.start_odin_button, main.flash_button, state=False
                ),
                lambda: main.connect_button.set_label("Connect"),
                lambda: main.change_button_command(
                    main.connect_button, lambda _: main.send_cmd_entry("connect")
                ),
            ],
            "Successfully began an Odin session!": [
                lambda: print("Successfully began an Odin session!"),
                # NOTE: Why do we need to enable the start_odin_button here?
                # It's supposed to be enabled above ^.
                lambda: main.set_widget_state(
                    main.start_odin_button,
                    main.flash_button,
                    # main.t_flash_switch_row,
                    # main.efs_clear_switch_row,
                    # main.bootloader_update_switch_row,
                    # main.reset_flash_count_switch_row,
                    state=True,
                ),
                lambda: main.start_odin_button.set_label("End Odin Session"),
                lambda: main.change_button_command(
                    main.start_odin_button, lambda _: main.end_odin()
                ),
            ],
            "Successfully ended an Odin session!": [
                lambda: print("Successfully ended an Odin session!"),
                lambda: main.set_widget_state(
                    main.flash_button,
                    main.flash_button,
                    main.t_flash_switch_row,
                    main.efs_clear_switch_row,
                    main.bootloader_update_switch_row,
                    main.reset_flash_count_switch_row,
                    state=False,
                ),
                lambda: main.start_odin_button.set_label("Start Odin Session"),
                lambda: main.change_button_command(
                    main.start_odin_button, lambda _: main.start_odin_session()
                ),
                # We disable it because with Thor:
                # "You can't reuse the same USB connection after you close an
                # Odin session, and you can't re-connect the device.
                # You have to reboot each time."
                lambda: main.set_widget_state(main.start_odin_button, state=False),
            ],
            'Successfully set "T-Flash" to "true"!': [
                lambda: main.option_change_successful("t_flash", True)
            ],
            'Successfully set "T-Flash" to "false"!': [
                lambda: main.option_change_successful("t_flash", False)
            ],
            'Successfully set "EFS Clear" to "true"!': [
                lambda: main.option_change_successful("efs_clear", True)
            ],
            'Successfully set "EFS Clear" to "false"!': [
                lambda: main.option_change_successful("efs_clear", False)
            ],
            'Successfully set "Bootloader Update" to "true"!': [
                lambda: main.option_change_successful("bootloader_update", True)
            ],
            'Successfully set "Bootloader Update" to "false"!': [
                lambda: main.option_change_successful("bootloader_update", False)
            ],
            'Successfully set "Reset Flash Count" to "true"!': [
                lambda: main.option_change_successful("reset_flash_count", True)
            ],
            'Successfully set "Reset Flash Count" to "false"!': [
                lambda: main.option_change_successful("reset_flash_count", False)
            ],
        }

    def test(self):
        print(f"This is a test of the {self.name} plugin.")

    def initialise_buttons(self, main):
        main.set_widget_state(
            main.connect_button,
            main.start_odin_button,
            main.flash_button,
            state=False,
        )

    def flash(self, main):
        auto = main.settings.get("auto_partitions", False)
        files = []
        paths = {}
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            entry = getattr(main, f"{slot}_entry")
            if entry.get_text():
                file_path = entry.get_text()
                file = os.path.basename(file_path)
                files.append(file)
                paths[slot] = os.path.dirname(entry.get_text())
        if len(paths) == 0:
            print(main.strings["no_files_selected2"])
            main.create_alert_dialog(
                "Invalid files", main.strings["no_files_selected2"]
            )
        elif len(set(paths.values())) > 1:
            print("The files NEED to be in the same dir...")
            main.create_alert_dialog("Invalid files", main.strings["invalid_files"])
        else:
            base_dir = list(paths.values())[0]
            main.thor_select_partitions(files, base_dir, auto)

    def select_device(self, main, function=None):
        def set_selected_device(btn, device):
            if btn.get_active:
                self.device = device

        def send_selected_device(cancel=False):
            if cancel:
                times = len(devices)
            else:
                times = self.device - 1
            for _ in range(times):
                # Send "Down Arrow"
                main.send_cmd("\x1b[B", False)
            # Send "Enter"
            main.send_cmd("\n", False)

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
            box = self.gtk.Box.new(self.gtk.Orientation.VERTICAL, 5)
            grid = self.gtk.Grid()
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
                checkbutton.connect("toggled", set_selected_device, row)
                row = row + 1

            responses = [
                {"id": "cancel", "label": "Cancel", "appearance": "0"},
                {"id": "ok", "label": "OK", "appearance": "0"},
            ]
            main.create_alert_dialog(
                main.strings["choose_a_device"], "", responses, callback, "ok", box
            )

        devices = main.get_output(
            "connect", "Choose a device to connect to:", "Cancel operation"
        )
        # Make sure each device is on one line.
        devices = clean_devices(devices)
        # TODO: I haven't actually tested this with two devices connected.
        # devices = ["/dev/device1", "/dev/device2"]
        if not devices[0] or devices[0] == "Timeout":
            print("No devices were found!")
        else:
            if len(devices) == 1:
                self.device = 1
                send_selected_device()
            else:
                self.device = 1
                display_devices()

    def select_partitions(self, main, files, base_dir, auto):
        main.retry_partition = False
        run = 0

        def send_selected_partitions(selected_partitions):
            print(f"selected_partitions: {selected_partitions}")
            n_partitions = len(selected_partitions)
            for i, partition in enumerate(selected_partitions):
                if partition:
                    print('SENDING: "Space"')
                    main.send_cmd("\x20", False)
                    self.time.sleep(0.05)
                # If it's the last partition displayed,
                # we don't need to send a down arrow.
                if not i == n_partitions:
                    print('SENDING: "Down Arrow"')
                    main.send_cmd("\x1b[B", False)
                    self.time.sleep(0.05)

        def display_partitions(partitions, file):
            selected_partitions = []

            def partition_toggled(button, row):
                if button.get_active():
                    selected_partitions[row] = True
                else:
                    selected_partitions[row] = False

            def return_selected_partitions(cancel=False):
                if not cancel:
                    send_selected_partitions(selected_partitions)
                print('SENDING: "Enter"')
                main.send_cmd("\n", False)
                self.time.sleep(0.3)
                self.glib.idle_add(select)

            def callback(dialog, result):
                response_id = dialog.choose_finish(result)
                print(response_id)
                if response_id == "ok":
                    return_selected_partitions()
                elif response_id == "cancel":
                    return_selected_partitions(cancel=True)

            grid = self.gtk.Grid.new()

            box = self.gtk.Box.new(self.gtk.Orientation.VERTICAL, 10)
            box.append(grid)

            responses = [
                {"id": "ok", "label": "OK", "appearance": "0"},
            ]

            dialog = main.create_alert_dialog(
                "Select Partitions",
                f"Select what partitions to flash from:/n{file}",
                responses,
                callback,
                extra_child=box,
            )

            row = 0
            for i, partition in enumerate(partitions):
                btn = main.create_checkbutton(
                    partition, 0, row, grid, padding=(5, 5, 0, 0), width=2
                )
                btn.connect(
                    "toggled",
                    lambda _, btn=btn, row=i: partition_toggled(btn, row),
                )
                selected_partitions.append(False)
                row += 1

        def select():
            nonlocal run
            run += 1
            print(f"RUN {run}")
            end = None
            command = None
            wait = True
            if main.retry_partition:
                wait = False
                main.retry_partition = False
            # If this is the first run, run the flashTar command.
            if run == 1:
                end = "(Press <space> to select, <enter> to accept)"
                command = f"flashTar {base_dir}"
                print(f'RUNNING: "{command}"')
                main.send_cmd(command)
            # Get the output.
            output = main.get_output(
                command=None,
                start="shell>",
                end=end,
                wait=wait,
            )
            # print(f"output: {output}")
            if not output[0] or output[0] == "Timeout":
                print("No output was found.")
                print(output[0])
                return self.glib.SOURCE_CONTINUE
            else:
                # If the output is for selecting partitions and is complete.
                if output[0] == "Choose what partitions to flash from":
                    print("Found start of partitions.")
                    # TODO: Have a function that checks for a string (which may or may not be on one line) in output.
                    # if output[-1] == "(Press <space> to select, <enter> to accept)":
                    if "ept)" in output[-1]:
                        print("Found end of partitions.")
                        output = output[1:]
                        file_lines = []
                        print(output)
                        for line in output:
                            if line.startswith("> [ ]"):
                                break
                            # This is displayed if Thor can't match any partitions.
                            elif line == "…":
                                break
                            file_lines.append(line)
                        file = ""
                        if file_lines:
                            if ":" in file_lines[0]:
                                file = file_lines[0].split(":")[0].strip()
                            else:
                                file = "".join(file_lines)
                                if file.endswith(":"):
                                    file = file[:-1]
                        print(f'FILE: "{file}"')
                        # If the file was selected by the user.
                        if file in files:
                            print("File was selected.")
                            # Extract the partitions
                            partitions = [
                                line.lstrip("> [ ] ")
                                for line in output
                                if line.startswith("> [ ] ") or line.startswith("[ ] ")
                            ]
                            print(f"PARTITIONS: {partitions}")
                            selected_partitions = []
                            # If the "Automatically select all partitions"
                            # setting is True.
                            if auto:
                                print("Automatically selecting all partitions.")
                                for partition in partitions:
                                    selected_partitions.append(True)
                                send_selected_partitions(selected_partitions)
                                # Send "Enter" once we have selected the partitions
                                # that we want.
                                print('SENDING: "Enter"')
                                main.send_cmd("\n", False)
                                self.time.sleep(0.3)
                                return self.glib.SOURCE_CONTINUE
                            else:
                                print(f'Select what partitions to flash from: "{file}"')
                                shortened_file = self.shared_utils.shorten_string(
                                    file, 46
                                )
                                display_partitions(partitions, shortened_file)
                        # If the file wasn't selected by the user.
                        else:
                            print("File wasn't selected.")
                            print('SENDING: "Enter"')
                            main.send_cmd("\n", False)
                            self.time.sleep(0.3)
                            return self.glib.SOURCE_CONTINUE
                    else:
                        main.retry_partition = True
                        return self.glib.SOURCE_CONTINUE
                elif output[0].startswith("You chose to flash"):
                    print("Verifying flash.")
                    n_partitions = self.re.search(r"(\d+) partitions", output[0])
                    partition_list = []
                    for line in output:
                        if line.startswith("Are you absol"):
                            break
                        partition_list.append(line)
                    main.verify_flash(n_partitions.group(1), partition_list, auto)
                    return self.glib.SOURCE_REMOVE
                else:
                    print(f"Unknown output:\n{output}")
                    return self.glib.SOURCE_REMOVE

        self.glib.idle_add(select)
