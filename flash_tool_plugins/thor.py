# flash_tool_plugins/thor.py
from flash_tool_plugins import FlashToolPlugin
import os
import re
import logging
import pexpect
import threading

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


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
        # Not used anymore.
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
        """

    def test(self):
        logger.debug("test is running")
        print(f"This is a test of the {self.name} plugin.")

    def setup_flash_tool(self, main):
        logger.debug("setup_flash_tool is running")
        main.child.expect("shell>")
        main.set_widget_state(main.flash_button, state=True)

    def selected_files(self, main, files, paths):
        logger.debug("selected_files is running")
        self.files = files
        self.paths = paths
        self.connect(main)

    def connect(self, main):
        logger.debug("connect is running")
        main.child.sendline("connect")
        result = main.child.expect(
            [
                "Cancel operation",
                "No Samsung devices were found!",
                "Already connected to a device!",
            ]
        )

        # If at least one device is detected.
        if result == 0:
            output = main.child.before.decode("utf-8")
            cleaned_output = main.remove_ansi_escape_sequences(output)
            devices = []
            for line in reversed(
                [line for line in map(str.strip, cleaned_output.splitlines()) if line]
            ):
                # print(f"line: '{line}'")
                # print(f"repr line: {repr(line)}")
                if line == "Choose a device to connect to:":
                    # print("Found top of device list.")
                    break
                devices.append(line)
            # print("devices: ", devices)
            logger.debug(f"{devices=}")
            # For testing.
            # devices = ["device 1", "device 2"]
            num_devices = len(devices)
            if num_devices == 1:
                print("There is only one device, selecting it automatically.")
                device_number = 1
                self.selected_device(main, device_number, num_devices)
            else:
                # Have the user select a device.
                main.select_device(devices)

        # If no devices were found.
        elif result == 1:
            main.on_no_devices_found()
        # If we're already connected to a device.
        elif result == 2:
            logger.info('connect: Already connected to a device!')
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f'connect: Unexpected output:\n{output=}')

    def selected_device(self, main, device, num_devices):
        logger.debug("selected_device is running")
        logger.debug(f"selected_device: {device=}")
        if device == None:
            times_down = num_devices
        elif device == 1:
            times_down = 0
        else:
            times_down = device - 1
        for _ in range(times_down):
            # Send "Down Arrow"
            logger.debug('selected_device: Sending "Down Arrow".')
            main.child.send("\x1b[B")
        logger.debug('selected_device: Sending "Enter".')
        main.child.send("\n")
        result = main.child.expect_exact(
            [
                "Successfully connected to the device!",
                "Device disconnected?",
                "Cancelled by user",
                "Device or resource busy (16)",
            ]
        )
        if result == 0:
            logger.info('selected_device: Succesfully connected to the device!')
            # TODO: Flash the device.
            self.start_odin_session(main)
        elif result == 1:
            logger.info('selected_device: Device disconnected?')
        elif result == 2:
            logger.info('selected_device: Canceled by user.')
        elif result == 3:
            logger.info('selected_device: Failed to claim interface: Device or resource busy (16).')
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f'selected_device: Failed to connect:\n{output=}')

    def initialise_buttons(self, main):
        logger.debug("initialise_buttons is running")
        main.set_widget_state(
            main.flash_button,
            state=False,
        )

    def flash(self, main):
        logger.debug("flash is running")
        auto = main.settings.get("auto_partitions", False)
        base_dir = list(self.paths.values())[0]
        self.select_partitions(self.files, base_dir, auto)
        # self.start_odin_session(main)

    def start_odin_session(self, main):
        logger.debug("start_odin_session is running")
        # main.child.expect("shell>")
        main.child.sendline("begin odin")
        result = main.child.expect_exact(
            [
                "Successfully began an Odin session!",
                "Failed to bulk read: Connection timed out (110)",
            ],
            timeout=10,
        )
        if result == 0:
            logger.info("start_odin_session: Successfully began an Odin session!")
            base_dir = list(self.paths.values())[0]
            auto = main.settings.get("auto_partitions", False)
            self.select_partitions(main, self.files, base_dir, auto)
        elif result == 1:
            logger.info("start_odin_session: Failed to bulk read: Connection timed out (110).")

            def callback(dialog, result):
                response_id = dialog.choose_finish(result)
                if response_id == "cancel":
                    logger.info("start_odin_session: TODO: Do whatever cancel should do.")
                elif response_id == "continue":
                    disconnected = self.disconnect(main)
                    if disconnected:
                        logger.info("start_odin_session: Reconnecting...")
                        self.connect(main)
                    else:
                        logger.info("start_odin_session: Would not reconnect.")

            responses = [
                {"id": "continue", "label": "Continue", "appearance": "0"},
            ]
            main.create_alert_dialog(
                "Failed to start an Odin Session",
                "Try re-entering Download Mode on the device, and then click 'Continue'.",
                responses,
                callback,
                "retry",
            )
            # print(main.child.before)
            # main.child.interact()
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f"start_odin_session: Failed to start an odin session:\n{output=}")

    # Returns True if able to disconnect, False otherwise.
    def disconnect(self, main):
        logger.debug("disconnect is running")
        main.child.sendline("disconnect")
        result = main.child.expect_exact(
            [
                "Successfully disconnected the device!",
            ],
            timeout=10,
        )
        if result == 0:
            logger.info("disconnect: Successfully disconnected the device!")
            return True
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f"disconnect: Failed to disconnect the device:\n{output=}")
            return False

    def cycle(self, main, files):
        logger.debug("cycle is running")
        try:
            result = main.child.expect_exact(
                [
                    "(Press <space> to select, <enter> to accept)",
                    "sure you want to flash those?",
                ],
                timeout=10,
            )
            if result == 0:
                logger.debug("cycle: Found end of partitions.")
                output = main.child.before.decode("utf-8")
                cleaned_output = main.remove_ansi_escape_sequences(output)
                output_lines = cleaned_output.splitlines()
                file = None
                buffer = None
                partitions = []
                for line in reversed(output_lines):
                    line = line.strip()
                    if line.endswith(":"):
                        break
                    elif line.startswith("> [ ]") or line.startswith("[ ]"):
                        partitions.insert(0, line)
                file = self.get_file(cleaned_output)
                logger.debug(f'cycle: FILE: "{file}"')
                logger.debug(f"cycle: FILES: {files}")
                logger.debug(f"cycle: PARTITIONS: {partitions}")
                if file == self.last_file:
                    logger.error("cycle: file = last_file.\n\n\n")
                    print(main.child.before)
                    main.child.interact()
                if not file:
                    logger.error("cycle: file = None")
                    print(output_lines)
                    print("\n\n\n")
                    print(main.child.before)
                    main.child.interact()
                self.last_file = file
                if file in files:
                    logger.debug(f"cycle: File was selected: '{file}'")
                    if self.auto:
                        selected_partitions = [True] * len(partitions)
                        self.send_selected_partitions(main, selected_partitions, files)
                    else:
                        # Have the user select the partitions to flash.
                        main.select_partitions(
                            partitions, self.send_selected_partitions, files
                        )
                else:
                    logger.info(f"cycle: File wasn't selected, skipping: '{file}'")
                    logger.debug('cycle: Sending "Enter".')
                    main.child.send("\n")
                    self.expect_output(
                        main,
                        ["(Press <space> to select, <enter> to accept)"],
                        timeout=1,
                    )
                    self.cycle(main, files)
            elif result == 1:
                print("Time to verify flash!")
                self.verify_flash(main)
        except pexpect.EOF:
            logger.error("cycle: Unexpected EOF from the child process.")
        except pexpect.TIMEOUT:
            logger.error("cycle: Timeout waiting for output.")
            output = main.child.before.decode("utf-8")
            cleaned_output = main.remove_ansi_escape_sequences(output)
            print(cleaned_output)
            main.child.interact()

    def send_selected_partitions(self, main, selected_partitions, files):
        logger.debug("send_selected_partitions is running")
        if selected_partitions == None:
            logger.debug("send_selected_partitions: Canceling...")
        else:
            n_partitions = len(selected_partitions)
            for i, partition in enumerate(selected_partitions):
                if partition:
                    logger.debug('send_selected_partitions: Sending "Space".')
                    main.child.send("\x20")
                    self.expect_output(
                        main,
                        ["(Press <space> to select, <enter> to accept)"],
                        timeout=1,
                    )
                # If it's the last partition displayed,
                # we don't need to send a down arrow.
                # i+1 because i starts at 0.
                if not i + 1 == n_partitions:
                    logger.debug('send_selected_partitions: Sending "Down Arrow".')
                    main.child.send("\x1b[B")
                    self.expect_output(
                        main,
                        [
                            "(Press <space> to select, <enter> to accept)",
                        ],
                        timeout=1,
                    )
        logger.debug('send_selected_partitions: Sending "Enter".')
        main.child.send("\n")
        self.expect_output(
            main,
            [
                "(Press <space> to select, <enter> to accept)",
            ],
            timeout=1,
        )
        self.cycle(main, files)

    def select_partitions(self, main, files, base_dir, auto):
        logger.debug("select_partitions is running")
        self.last_file = None
        self.auto = auto
        main.child.sendline(f"flashTar {base_dir}")
        self.cycle(main, files)

    # THIS was the problem.
    def expect_output(self, main, expected_end_output, timeout=1):
        logger.debug("expect_output is running")
        try:
            result = main.child.expect_exact(expected_end_output, timeout=timeout)
            return result
        except pexpect.EOF:
            logger.error("expect_output: Received EOF.")
        except pexpect.TIMEOUT:
            logger.error(
                f"expect_output: Timed-out.\nexpected_end_output: {expected_end_output}\n\n\n"
            )
            output = main.child.before.decode("utf-8")
            cleaned_output = main.remove_ansi_escape_sequences(output)
            print(cleaned_output)
            main.child.interact()

    def get_num_partitions(self, text):
        logger.debug(f"get_num_partitions is running, {text=}")
        match = re.search(r"(\d+) partitions in total:", text)
        if match:
            return int(match.group(1))
        else:
            logger.error("get_num_partitions: Match not found.")
            return None

    # WIP
    def verify_flash(self, main):
        logger.debug("verify_flash is running")
        output = main.child.before.decode("utf-8")
        cleaned_output = main.remove_ansi_escape_sequences(output)
        num_partitions = self.get_num_partitions(cleaned_output)
        if num_partitions:
            main.verify_flash(self.auto, num_partitions, self.on_verified_flash)
        else:
            logger.error(
                f"verify_flash: {num_partitions=}, {repr(cleaned_output)}\n\n\n"
            )
            print(cleaned_output)
            main.child.interact()

    def wait_for_done_flashing(self, main):
        logger.debug("wait_for_done_flashing is running")
        result = main.child.expect_exact(
            [
                "shell>",
                pexpect.TIMEOUT,
                pexpect.EOF,
            ],
            timeout=600,
        )
        if result == 0:
            self.end_odin_session(main)
        elif result == 1:
            logger.error("wait_for_done_flashing: Timeout.")
        elif result == 2:
            logger.error("wait_for_done_flashing: EOF.")
        main.child.interact()

    def end_odin_session(self, main):
        logger.debug("end_odin_session is running")
        logger.debug('end_odin_session: Running "end".')
        main.child.sendline("end")
        result = main.child.expect_exact(
            [
                "Successfully ended an Odin session!",
                pexpect.TIMEOUT,
                pexpect.EOF,
            ],
            timeout=30,
        )
        if result == 0:
            logger.info("end_odin_session: Successfully ended an Odin session!")
        elif result == 1:
            logger.error("end_odin_session: Timeout.")
        elif result == 2:
            logger.error("end_odin_session: EOF.")

    def on_verified_flash(self, main, continue_flashing):
        logger.debug("on_verified_flash is running")
        if continue_flashing:
            logger.debug('on_verified_flash: Sending "y".')
            main.child.send("y")
            logger.debug('on_verified_flash: Sending "Enter".')
            main.child.send("\n")
            thread = threading.Thread(target=self.wait_for_done_flashing, args=(main,))
            thread.start()
        else:
            # TODO: Cancel flash.
            logger.debug(f"verified_flash: Canceling the flash.")
            logger.debug('verified_flash: Sending "n".')
            main.child.send("n")
            logger.debug('verified_flash: Sending "Enter".')
            main.child.send("\n")
            main.child.interact()

    def get_file(self, text):
        logger.debug("get_file is running")
        # Find the last occurrence of ":"
        colon_index = text.rfind(":")
        # If no colon is found or it's the first character, return False.
        if colon_index == -1 or colon_index == 0:
            return None
        # Extract the substring before the colon.
        substring = text[:colon_index].strip()
        # Find the start phrase
        start_phrase = "Choose what partitions to flash from"
        start_index = substring.find(start_phrase)
        # If the start index is found, extract everything after it.
        if start_index != -1:
            file = substring[start_index + len(start_phrase) :].strip()
        else:
            # If the end phrase is not found, take the whole substring.
            file = substring
        return file

    # Function that was used extensively for testing. Has been superceded by the above code. (cycle, send_selected_partitions, etc.)
    """
    def select_partitions(self, main, files, base_dir, auto):
        self.last_file = None
        run = 0

        def send_selected_partitions(selected_partitions):
            print(f"selected_partitions: {selected_partitions}")
            n_partitions = len(selected_partitions)
            for i, partition in enumerate(selected_partitions):
                if partition:
                    print('SENDING: "Space"')
                    main.child.send("\x20")  # Send space to select
                    # self.time.sleep(0.05)
                    self.expect_output(main, ["(Press <space> to select, <enter> to accept)"], timeout=1)
                if i < n_partitions - 1:  # Only send down arrow if not the last one
                    print('SENDING: "Down Arrow"')
                    main.child.send("\x1b[B")  # Send down arrow
                    # self.time.sleep(0.05)
                    self.expect_output(main, ["(Press <space> to select, <enter> to accept)"], timeout=1)

        def display_partitions(partitions, file):
            self.prev_file = file
            selected_partitions = [False] * len(partitions)

            def partition_toggled(button, row):
                selected_partitions[row] = button.get_active()

            def return_selected_partitions(cancel=False):
                if not cancel:
                    send_selected_partitions(selected_partitions)
                print('SENDING: "Enter"')
                main.child.send("\n")  # Finalize selection
                # self.time.sleep(1)
                result = self.expect_output(main, ["(Press <space> to select, <enter> to accept)", "You chose to flash"], timeout=5)
                if result == 0:
                    #return self.glib.SOURCE_CONTINUE
                    self.glib.idle_add(select)
                elif result == 1:
                    print("Time to verify flash!")
                    self.verify_flash(main)

            def callback(dialog, result):
                response_id = dialog.choose_finish(result)
                if response_id == "ok":
                    return_selected_partitions()
                elif response_id == "cancel":
                    return_selected_partitions(cancel=True)

            grid = self.gtk.Grid.new()
            box = self.gtk.Box.new(self.gtk.Orientation.VERTICAL, 10)
            box.append(grid)

            responses = [{"id": "ok", "label": "OK", "appearance": "0"}]
            dialog = main.create_alert_dialog(
                "Select Partitions",
                f"Select what partitions to flash from:/n{file}",
                responses,
                callback,
                extra_child=box,
            )

            for row, partition in enumerate(partitions):
                btn = main.create_checkbutton(
                    partition, 0, row, grid, padding=(5, 5, 0, 0), width=2
                )
                btn.connect(
                    "toggled", lambda _, btn=btn, row=row: partition_toggled(btn, row)
                )

        def select():
            nonlocal run
            run += 1
            print(f"RUN {run}")

            if run == 1:
                command = f"flashTar {base_dir}"
                print(f'RUNNING: "{command}"')
                main.child.sendline(command)  # Send command to child
            try:
                # Expect the output from the child process
                result = main.child.expect_exact(
                    [
                        "(Press <space> to select, <enter> to accept)",
                        "You chose to flash ",
                    ],
                    timeout=10,
                )

                if result == 0:  # Found the end of partitions
                    print("Found end of partitions.")
                    # output_lines = main.child.before.decode("utf-8").splitlines()
                    output = main.child.before.decode("utf-8")
                    cleaned_output = main.remove_ansi_escape_sequences(output)
                    output_lines = cleaned_output.splitlines()
                    file = None
                    buffer = None
                    partitions = []
                    for line in reversed(output_lines):
                        line = line.strip()
                        if line.endswith(":"):
                            break
                        elif line.startswith("> [ ]") or line.startswith("[ ]"):
                            partitions.insert(0, line)
                    file = self.get_file(cleaned_output)
                    print(f'FILE: "{file}"')
                    print(f"FILES: {files}")
                    print(f"PARTITIONS: {partitions}")
                    if file == self.last_file:
                        print("ERROR: last_file == file.\n\n\n\n\n\n\n")
                        print(main.child.before)
                        main.child.interact()
                    if not file:
                        print("ERROR: file = None")
                        print(output_lines)
                        print("\n\n\n\n")
                        print(main.child.before)
                        main.child.interact()
                    self.last_file = file
                    if file in files:
                        print("File was selected.")
                        if auto:
                            print("Automatically selecting all partitions.")
                            send_selected_partitions([True] * len(partitions))
                            print('SENDING: "Enter"')
                            main.child.send("\n")
                            # self.time.sleep(0.3)
                            self.expect_output(main, ["(Press <space> to select, <enter> to accept)"], timeout=1)
                            return self.glib.SOURCE_CONTINUE
                        else:
                            display_partitions(partitions, file)
                    else:
                        print("File wasn't selected.")
                        print('SENDING: "Enter"')
                        main.child.send("\n")
                        # self.time.sleep(0.3)
                        result = self.expect_output(main, ["(Press <space> to select, <enter> to accept)", "You chose to flash "], timeout=5)
                        if result == 0:
                            return self.glib.SOURCE_CONTINUE
                        elif result == 1:
                            print("Time to verify flash!")
                            self.verify_flash() 
                elif result == 1:
                    print("Time to verify flash!")
                    self.verify_flash(main)
            except pexpect.EOF:
                print("Unexpected EOF from the child process.")
                return self.glib.SOURCE_REMOVE
            except pexpect.TIMEOUT:
                print("Timeout waiting for output.")
                output = main.child.before.decode("utf-8")
                cleaned_output = main.remove_ansi_escape_sequences(output)
                print(cleaned_output)
                main.child.interact()
                return self.glib.SOURCE_REMOVE

        self.glib.idle_add(select)
        """
