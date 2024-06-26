#!/usr/bin/env python3

"""
Galaxy Flasher - A GUI for Samsung Flash Tools
Copyright (C) 2023-2024 ethical_haquer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import locale
import os
import platform
import re
import sys
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Vte

locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = "_"
lang = locale.split(seperator, 1)[0]

version = "Alpha v0.5.1"
config_dir = GLib.get_user_config_dir()
app_dir = "galaxy-flasher"
app_config_dir = os.path.join(config_dir, app_dir)
if not os.path.exists(app_config_dir):
    os.makedirs(app_config_dir)
settings_file = os.path.join(app_config_dir, "settings.json")
swd = os.path.dirname(os.path.realpath(__file__))
locale_file = f"{swd}/locales/{lang}.json"
machine = platform.machine()
system = platform.system().lower()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.last_text = ""
        super().__init__(*args, **kwargs)
        # Add the CSS provider to the screen
        style_provider = Gtk.CssProvider()
        css = """
            .mybutton:not(:hover) {
                background-color: @popover-background-color;
            }

        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        # Load strings
        # TODO: Remove unneeded strings from en.json
        with open(locale_file) as json_string:
            self.strings = json.load(json_string)
        # Load settings
        self.load_settings()
        self.flashtool = self.settings.get("flash_tool", "thor")
        # If the system isn't linux.
        if system != "linux":
            print("Currently, Galaxy Flasher only supports Linux.")
            self.connect(
                "show",
                lambda _: self.error_dialog(
                    "Unsupported OS", "Currently, Galaxy Flasher only supports Linux."
                ),
            )
            flashtool_exec = [
                "echo",
                f"{system} is currently not supported by Galaxy Flasher.\nIf you think this is incorrect, please open an issue on GitHub, or let me know on XDA.",
            ]
        # If the system is linux.
        else:
            # Set the flash-tool path
            if self.flashtool == "thor":
                flashtool_path = (
                    f"{swd}/flash-tools/thor/{system}/{machine}/TheAirBlow.Thor.Shell"
                )
                self.prompt = "shell> "
            elif self.flashtool == "odin4":
                flashtool_path = f"{swd}/odin4-wrapper.sh"
                self.prompt = ">> "
            elif self.flashtool == "pythor":
                flashtool_path = f"{swd}/flash-tools/pythor/{system}/pythor_cli"
                self.prompt = ">> "
            # Only use the sudo setting for Thor.
            if self.settings.get("sudo", False) and self.flashtool == "thor":
                flashtool_exec = ["sudo", flashtool_path]
            else:
                flashtool_exec = [flashtool_path]
            # Check if flashtool_path exists.
            if not os.path.isfile(flashtool_path):
                print(f"Error: File {flashtool_path} not found")
                flashtool_exec = [
                    "echo",
                    f'The file: "{flashtool_path}" was not found.',
                ]
                self.connect(
                    "show",
                    lambda _: self.error_dialog(
                        "File not found",
                        f'The file: "{flashtool_path}" was not found.',
                    ),
                )
        # Define main grid
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)
        self.set_child(self.grid)
        # Set window title
        self.set_title(f"Galaxy Flasher - {version}")
        # Define stack to hold tabs
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)
        # Setup StackSwitcher
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        self.stack_switcher.set_margin_start(10)
        self.stack_switcher.set_margin_end(0)
        self.stack_switcher.set_margin_top(10)
        self.stack_switcher.set_margin_bottom(0)
        # Attach stack/StackSwitcher
        self.grid.attach(self.stack_switcher, 0, 0, 1, 1)
        self.grid.attach_next_to(
            self.stack, self.stack_switcher, Gtk.PositionType.BOTTOM, 1, 6
        )
        # Create flash-tool output box
        self.vte_term = Vte.Terminal()
        self.vte_term.spawn_async(
            Vte.PtyFlags.DEFAULT,  # Pty Flags
            swd,  # Working DIR
            flashtool_exec,  # Command/BIN (argv)
            None,  # Environmental Variables (env)
            GLib.SpawnFlags.DEFAULT,  # Spawn Flags
            None,
            None,  # Child Setup
            -1,  # Timeout (-1 for indefinitely)
            None,  # Cancellable
            None,  # Callback
            None,  # User Data
        )
        # Create scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.vte_term)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_halign(Gtk.Align.FILL)
        scrolled_window.set_valign(Gtk.Align.FILL)
        self.stack.add_titled(scrolled_window, "Log", "Log")
        # Set the theme
        theme = self.settings.get("theme") or "system"
        self.set_theme(theme)
        # Create other tabs
        for tab in ["Options", "Pit", "Settings"]:
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            self.stack.add_titled(grid, tab, tab)
            setattr(self, f"{tab.lower()}_grid", grid)
        # Create file slots
        row = 2
        padding = (0, 0, 0, 0)
        entry_padding = (0, 10, 0, 0)
        slots = ["BL", "AP", "CP", "CSC", "USERDATA"]
        for slot in slots:
            if slot is slots[-1]:
                padding = (0, 0, 0, 10)
                entry_padding = (0, 10, 0, 10)
            button = self.create_button(
                slot, 1, row, self.grid, lambda _, x=slot: self.open_file(x), padding
            )
            entry = self.create_entry(2, row, self.grid, entry_padding, 2, 1, True)
            setattr(self, f"{slot}_button", button)
            setattr(self, f"{slot}_entry", entry)
            if self.flashtool == "pythor":
                button.set_sensitive(False)
                entry.set_sensitive(False)
            row += 1
        # Create command entry
        self.command_entry = self.create_entry(
            column=1,
            row=1,
            grid=self.grid,
            padding=(0, 10, 0, 0),
            width=3,
            height=1,
        )
        self.command_entry.connect(
            "activate", lambda _, __: self.on_command_enter(), None
        )
        # Create the upper-right buttons.
        if self.flashtool == "thor":
            buttons = [
                {
                    "name": "connect_button",
                    "text": self.strings["connect"],
                    "command": lambda _: self.thor_select_device(),
                },
                {
                    "name": "start_odin_button",
                    "text": self.strings["start_odin_protocol"],
                    "command": lambda _: self.start_odin_session(),
                },
                {
                    "name": "flash_button",
                    "text": "Flash!",
                    "command": lambda _: self.flash(),
                },
            ]
        elif self.flashtool == "pythor":
            buttons = [
                {
                    "name": "help_button",
                    "text": "Help",
                    "command": lambda _: self.send_cmd("help"),
                },
                {
                    "name": "connect_button",
                    "text": "Connect",
                    "command": lambda _: self.connect_device(),
                },
                {
                    "name": "start_odin_button",
                    "text": "Start Session",
                    "command": lambda _: self.start_odin_session(),
                },
            ]
        elif self.flashtool == "odin4":
            buttons = [
                {
                    "name": "help_button",
                    "text": "Help",
                    "command": lambda _: self.send_cmd("help"),
                },
                {
                    "name": "list_button",
                    "text": "List Devices",
                    "command": lambda _: self.send_cmd("list"),
                },
                {
                    "name": "flash_button",
                    "text": "Flash!",
                    "command": lambda _: self.flash(),
                },
            ]
        column = 1
        padding = (0, 0, 10, 0)
        for btn in buttons:
            name = btn["name"]
            text = btn["text"]
            command = btn["command"]
            if btn is buttons[-1]:
                padding = (0, 10, 10, 0)
            button = self.create_button(
                text,
                column=column,
                row=0,
                grid=self.grid,
                command=command,
                padding=padding,
            )
            setattr(self, name, button)
            column += 1
        if self.flashtool == "thor":
            self.set_widget_state(
                self.connect_button,
                self.start_odin_button,
                self.flash_button,
                state=False,
            )
        elif self.flashtool == "odin4":
            self.set_widget_state(
                self.help_button, self.list_button, self.flash_button, state=False
            )
        elif self.flashtool == "pythor":
            self.set_widget_state(self.connect_button, state=False)
        # Setup header
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        # Create about action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about_window)
        self.add_action(about_action)
        # Create quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda _, __: sys.exit())
        self.add_action(quit_action)
        # Create menu
        menu = Gio.Menu.new()
        menu.append("About", "win.about")
        menu.append("Quit", "win.quit")
        # Create popover
        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu)
        # Create hamburger
        hamburger = Gtk.MenuButton()
        hamburger.set_popover(popover)
        hamburger.set_icon_name("open-menu-symbolic")
        header.pack_start(hamburger)
        # Create the Option tab widgets.
        # TODO: This could be improved to be more like the Settings tab.
        row = 0
        if self.flashtool == "thor":
            options = [
                {"option": "T Flash"},
                {"option": "EFS Clear (currently disabled)"},
                {"option": "Bootloader Update"},
                {"option": "Reset Flash Count"},
            ]
            for item in options:
                option = item["option"]
                check_button = self.create_checkbutton(
                    option, 0, row, self.options_grid, (6, 0, 0, 0)
                )
                check_button.connect("toggled", self.option_changed)
                if option == "EFS Clear (currently disabled)":
                    self.set_widget_state(check_button, state=False)
                row += 1
        elif self.flashtool == "odin4":
            row = 0
            self.create_label(
                text='The "-V" option will be added once I know what it does.',
                grid=self.options_grid,
                row=row,
                padding=(10, 0, 0, 0),
            )
        elif self.flashtool == "pythor":
            self.create_label(
                text="Currently, PyThor has no options.",
                grid=self.options_grid,
                padding=(10, 0, 0, 0),
            )
        # Create place-holder label for Pit tab.
        self.create_label(
            text=f"{self.strings['just_a_test']}\n\n{self.strings['pull_requests_welcome']}",
            grid=self.pit_grid,
            padding=(10, 0, 0, 0),
        )
        # Create the Settings tab widgets.
        settings_list = [
            {
                "title": "General",
                "settings": [
                    [
                        "combo",
                        "Flash Tool",
                        None,
                        "flash_tool",
                        "Thor",
                        "thor",
                        "Odin4",
                        "odin4",
                        "PyThor (in development)",
                        "pythor",
                    ],
                    [
                        "combo",
                        "Theme",
                        None,
                        "theme",
                        "System",
                        "system",
                        "Light",
                        "light",
                        "Dark",
                        "dark",
                    ],
                ],
            },
            {
                "title": "Thor",
                "settings": [
                    ["switch", "Run with sudo", None, "sudo", False],
                    [
                        "switch",
                        "Automatically select all partitions",
                        "Instead of asking you what partitions to flash, automatically select them all.",
                        "auto_partitions",
                        False,
                    ],
                ],
            },
        ]
        self.create_preferences(settings_list, self.settings_grid)
        # Create the terminal's right-click options.
        term_popover = Gtk.Popover()
        # This doesn't show an arrow, I'm not sure if we want one though.
        # term_popover.set_has_arrow(True)
        term_option_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        copy_button = Gtk.Button(label="Copy", css_classes=["mybutton"])
        copy_button.connect(
            "clicked",
            lambda button: (
                self.vte_term.copy_clipboard_format(1),
                term_popover.set_visible(False),
            ),
        )
        paste_button = Gtk.Button(label="Paste", css_classes=["mybutton"])
        paste_button.connect(
            "clicked",
            lambda button: (
                self.vte_term.paste_clipboard(),
                term_popover.set_visible(False),
            ),
        )
        term_option_box.append(copy_button)
        term_option_box.append(paste_button)
        term_popover.set_child(term_option_box)
        self.vte_term.set_context_menu(term_popover)
        # Scan the output whenever it changes
        self.vte_term.connect("contents-changed", self.scan_output)
        # Print out the ASCII text "Galaxy Flasher", created with figlet.
        print(
            rf"""
  ____       _                    _____ _           _
 / ___| __ _| | __ ___  ___   _  |  ___| | __ _ ___| |__   ___ _ __ 
| |  _ / _` | |/ _` \ \/ / | | | | |_  | |/ _` / __| '_ \ / _ \ '__|
| |_| | (_| | | (_| |>  <| |_| | |  _| | | (_| \__ \ | | |  __/ |
 \____|\__,_|_|\__,_/_/\_\\__, | |_|   |_|\__,_|___/_| |_|\___|_|
                          |___/

                          {version}
        """
        )

    def load_settings(self):
        self.settings = {}
        if os.path.exists(settings_file):
            with open(settings_file, "r") as file:
                self.settings = json.load(file)

    def save_settings(self):
        with open(settings_file, "w") as file:
            json.dump(self.settings, file)

    def flash(self):
        if self.flashtool == "thor":
            auto = self.settings.get("auto_partitions", False)
            files = []
            paths = {}
            for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
                entry = getattr(self, f"{slot}_entry")
                if entry.get_text():
                    file_path = entry.get_text()
                    file = os.path.basename(file_path)
                    files.append(file)
                    paths[slot] = os.path.dirname(entry.get_text())
            if len(paths) == 0:
                print(self.strings["no_files_selected2"])
                self.error_dialog("Invalid files", self.strings["no_files_selected2"])
            elif len(set(paths.values())) > 1:
                print("The files NEED to be in the same dir...")
                self.error_dialog("Invalid files", self.strings["invalid_files"])
            else:
                base_dir = list(paths.values())[0]
                self.thor_select_partitions(files, base_dir, auto)

        elif self.flashtool == "odin4":
            args = []
            for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
                slot_to_arg = {
                    "BL": "-b",
                    "AP": "-a",
                    "CP": "-c",
                    "CSC": "-s",
                    "USERDATA": "-u",
                }
                entry = getattr(self, f"{slot}_entry")
                file = entry.get_text()
                if file:
                    arg = slot_to_arg[slot]
                    file_arg = f"{arg} {file}"
                    args.append(file_arg)
            if len(args) == 0:
                print(self.strings["no_files_selected2"])
                self.error_dialog("Invalid files", self.strings["no_files_selected2"])
            else:
                device = self.odin4_select_device()
                if not device:
                    message = "No devices were found - First connect a device that's in Download Mode"
                    print(message)
                    self.error_dialog(
                        "No devices were found",
                        "First connect a device that's in Download Mode",
                    )
                else:
                    args.insert(0, f"-d {device}")
                    command = " ".join(["flash"] + args)
                    print(f"Running: {command}")
                    self.send_cmd(command)

    def shorten_string(self, string, length):
        current_length = len(string)
        if current_length > length:
            new_string = string[: length - 3] + "..."
        else:
            new_string = string
        return new_string

    def thor_select_partitions(self, files, base_dir, auto):
        self.retry_partition = False
        run = 0

        def send_selected_partitions(selected_partitions):
            print(f"selected_partitions: {selected_partitions}")
            n_partitions = len(selected_partitions)
            for i, partition in enumerate(selected_partitions):
                if partition == True:
                    print('SENDING: "Space"')
                    self.send_cmd("\x20", False)
                    time.sleep(0.05)
                # If it's the last partition displayed,
                # we don't need to send a down arrow.
                if not i == n_partitions:
                    print('SENDING: "Down Arrow"')
                    self.send_cmd("\x1b[B", False)
                    time.sleep(0.05)

        def display_partitions(partitions, file):
            selected_partitions = []

            def partition_toggled(button, row):
                if button.get_active():
                    selected_partitions[row] = True
                else:
                    selected_partitions[row] = False

            def return_selected_partitions(cancel=False):
                window.destroy()
                if not cancel:
                    send_selected_partitions(selected_partitions)
                print('SENDING: "Enter"')
                self.send_cmd("\n", False)
                time.sleep(0.3)
                GLib.idle_add(select)

            window, grid = self.create_window("Select Partitions")
            window.connect(
                "close_request", lambda _: return_selected_partitions(cancel=True)
            )
            row = 0
            self.create_label(
                text="Select what partitions to flash from:",
                grid=grid,
                row=row,
                padding=(5, 5, 5, 5),
                align=Gtk.Align.CENTER,
                width=2,
            )
            row += 1
            self.create_label(
                text=file,
                grid=grid,
                row=row,
                padding=(5, 5, 0, 5),
                align=Gtk.Align.CENTER,
                width=2,
            )
            row += 1
            for i, partition in enumerate(partitions):
                btn = self.create_checkbutton(
                    partition, 0, row, grid, padding=(5, 5, 0, 0), width=2
                )
                btn.connect(
                    "toggled",
                    lambda _, btn=btn, row=i: partition_toggled(btn, row),
                )
                selected_partitions.append(False)
                row += 1
            self.create_button(
                "Cancel",
                0,
                row,
                grid,
                lambda _: return_selected_partitions(cancel=True),
                padding=(5, 10, 5, 5),
            )
            self.create_button(
                "OK",
                1,
                row,
                grid,
                lambda _: return_selected_partitions(),
                padding=(0, 5, 5, 5),
            )
            window.present()

        def select():
            nonlocal run
            run += 1
            print(f"RUN {run}")
            end = None
            command = None
            wait = True
            if self.retry_partition:
                wait = False
                self.retry_partition = False
            # If this is the first run, run the flashTar command.
            if run == 1:
                end = "(Press <space> to select, <enter> to accept)"
                command = f"flashTar {base_dir}"
                print(f'RUNNING: "{command}"')
                self.send_cmd(command)
            # Get the output.
            output = self.get_output(
                command=None,
                start="shell>*",
                end=end,
                wait=wait,
            )
            # print(f"output: {output}")
            if not output[0] or output[0] == "Timeout":
                print("No output was found.")
                return GLib.SOURCE_CONTINUE
            else:
                # If the output is for selecting partitions and is complete.
                if output[0] == "Choose what partitions to flash from":
                    print("Found start of partitions.")
                    if output[-1] == "(Press <space> to select, <enter> to accept)":
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
                                self.send_cmd("\n", False)
                                time.sleep(0.3)
                                return GLib.SOURCE_CONTINUE
                            else:
                                print(f'Select what partitions to flash from: "{file}"')
                                shortened_file = self.shorten_string(file, 46)
                                display_partitions(partitions, shortened_file)
                        # If the file wasn't selected by the user.
                        else:
                            print("File wasn't selected.")
                            print('SENDING: "Enter"')
                            self.send_cmd("\n", False)
                            time.sleep(0.3)
                            return GLib.SOURCE_CONTINUE
                    else:
                        self.retry_partition = True
                        return GLib.SOURCE_CONTINUE
                elif (
                    output[-1]
                    == "Are you absolutely sure you want to flash those? [y/n] (n):"
                ):
                    print("Verifying flash.")
                    n_partitions = re.search(r"(\d+) partitions", output[0])
                    partition_list = []
                    for line in output[1:-1]:
                        partition_list.append(line)
                    self.verify_flash(n_partitions.group(1), partition_list, auto)
                    return GLib.SOURCE_REMOVE
                else:
                    print("Unknown output.")
                    return GLib.SOURCE_REMOVE

        GLib.idle_add(select)

    def create_window(self, title):
        grid = Gtk.Grid()
        window = Gtk.Window()
        window.set_modal(True)
        window.set_title(title)
        window.set_child(grid)
        window.set_transient_for(self)
        return window, grid

    def scan_output(self, vte):
        if self.flashtool == "thor":
            strings_to_commands = {
                "[sudo] password for": [
                    lambda: self.set_password_entry(self.command_entry, True)
                ],
                "Welcome to Thor Shell": [
                    lambda: self.set_password_entry(self.command_entry, False),
                    lambda: self.set_widget_state(self.connect_button, state=True),
                ],
                "Successfully connected to the device!": [
                    lambda: print("Successfully connected to the device!"),
                    lambda: self.set_widget_state(self.start_odin_button, state=True),
                    lambda: self.connect_button.set_label("Disconnect"),
                    lambda: self.change_button_command(
                        self.connect_button, lambda _: self.send_cmd("disconnect")
                    ),
                ],
                "Successfully disconnected the device!": [
                    lambda: print("Successfully disconnected the device!"),
                    lambda: self.set_widget_state(self.start_odin_button, state=False),
                    lambda: self.connect_button.set_label("Connect"),
                    lambda: self.change_button_command(
                        self.connect_button, lambda _: self.send_cmd_entry("connect")
                    ),
                ],
                "Successfully began an Odin session!": [
                    lambda: print("Successfully began an Odin session!"),
                    # NOTE: Why do we need to enable the start_odin_button here?
                    # It's supposed to be enabled above ^.
                    lambda: self.set_widget_state(
                        self.start_odin_button, self.flash_button, state=True
                    ),
                    lambda: self.start_odin_button.set_label("End Odin Session"),
                    lambda: self.change_button_command(
                        self.start_odin_button, lambda _: self.end_odin()
                    ),
                ],
                "Successfully ended an Odin session!": [
                    lambda: print("Successfully ended an Odin session!"),
                    lambda: self.set_widget_state(self.flash_button, state=False),
                    lambda: self.start_odin_button.set_label("Start Odin Session"),
                    lambda: self.change_button_command(
                        self.start_odin_button, lambda _: self.start_odin_session()
                    ),
                    # We disable it because with Thor:
                    # "You can't reuse the same USB connection after you close an
                    # Odin session, and you can't re-connect the device.
                    # You have to reboot each time."
                    lambda: self.set_widget_state(self.start_odin_button, state=False),
                ],
            }
        elif self.flashtool == "odin4":
            strings_to_commands = {
                "Welcome to Interactive Odin4!": [
                    lambda: self.set_widget_state(
                        self.help_button,
                        self.list_button,
                        self.flash_button,
                        state=True,
                    )
                ]
            }
        elif self.flashtool == "pythor":
            strings_to_commands = {
                ">>": [lambda: self.set_widget_state(self.connect_button, state=True)]
            }
        # This is a pretty bad way to do this.
        # 10000 should be replaced with the actual value, But it works.
        term_text = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, 10000)[0]
        # TODO: Look into why this is needed, obviously it's only for Thor.
        if term_text.strip().rsplit("shell>")[-1].strip() == "":
            try:
                term_text = term_text.strip().rsplit("shell>")[-2].strip()
            except:
                term_text = term_text.strip().rsplit("shell>")[-1].strip()
        else:
            term_text = term_text.strip().rsplit("shell>")[-1].strip()
        if term_text != self.last_text:
            for string, commands in strings_to_commands.items():
                if string in term_text and string not in self.last_text:
                    for command in commands:
                        command()

            self.last_text = term_text

    def remove_blank_lines(self, string):
        lines = string.splitlines()
        filtered_lines = [line for line in lines if line.strip()]
        new_string = "\n".join(filtered_lines)
        return new_string

    def check_output(self, vte, command, result, start, end, wait, add_enter, timeout):
        # This is a pretty bad way to do this.
        # 10000 should be replaced with the actual value, But it works.
        old_output = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, 10000)[0]
        old_output = self.remove_blank_lines(old_output)
        if command:
            self.send_cmd(command, add_enter)

        cycles = 0
        start_time = time.time()
        if start:
            start = start.strip()
        # If start isn't specified, use the command as start.
        else:
            if command:
                start = self.prompt + command
            else:
                print(
                    "get_output requires that if the start arg isn't"
                    "specified, the command arg must be."
                )
        if end:
            end = end.strip()

        def check():
            nonlocal cycles
            # This is a pretty bad way to do this.
            # 10000 should be replaced with the actual value, But it works.
            current_output = vte.get_text_range_format(
                Vte.Format(1), 0, 0, 10000, 10000
            )[0]
            current_output = self.remove_blank_lines(current_output)
            # If the output has changed or wait is False.
            if current_output != old_output or wait == False:
                lines = current_output.splitlines()
                new_lines = []
                start_index = -1
                # Find the last occurence of start.
                for i in range(len(lines) - 1, -1, -1):
                    start_match = re.search(start, lines[i])
                    # if lines[i].startswith(start):
                    if start_match:
                        start_index = i
                        break
                # Get all the lines after start and up to end, if it's
                # found, otherwise get everything after start.
                if start_index != -1:
                    new_lines = lines[start_index + 1 :]
                end_index = None
                if end:
                    for i, line in enumerate(new_lines):
                        line = line.strip()
                        end_match = re.search(end, line)
                        # if line.strip() == end:
                        if end_match:
                            end_index = i
                            break
                # If end was found or was None, return the result,
                # otherwise continue.
                if end_index != None or end == None:
                    if end != None:
                        new_lines = new_lines[:end_index]
                    cleaned_new_output = "\n".join(new_lines)
                    # Check if cleaned_new_output is empty or contains only whitespace.
                    if cleaned_new_output.strip():
                        new_lines = cleaned_new_output.split("\n")
                        for line in new_lines:
                            line = line.strip()
                            result.append(line)
                        # print(f'Output: {result}')
                    else:
                        result.append(None)
                        # print("The command finished with no output.")
                    return GLib.SOURCE_REMOVE
            if time.time() - start_time > timeout:
                result.append("Timeout")
                # print("Timeout reached!")
                return GLib.SOURCE_REMOVE
            cycles += 1
            return GLib.SOURCE_CONTINUE

        GLib.idle_add(check)

    def get_output(
        self,
        command=None,
        start=None,
        end=">>",
        wait=True,
        add_enter=True,
        timeout=2,
    ):
        """
        The command and start args are optional, but if the command arg is not
        specified the start arg has to be.
        If the start arg is not specified start is set to the command.
        If a command is given, it runs the command.
        The optional add_enter arg determines whether a "\n" is appended to
        the command, if a command was specified. By default it is True.
        It returns the output after start, up to the line matching the optional
        end arg, which by default is ">>".
        If end is specified as None, all of the new output will be returned.
        By default, it won't check for start anything until the output changes.
        If you don't want it to wait for the output to change,
        set the optional wait arg to False.
        It returns None if the command finished with no output.
        It returns "Timeout" if the command doesn't finish within the number of
        seconds specified by the optional timeout arg, which by default is 2.
        """
        result = []
        self.check_output(
            self.vte_term,
            command,
            result,
            start,
            end,
            wait,
            add_enter,
            timeout,
        )
        while not result:
            GLib.main_context_default().iteration(True)
        return result

    def thor_select_device(self):
        def set_selected_device(btn, device_index):
            if btn.get_active:
                self.device_index = device_index

        def send_selected_device(cancel=False):
            if cancel:
                times = len(devices)
            else:
                times = self.device_index - 1
            for _ in range(times):
                # Send "Down Arrow"
                self.send_cmd("\x1b[B", False)
            # Send "Enter"
            self.send_cmd("\n", False)

        devices = self.get_output(
            "connect", "Choose a device to connect to:", "Cancel operation"
        )
        # TODO: I haven't actually tested this with two devices connected.
        # devices = "/dev/device1\n/dev/device2"
        if not devices[0] or devices[0] == "Timeout":
            print("No devices were found!")
        else:
            if len(devices) == 1:
                self.device_index = 1
                send_selected_device()
            else:
                window, grid = self.create_window(self.strings["connect_device"])
                self.create_label(text=self.strings["choose_a_device"], grid=grid)
                group = None
                row = 1
                for index, device in enumerate(devices):
                    checkbutton = self.create_checkbutton(device.strip(), 0, row, grid)
                    if index == 0:
                        group = checkbutton
                    else:
                        checkbutton.set_group(group)
                    checkbutton.connect("toggled", set_selected_device, row)
                    row = row + 1
                self.create_button(
                    "Cancel",
                    1,
                    row,
                    grid,
                    lambda _: (
                        send_selected_device(cancel=True),
                        window.destroy(),
                    ),
                )
                self.create_button(
                    "OK",
                    2,
                    row,
                    grid,
                    lambda _: (send_selected_device(), window.destroy()),
                )
                window.present()

    def odin4_select_device(self):
        devices = self.get_output("list")
        # TODO: I haven't actually tested this with two devices connected.
        # devices = "/dev/device1\n/dev/device2"
        if not devices[0] or devices[0] == "Timeout":
            return None
        else:
            if len(devices) == 1:
                return devices[0]
            else:
                self.device = devices[0]

                def set_selected_device(btn, device):
                    if btn.get_active:
                        self.device = device

                def return_selected_device(cancel=False):
                    if cancel or not device:
                        return None
                    else:
                        print(f"Selected device: {self.device}")
                        return self.device

                window, grid = self.create_window(self.strings["connect_device"])
                self.create_label(text=self.strings["choose_a_device"], grid=grid)
                group = None
                row = 1
                for index, device in enumerate(devices):
                    checkbutton = self.create_checkbutton(device, 0, row, grid)
                    if index == 0:
                        group = checkbutton
                        checkbutton.set_active(True)
                    else:
                        checkbutton.set_group(group)
                    checkbutton.connect("toggled", set_selected_device, device)
                    row = row + 1
                self.create_button(
                    "Cancel",
                    1,
                    row,
                    grid,
                    lambda _: (return_selected_device(cancel=True), window.destroy()),
                )
                self.create_button(
                    "OK",
                    2,
                    row,
                    grid,
                    lambda _: (return_selected_device(), window.destroy()),
                )
                window.present()

    # TODO: Display the partitions that are to be flashed.
    def verify_flash(self, n, partitions, auto):
        window, grid = self.create_window(self.strings["verify_flash"])
        row = 1
        if auto:
            noun = "The computer"
        else:
            noun = "You"
        self.create_label(
            text=f"{noun} selected {n} partitions to flash.",
            grid=grid,
            row=row,
            padding=(5, 5, 5, 5),
            align=Gtk.Align.CENTER,
            width=2,
        )
        row += 1
        self.create_label(
            text="Are you absolutely sure you want to flash them?",
            grid=grid,
            row=row,
            padding=(5, 5, 0, 0),
            align=Gtk.Align.CENTER,
            width=2,
        )
        row += 1
        self.create_button(
            "Yes",
            0,
            row,
            grid,
            lambda _: (self.send_cmd("y"), window.destroy()),
            padding=(5, 10, 5, 5),
        )
        self.create_button(
            "No",
            1,
            row,
            grid,
            lambda _: (self.send_cmd("n"), window.destroy()),
            padding=(0, 5, 5, 5),
        )
        window.present()

    def option_changed(self, button):
        if self.flashtool == "thor":
            convert = {
                "t_flash": "tflash",
                "efs_clear": "efsclear",
                "reset_flash_count": "resetfc",
                "bootloader_update": "blupdate",
            }

            option = button.get_label().lower().replace(" ", "_")
            value = button.get_active()

            print(f"{option}: {value}")
            setattr(self, option, value)

            option = convert[option]
            self.send_cmd(f"options {option} {value}")

    def switch_row_changed(self, switch, state, setting):
        active = switch.get_active()
        self.set_setting(setting, active)

    def set_setting(self, setting, value):
        if setting == "theme":
            self.set_theme(value)
        self.settings[setting] = value
        print(f"{setting} set to: '{value}'")
        self.save_settings()

    # TODO: There has to be a better way to handle the terminal's colors...
    def set_theme(self, theme):
        if theme == "system":
            color_scheme = Adw.ColorScheme.PREFER_LIGHT
        elif theme == "light":
            color_scheme = Adw.ColorScheme.FORCE_LIGHT
        elif theme == "dark":
            color_scheme = Adw.ColorScheme.FORCE_DARK
        else:
            print(
                "Error in set_theme function: theme argument can be either "
                f'"system", "light", or "dark". Not "{theme}".'
            )
            return
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(color_scheme)
        if Adw.StyleManager.get_dark(style_manager):
            terminal_foreground = "#ffffff"
            terminal_background = "#242424"
        else:
            terminal_foreground = "#000000"
            terminal_background = "#fafafa"

        foreground = Gdk.RGBA()
        foreground.parse(terminal_foreground)
        background = Gdk.RGBA()
        background.parse(terminal_background)
        self.vte_term.set_colors(foreground, background, None)

    def error_dialog(self, title, message):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons(["OK"])
        dialog.show(self)

    def connect_device(self):
        self.send_cmd("connect")

    def start_odin_session(self):
        if self.flashtool == "thor":
            self.send_cmd("begin odin")
        elif self.flashtool == "pythor":
            self.send_cmd("begin")

    def end_odin(self):
        self.send_cmd("end")

    def on_command_enter(self):
        text = self.command_entry.get_text()
        self.command_entry.set_text("")
        self.send_cmd_entry(text)

    def set_widget_state(self, *args, state=True):
        for widget in args:
            widget.set_sensitive(state)

    def toggle_entry_visibility(self, entry, icon_pos):
        visible = entry.get_visibility()
        if visible:
            icon = "view-reveal-symbolic"
        else:
            icon = "view-conceal-symbolic"
            entry.set_visibility(not visible)
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition(icon_pos), icon)

    def set_password_entry(self, entry, state):
        if state:
            icon = "view-reveal-symbolic"
        else:
            icon = "view-conceal-symbolic"
        entry.set_visibility(not state)
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition(1), icon)
        self.command_entry.connect("icon-press", self.toggle_entry_visibility)

    def send_cmd(self, cmd, add_enter=True):
        if add_enter == True:
            cmd = cmd + "\n"
        self.vte_term.feed_child(cmd.encode("utf-8"))

    # Like send_cmd, but checks for "special" commands that have a function.
    # As the name suggests, it is used for the command entry,
    # but it can also be used by buttons, such as the connect button.
    def send_cmd_entry(self, cmd):
        cmd = cmd.strip() + "\n"
        special = False
        if self.flashtool == "thor":
            if cmd == "connect\n":
                special = True
                self.thor_select_device()
            if cmd == "flashTar\n":
                special = True
                self.flash()
        if not special:
            self.vte_term.feed_child(cmd.encode("utf-8"))

    def open_file(self, partition):
        def file_dialog_callback(obj, result):
            try:
                file = obj.open_finish(result)
                if file:
                    file_path = file.get_path()
                    print(f"Selected file: {file_path}")
                    entry = getattr(self, f"{partition}_entry")
                    entry.set_text(file_path)
            except GLib.Error as e:
                # If the user cancelled, pass.
                if e.code == 2:
                    pass
                else:
                    print(f"Error: {e}")

        file_dialog = Gtk.FileDialog(title=f"Select a {partition} file")
        odin_filter = Gtk.FileFilter()
        odin_filter.set_name("Odin files")
        odin_filter.add_mime_type("application/x-tar")
        odin_filter.add_pattern("*.tar.md5")
        odin_filter.add_pattern("*.tar")
        filter_list = Gio.ListStore.new(Gtk.FileFilter)
        filter_list.append(odin_filter)
        file_dialog.set_filters(filter_list)
        file_dialog.open(self, None, file_dialog_callback)

    def create_label(
        self,
        text,
        grid,
        column=0,
        row=0,
        padding=(0, 0, 0, 0),
        font=("monospace", 11),
        align=Gtk.Align.START,
        width=1,
        height=1,
    ):
        label = Gtk.Label()
        self.set_padding(label, padding)
        label.set_markup(f'<span font_desc="{font[0]} {font[1]}">{text}</span>')
        label.set_halign(align)
        grid.attach(label, column, row, width, height)
        return label

    def create_button(
        self, label, column, row, grid, command, padding=(0, 0, 0, 0), width=1, height=1
    ):
        button = Gtk.Button(label=label)
        self.set_padding(button, padding)
        button.signal_id = button.connect("clicked", command)
        grid.attach(button, column, row, width, height)
        return button

    def create_preferences(self, main_preferences_list, grid):
        preferences_page = Adw.PreferencesPage.new()
        for section in main_preferences_list:
            preferences_group = Adw.PreferencesGroup.new()
            preferences_page.add(preferences_group)
            group_title = section["title"]
            settings = section["settings"]
            if group_title:
                preferences_group.set_title(group_title)
            for setting_list in settings:
                setting_type = setting_list[0]
                title = setting_list[1]
                subtitle = setting_list[2]
                setting = setting_list[3]
                if setting_type == "switch":
                    default_value = setting_list[3]
                    switch_row = Adw.SwitchRow.new()
                    switch_row.set_title(title)
                    if subtitle:
                        switch_row.set_subtitle(subtitle)
                    switch_row.set_active(self.settings.get(setting, default_value))
                    switch_row.connect(
                        "notify::active", self.switch_row_changed, setting
                    )
                    preferences_group.add(switch_row)

                elif setting_type == "combo":
                    default_value = setting_list[5]
                    # Gets the current_value of setting.
                    current_value = self.settings.get(setting, default_value)
                    # Create the combo row.
                    combo_row = Adw.ComboRow(title=title)
                    if subtitle:
                        combo_row.set_subtitle(subtitle)
                    # Split the value_names and values into seperate lists.
                    value_name_list = Gtk.StringList.new()
                    value_list = []
                    value_name = True
                    for item in setting_list[4:]:
                        if value_name:
                            value_name_list.append(item)
                            value_name = False
                        else:
                            value_list.append(item)
                            value_name = True
                    combo_row.set_model(value_name_list)
                    # Get the index of the current value.
                    current_value_index = value_list.index(current_value)
                    # Set the currently selected item.
                    combo_row.set_selected(current_value_index)
                    # Connect the notify::selected signal.
                    combo_row.connect(
                        "notify::selected",
                        lambda row, _, ls=value_list, sett=setting: self.on_combo_row_changed(
                            row, ls, sett
                        ),
                    )
                    preferences_group.add(combo_row)
        grid.attach(preferences_page, 0, 0, 1, 1)

    def on_combo_row_changed(self, combo_row, value_list, setting):
        new_value_index = combo_row.get_selected()
        new_value = value_list[new_value_index]
        self.set_setting(setting, new_value)

    def change_button_command(self, button, new_command):
        button.disconnect(button.signal_id)
        button.signal_id = button.connect("clicked", new_command)

    def create_entry(
        self, column, row, grid, padding=(0, 0, 0, 0), width=1, height=1, expand=False
    ):
        entry = Gtk.Entry()
        self.set_padding(entry, padding)
        if expand:
            entry.set_hexpand(True)
            entry.set_halign(Gtk.Align.FILL)
        grid.attach(entry, column, row, width, height)
        return entry

    def create_checkbutton(
        self,
        label,
        column,
        row,
        grid,
        padding=(0, 0, 0, 0),
        align=Gtk.Align.START,
        width=1,
        height=1,
    ):
        check_button = Gtk.CheckButton(label=label)
        self.set_padding(check_button, padding)
        check_button.set_halign(align)
        grid.attach(check_button, column, row, width, height)
        return check_button

    def create_radiobuttons(
        self,
        name,
        setting,
        default_value,
        radiobuttons,
        column,
        row,
        grid,
        padding=(0, 0, 0, 0),
        radio_padding=(0, 0, 0, 0),
        font=("monospace", 11),
    ):
        current_value = self.settings.get(setting, default_value)
        # Create the label
        self.create_label(name, grid, column, row, padding, font)
        # Create the radiobuttons
        radiobutton_group = None
        for i, item in enumerate(radiobuttons):
            text = item["text"]
            value = item["value"]
            radiobutton = self.create_checkbutton(
                text, 0, row + i + 1, grid, radio_padding
            )
            if current_value == value:
                radiobutton.set_active(True)
            if radiobutton_group is None:
                radiobutton_group = radiobutton
            else:
                radiobutton.set_group(radiobutton_group)
            handler = lambda widget, value=value: self.on_radiobutton_toggled(
                widget, setting, value
            )
            radiobutton.connect("toggled", handler)

    def create_toggle_switch(
        self, label, column, row, grid, width=1, height=1, padding=(10, 0, 0, 0)
    ):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        toggle_switch = Gtk.Switch()
        toggle_label = Gtk.Label(label=label)
        box.append(toggle_switch)
        box.append(toggle_label)
        box.set_spacing(10)
        self.set_padding(box, padding)
        grid.attach(box, column, row, width, height)
        return toggle_switch

    def set_padding(self, widget, padding):
        widget.set_margin_start(padding[0])
        widget.set_margin_end(padding[1])
        widget.set_margin_top(padding[2])
        widget.set_margin_bottom(padding[3])

    def about_window(self, *_):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Galaxy Flasher")
        dialog.set_version(version)
        dialog.set_developer_name("ethical_haquer")
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        credits = [
            {"name": "justaCasualCoder", "github_profile": "justaCasualCoder"},
            {"name": "ethical_haquer", "github_profile": "ethical-haquer"},
            {"name": "TheAirBlow", "github_profile": "TheAirBlow"},
        ]
        for credit in credits:
            name = credit["name"]
            github_profile = credit["github_profile"]
            dialog.add_credit_section(
                name, [f"Github Profile https://github.com/{github_profile}"]
            )
        dialog.set_website("https://github.com/ethical-haquer/Galaxy-Flasher")
        dialog.set_issue_url("https://github.com/ethical-haquer/Galaxy-Flasher/issues")
        dialog.set_visible(True)


class GalaxyFlasher(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_default_size(950, 400)
        self.win.present()


app = GalaxyFlasher(application_id="com.ethicalhaquer.galaxyflasher")
app.run(sys.argv)
