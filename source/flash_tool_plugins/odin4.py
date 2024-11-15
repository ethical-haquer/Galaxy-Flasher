# flash_tool_plugins/odin4.py
from flash_tool_plugins import FlashToolPlugin
import os
import logging
import pexpect
import threading
import time

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class Odin4(FlashToolPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.glib = main.glib
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

    def setup_flash_tool(self, main):
        logger.debug("setup_flash_tool is running")
        main.child.expect(">>")
        main.set_widget_state(main.start_page.button0, state=True)

    def check_files(self, main, selected_files):
        logger.debug("check_files is running")
        if len(selected_files) == 0:
            logger.info(f'check_files: {main.strings["no_files_selected2"]}')
            main.create_alert_dialog(
                "Invalid files", main.strings["no_files_selected2"]
            )
        else:
            self.on_selected_files(main, selected_files)

    def on_selected_files(self, main, selected_files):
        logger.debug("on_selected_files is running")
        self.selected_files = selected_files
        self.connect(main)

    def connect(self, main):
        logger.debug("connect is running")
        main.child.sendline("list")
        result = main.child.expect(
            [
                ">>",
            ]
        )
        if result == 0:
            output = main.child.before.decode("utf-8")
            cleaned_output = main.remove_ansi_escape_sequences(output)
            devices = []
            for line in reversed(
                [line for line in map(str.strip, cleaned_output.splitlines()) if line]
            ):
                # print(f"line: '{line}'")
                # print(f"repr line: {repr(line)}")
                if line == "list":
                    # print("Found top of device list.")
                    break
                devices.append(line)
            print("devices: ", devices)
            logger.debug(f"{devices=}")
            # For testing.
            # devices = ["device 1", "device 2"]
            num_devices = len(devices)
            if num_devices == 1:
                logger.info(
                    "connect: There is only one device, selecting it automatically."
                )
                device = devices[0]
                self.selected_device(main, device, num_devices)
            elif num_devices == 0:
                main.on_no_devices_found()
            else:
                # Have the user select a device.
                main.display_devices(devices)

        else:
            output = main.remove_ansi_escape_sequences(
                main.child.before.decode("utf-8")
            )
            logger.error(f"connect: Unexpected output:\n{output=}")

    def get_progress_and_wait_for_end(self, main):
        logger.debug("get_progress_and_wait_for_end is running")
        main.display_flash_progress()

        def check_for_output(main):
            while True:
                result = main.child.expect(
                    [
                        "Check file :",
                        "Setup Connection",
                        "initializeConnection",
                        "Set Partition",
                        "Receive PIT Info",
                        "success getpit",
                        "Upload Binaries",
                        "Close Connection",
                        ">>",
                        pexpect.TIMEOUT,
                        pexpect.EOF,
                    ],
                    timeout=600,
                )
                if result == 0:
                    output = main.child.before.decode("utf-8")
                    self.glib.idle_add(main.update_flash_progress, "Checking files...")
                elif result == 1:
                    self.glib.idle_add(main.update_flash_progress, "Setup Connection")
                elif result == 2:
                    self.glib.idle_add(
                        main.update_flash_progress, "initializeConnection"
                    )
                elif result == 3:
                    self.glib.idle_add(main.update_flash_progress, "Set Partition")
                elif result == 4:
                    self.glib.idle_add(main.update_flash_progress, "Receive PIT Info")
                elif result == 5:
                    self.glib.idle_add(main.update_flash_progress, "success getpit")
                elif result == 6:
                    self.glib.idle_add(main.update_flash_progress, "Upload Binaries")
                elif result == 7:
                    self.glib.idle_add(main.update_flash_progress, "Close Connection")
                elif result == 8:
                    main.display_done_flashing()
                    break
                elif result == 9:
                    logger.error("get_progress_and_wait_for_end: Timeout.")
                    break
                elif result == 10:
                    logger.error("get_progress_and_wait_for_end: EOF.")
                    break
                time.sleep(0.1)

        check_for_output(main)

    def selected_device(self, main, device, num_devices):
        logger.debug("selected_device is running")
        logger.debug(f"selected_device: {device=}")
        if device == None:
            self.device = None
        else:
            self.device = device
            self.flash(main)

    def flash(self, main):
        logger.debug("flash is running")
        args = []
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            slot_to_arg = {
                "BL": "-b",
                "AP": "-a",
                "CP": "-c",
                "CSC": "-s",
                "USERDATA": "-u",
            }
            file = self.selected_files.get(slot)
            if file:
                arg = slot_to_arg[slot]
                file_arg = f"{arg} {file}"
                args.append(file_arg)
        device = self.device
        args.insert(0, f"-d {device}")
        command = " ".join(["flash"] + args)
        logger.info(f"flash: Running: {command}")
        main.child.sendline(command)
        thread = threading.Thread(
            target=self.get_progress_and_wait_for_end, args=(main,)
        )
        thread.start()

    def select_partitions(self, main, files, base_dir, auto):
        print("Odin4 has no working select_partitions function.")
