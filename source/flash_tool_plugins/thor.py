# flash_tool_plugins/thor.py
from flash_tool_plugins import FlashToolPlugin
import os
import re
import logging
import pexpect
import threading
import time

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class Thor(FlashToolPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.glib = main.glib
        self.shared_utils = main.shared_utils
        self.gtk = main.gtk
        self.re = main.re
        self.name = "thor"
        self.displayed_name = "Thor"
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

    def test(self):
        logger.debug("test is running")
        logger.debug(f"test: This is a test of the {self.name} plugin.")

    def setup_flash_tool(self, main):
        logger.debug("setup_flash_tool is running")
        main.child.expect("shell>")
        main.set_widget_state(main.start_page.button0, state=True)

    def check_files(self, main, selected_files):
        logger.debug("check_files is running")
        files = []
        paths = {}
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            slot_lowered = slot.lower()
            # file_path = main.selected_files[slot_lowered]
            # if slot_lowered in selected_files:
            if slot in selected_files:
                # file_path = selected_files[slot_lowered]
                file_path = selected_files[slot]
                if file_path:
                    file_name = os.path.basename(file_path)
                    files.append(file_name)
                    paths[slot] = os.path.dirname(file_path)
        if len(paths) == 0:
            logger.info(f'check_files: {main.strings["no_files_selected2"]}')
            main.create_alert_dialog(
                "Invalid files", main.strings["no_files_selected2"]
            )
        elif len(set(paths.values())) > 1:
            logger.info("check_files: The files NEED to be in the same dir...")
            main.create_alert_dialog("Invalid files", main.strings["invalid_files"])
        else:
            self.on_selected_files(main, files, paths)

    def on_selected_files(self, main, selected_files, paths):
        logger.debug("on_selected_files is running")
        self.selected_files = selected_files
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
                logger.info(
                    "connect: There is only one device, selecting it automatically."
                )
                device_number = 1
                self.selected_device(main, device_number, num_devices)
            else:
                # Have the user select a device.
                main.display_select_device_page(devices)

        # If no devices were found.
        elif result == 1:
            main.on_no_devices_found()
        # If we're already connected to a device.
        elif result == 2:
            logger.info("connect: Already connected to a device!")
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f"connect: Unexpected output:\n{output=}")

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
            logger.info("selected_device: Succesfully connected to the device!")
            self.start_odin_session(main)
        elif result == 1:
            logger.info("selected_device: Device disconnected?")
        elif result == 2:
            logger.info("selected_device: Canceled by user.")
        elif result == 3:
            logger.info(
                "selected_device: Failed to claim interface: Device or resource busy (16)."
            )
        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f"selected_device: Failed to connect:\n{output=}")

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
            self.select_partitions(main, base_dir, auto)
        elif result == 1:
            logger.info(
                "start_odin_session: Failed to bulk read: Connection timed out (110)."
            )

            def callback(dialog, result):
                response_id = dialog.choose_finish(result)
                if response_id == "cancel":
                    logger.info(
                        "start_odin_session: TODO: Do whatever cancel should do."
                    )
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
            logger.error(
                f"start_odin_session: Failed to start an odin session:\n{output=}"
            )

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

    def cycle(self, main):
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
                cleaned_lines = main.clean_output(output)
                cleaned_string = main.list_to_string(cleaned_lines, separator="")
                logger.debug(f'cycle: {cleaned_lines=}')
                file = None
                buffer = None
                partitions = []
                for line in reversed(cleaned_lines):
                    line = line.strip()
                    if line.endswith(":"):
                        break
                    elif line.startswith("> [ ]") or line.startswith("[ ]"):
                        partition = self.clean_partition_name(line)
                        partitions.insert(0, partition)
                file = self.get_file(cleaned_string)
                logger.debug(f'cycle: FILE: {repr(file)}')
                logger.debug(f"cycle: SELECTED_FILES: {self.selected_files}")
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
                if file in self.selected_files:
                    logger.debug(f"cycle: File was selected. {file=}")
                    if self.auto:
                        selected_partitions = [True] * len(partitions)
                        self.send_selected_partitions(main, selected_partitions)
                    else:
                        # Have the user select the partitions to flash.
                        main.display_select_partitions_page(
                            file, partitions, self.send_selected_partitions
                        )
                else:
                    logger.info(f"cycle: File wasn't selected, skipping. {file=}")
                    logger.debug('cycle: Sending "Enter".')
                    main.child.send("\n")
                    self.expect_output(
                        main,
                        ["(Press <space> to select, <enter> to accept)"],
                        timeout=1,
                    )
                    self.cycle(main)
            elif result == 1:
                self.verify_flash(main)
        except pexpect.EOF:
            logger.error("cycle: Unexpected EOF from the child process.")
        except pexpect.TIMEOUT:
            logger.error("cycle: Timeout waiting for output.")
            output = main.child.before.decode("utf-8")
            cleaned_output = main.remove_ansi_escape_sequences(output)
            print(cleaned_output)
            main.child.interact()

    def send_selected_partitions(self, main, selected_partitions):
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
        self.cycle(main)

    def select_partitions(self, main, base_dir, auto):
        logger.debug("select_partitions is running")
        self.last_file = None
        self.auto = auto
        logger.debug(f'select_partitions: Running "flashTar {base_dir}".')
        main.child.sendline(f"flashTar {base_dir}")
        self.cycle(main)

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

    def verify_flash(self, main):
        logger.debug("verify_flash is running")
        output = main.child.before.decode("utf-8")
        #cleaned_output = main.remove_ansi_escape_sequences(output)
        cleaned_lines = main.clean_output(output)
        cleaned_string = main.list_to_string(cleaned_lines, separator=" ")
        num_files = len(self.selected_files)
        #num_partitions = self.get_num_partitions(cleaned_output)
        num_partitions = self.get_num_partitions(cleaned_string)
        if not num_partitions == None:
            noun = "the computer" if self.auto else "you"
            files_noun = "file" if num_files == 1 else "files"
            partitions_noun = "partition" if num_partitions == 1 else "partitions"
            pronoun = "it" if num_partitions == 1 else "them"
            text = f"You selected {num_files} {files_noun}, and {noun} selected {num_partitions} {partitions_noun} to flash. Are you absolutely sure you want to flash {pronoun}?"
            main.display_verify_flash(text, self.on_verified_flash)
        else:
            logger.error(
                f"verify_flash: {num_partitions=}, {repr(cleaned_output)}\n\n\n"
            )
            print(cleaned_output)
            main.child.interact()

    def get_progress_and_wait_for_end(self, main):
        flashed_components = []
        logger.debug("get_progress_and_wait_for_end is running")
        main.display_flash_progress()

        def check_for_output(main):
            while True:
                result = main.child.expect(
                    [
                        r"(\d{2}:\d{2}:\d{2})",
                        "shell>",
                        pexpect.TIMEOUT,
                        pexpect.EOF,
                    ],
                    timeout=600,
                )
                if result == 0:
                    output = main.child.before.decode("utf-8")
                    matched_components = re.findall(r"onto\s+([A-Z][A-Z0-9]*)", output)
                    for component in matched_components:
                        if component not in flashed_components:
                            logger.info(
                                f"get_progress_and_wait_for_end: Flashed {component}"
                            )
                            self.glib.idle_add(
                                main.update_flash_progress, f"Flashed {component}"
                            )
                            # main.update_flash_progress(f"Flashed {component}")
                            flashed_components.append(component)
                    time.sleep(0.2)
                elif result == 1:
                    logger.info(f"get_progress_and_wait_for_end: {flashed_components=}")
                    self.glib.idle_add(
                        main.update_flash_progress, "Ending Odin Session..."
                    )
                    ended = self.end_odin_session(main)
                    if ended:
                        self.glib.idle_add(
                            main.update_flash_progress, "Disconnecting the device..."
                        )
                        disconnected = self.disconnect(main)
                        if disconnected:
                            main.display_done_flashing()
                        else:
                            logger.error(
                                "get_progress_and_wait_for_end: Failed to disconnect the device!"
                            )
                    else:
                        logger.error(
                            "get_progress_and_wait_for_end: Failed to end the Odin session!"
                        )
                    break
                elif result == 2:
                    logger.error("get_progress_and_wait_for_end: Timeout.")
                    break
                elif result == 3:
                    logger.error("get_progress_and_wait_for_end: EOF.")
                    break

        check_for_output(main)

    # Returns True if able to end, False otherwise.
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
            return True
        elif result == 1:
            logger.error("end_odin_session: Timeout.")
            return False
        elif result == 2:
            logger.error("end_odin_session: EOF.")
            return False

    def on_verified_flash(self, main, continue_flashing):
        logger.debug("on_verified_flash is running")
        if continue_flashing:
            logger.debug('on_verified_flash: Sending "y".')
            main.child.send("y")
            logger.debug('on_verified_flash: Sending "Enter".')
            main.child.send("\n")
            thread = threading.Thread(
                target=self.get_progress_and_wait_for_end, args=(main,)
            )
            thread.start()
        else:
            logger.debug(f"on_verified_flash: Canceling the flash.")
            logger.debug('on_verified_flash: Sending "n".')
            main.child.send("n")
            logger.debug('on_verified_flash: Sending "Enter".')
            main.child.send("\n")
            ended = self.end_odin_session(main)
            if ended:
                disconnected = self.disconnect(main)
                if disconnected:
                    main.cancel_flash("start")
                else:
                    logger.error("on_verified_flash: Failed to disconnect the device!")
            else:
                logger.error("on_verified_flash: Failed to end the Odin session!")

    def clean_partition_name(self, string):
        logger.debug("clean_partition_name is running")
        # Remove '> [ ] ' or '[ ] ' from the beginning of the string
        cleaned_string = re.sub(r"^(> \[ \] |\[ \] )", "", string)
        return cleaned_string
    
    def get_file(self, text):
        logger.debug("get_file is running")
        
        # Find the last occurrence of ":"
        colon_index = text.rfind(":")
        
        # If no colon is found or it's the first character, return None.
        if colon_index == -1 or colon_index == 0:
            return None
        
        # Extract the substring before the colon.
        substring = text[:colon_index].strip()
        
        # Find the start phrase
        start_phrase = "Choose what partitions to flash from"
        start_index = substring.find(start_phrase)
        
        # If the start phrase is found, extract everything after it.
        if start_index != -1:
            file = substring[start_index + len(start_phrase):].strip()
        else:
            # If the start phrase is not found, take the whole substring.
            file = substring

        logger.debug(f"get_file: Extracted file: {repr(file)}")
        return file

