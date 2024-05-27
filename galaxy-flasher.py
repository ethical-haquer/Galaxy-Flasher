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
import sys
import tarfile
import time

import gi
import xdg

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Vte

locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = "_"
lang = locale.split(seperator, 1)[0]

version = "Alpha v0.5.0"
config_dir = xdg.XDG_CONFIG_HOME
app_dir = "galaxy-flasher"
app_config_dir = os.path.join(config_dir, app_dir)
if not os.path.exists(app_config_dir):
    os.makedirs(app_config_dir)
settings_file = os.path.join(app_config_dir, "settings.json")
locale_file = f"locales/{lang}.json"
cwd = os.getcwd()
arch = platform.architecture()[0][:2]
system = platform.system().lower()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.last_text = ""
        super().__init__(*args, **kwargs)
        # Load strings
        # TODO: Remove unneeded strings from en.json
        with open(locale_file) as json_string:
            self.strings = json.load(json_string)
        # Load settings
        self.load_settings()
        # Set the flash-tool path
        self.flashtool = self.settings.get("flash_tool") or "thor"
        if self.flashtool == "thor":
            flashtool_path = (
                f"{cwd}/flash-tools/thor/{system}/x{arch}/TheAirBlow.Thor.Shell"
            )
        elif self.flashtool == "odin4":
            flashtool_path = f"{cwd}/odin4-wrapper.sh"
        elif self.flashtool == "pythor":
            flashtool_path = f"{cwd}/flash-tools/pythor/{system}/pythor_cli"
        # Only use the sudo setting for Thor.
        if self.settings.get("sudo", False) and self.settings["flash_tool"] == "thor":
            flashtool_exec = ["sudo", flashtool_path]
        else:
            flashtool_exec = [flashtool_path]
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
        # Check if flash-tool executable exists
        if not os.path.isfile(flashtool_path):
            print(f"Error: File {flashtool_path} not found")
            self.realize_id = self.connect(
                "show", lambda _: self.flashtool_not_found_dialog(flashtool_path)
            )
        # Create flash-tool output box
        self.vte_term = Vte.Terminal()
        # Set terminal colors
        foreground = Gdk.RGBA()
        foreground.parse("#ffffff")
        background = Gdk.RGBA()
        background.parse("#242424")
        self.vte_term.set_colors(foreground, background, None)
        self.vte_term.spawn_async(
            Vte.PtyFlags.DEFAULT,  # Pty Flags
            cwd,  # Working DIR
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
        # Create connect, start_odin, and flash buttons
        if self.flashtool == "thor":
            buttons = [
                {
                    "name": "connect_button",
                    "text": self.strings["connect"],
                    "command": lambda _: self.connect_device(),
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
        row = 0
        if self.flashtool == "thor":
            self.options = [
                {"option": "T Flash"},
                {"option": "EFS Clear"},
                {"option": "Bootloader Update"},
                {"option": "Reset Flash Count"},
            ]
            for item in self.options:
                option = item["option"]
                check_button = self.create_checkbutton(
                    option, 0, row, self.options_grid, (6, 0, 0, 0)
                )
                check_button.connect("toggled", self.option_changed)
                row += 1
        elif self.flashtool == "odin4":
            row = 0
            self.create_label(
                'The "-V" option will be added once I know what it does.',
                0,
                row,
                self.options_grid,
                (10, 0, 0, 0),
            )
        elif self.flashtool == "pythor":
            self.create_label(
                "Currently, PyThor has no options.",
                0,
                0,
                self.options_grid,
                (10, 0, 0, 0),
            )
        # Create place-holder label for Pit tab.
        self.create_label(
            f"{self.strings['just_a_test']}\n\n{self.strings['pull_requests_welcome']}",
            0,
            0,
            self.pit_grid,
            (10, 0, 0, 0),
        )
        # Create the Settings tab widgets.
        row = 0
        radiobuttons = [
            {"text": "Thor", "value": "thor"},
            {"text": "Odin4", "value": "odin4"},
            {"text": "PyThor (in development)", "value": "pythor"},
        ]
        self.create_radiobuttons(
            name="Flash Tool:",
            setting="flash_tool",
            default_value="thor",
            radiobuttons=radiobuttons,
            column=0,
            row=row,
            grid=self.settings_grid,
            padding=(10, 0, 0, 0),
            radio_padding=(16, 0, 0, 0),
        )
        row = row + len(radiobuttons) + 1
        self.options = [
            {"label": self.strings["run_thor_sudo"], "setting": "sudo"},
        ]
        for item in self.options:
            text = item["label"]
            setting = item["setting"]
            toggle = self.create_toggle_switch(text, 0, row, self.settings_grid)
            toggle.set_active(self.settings.get(setting, False))
            toggle.connect("state-set", self.toggle_changed, setting)
            active = toggle.get_active()
            self.settings[setting] = active
        # Scan the output whenever it changes
        self.vte_term.connect("contents-changed", self.scan_output)
        # Print out the ASCII text "Galaxy Flasher", created with figlet.
        # The triple back-slash "\\\" is needed to escape the double back-slash "\\".
        print(
            f"""
  ____       _                    _____ _           _
 / ___| __ _| | __ ___  ___   _  |  ___| | __ _ ___| |__   ___ _ __ 
| |  _ / _` | |/ _` \ \/ / | | | | |_  | |/ _` / __| '_ \ / _ \ '__|
| |_| | (_| | | (_| |>  <| |_| | |  _| | | (_| \__ \ | | |  __/ |
 \____|\__,_|_|\__,_/_/\_\\\__, | |_|   |_|\__,_|___/_| |_|\___|_|
                          |___/

                          {version}
        """
        )

    def flashtool_not_found_dialog(self, flashtool_path):
        self.disconnect(self.realize_id)
        self.error_dialog(
            self.strings["file_not_found2"].format(file=flashtool_path), "__init__"
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
        # This doesn't seem to work as expected.
        # It makes sure all of the selected files are in the same folder,
        # but it doesn't take into account that there may also be other files.
        if self.flashtool == "thor":

            def toggled_callback(button):
                if button.get_active():
                    self.selected_buttons[btn_array[button] - 1][0] = True
                else:
                    self.selected_buttons[btn_array[button] - 1][0] = False

            file_names = []
            self.selected_buttons = []
            btn_array = {}
            window, grid = self.dialog("Select Partitions")
            self.create_label("Select the partitions to flash", 0, 0, grid)
            row = 1
            paths = {}
            for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
                entry = getattr(self, f"{slot}_entry")
                if entry.get_text():
                    print(f"Flashing {entry.get_text()} to {slot}")
                    paths[slot] = os.path.dirname(entry.get_text())
            if len(paths) == 0:
                print(self.strings["no_files_selected2"])
                self.error_dialog(self.strings["no_files_selected2"], "flash")
            elif len(set(paths.values())) > 1:
                print("The files NEED to be in the same dir...")
                self.error_dialog(self.strings["invalid_files"], "flash")
            else:
                base_dir = list(paths.values())[0]
                self.send_cmd(f"flashTar {base_dir}")
                for file_path in os.listdir(base_dir):
                    print(f"file_path is: {file_path}")
                    if file_path.endswith(".md5") or file_path.endswith(".tar"):
                        file_path = os.path.join(base_dir, file_path)
                        with tarfile.open(file_path) as tar_file:
                            for member in tar_file.getmembers():
                                self.selected_buttons.append([False, file_path])
                                split = member.name.split(".")
                                # Skip Pit file
                                if split[1] != "pit":
                                    name = split[0].upper()
                                    file_names.append(name)
                                    btn = self.create_checkbutton(name, 0, row, grid)
                                    btn.connect("toggled", toggled_callback)
                                    btn_array[btn] = row
                                    row += 1
                self.create_button("Cancel", 1, row, grid, lambda _: window.destroy())
                self.create_button(
                    "OK",
                    2,
                    row,
                    grid,
                    lambda _: (self.send_selected_partitions(), window.destroy()),
                )
                window.present()

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
                self.error_dialog(self.strings["no_files_selected2"], "flash")
            else:
                device = self.odin4_select_device()
                if not device:
                    message = "No devices were found - First connect a device that's in Download Mode"
                    print(message)
                    self.error_dialog(message, "flash")
                else:
                    args.insert(0, f"-d {device}")
                    command = " ".join(["flash"] + args)
                    print(f"Running: {command}")
                    self.send_cmd(command)

    def send_selected_partitions(self):
        last_file = ""
        for selected, file_path in self.selected_buttons:
            if last_file and last_file != file_path:
                self.send_cmd("\n", False)
            if selected:
                self.send_cmd("\x20", False)
            self.send_cmd("\x1b[B", False)
            last_file = file_path
        self.send_cmd("\n", False)

    def dialog(self, title):
        # Create grid
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
                        self.connect_button, lambda _: self.send_cmd("connect")
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
                "Are you absolutely sure you want to flash those?": [
                    lambda: self.verify_flash()
                ],
                "Choose a device to connect to:": [
                    lambda: self.select_device(term_text)
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

    def select_device(self, text):
        def set_selected_device(btn, row):
            if btn.get_active:
                self.device_index = row

        self.devices = (
            text.split("Choose a device to connect to:")[1]
            .split("Cancel operation")[0]
            .strip()
            .strip("> ")
            .splitlines()
        )
        window, grid = self.dialog(self.strings["connect_device"])
        self.create_label(self.strings["choose_a_device"], 0, 0, grid)
        group = None
        row = 1
        for index, item in enumerate(self.devices):
            checkbutton = self.create_checkbutton(item.strip(), 0, row, grid)
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
            lambda _: (self.send_selected_device(cancel=True), window.destroy()),
        )
        self.create_button(
            "OK",
            2,
            row,
            grid,
            lambda _: (self.send_selected_device(), window.destroy()),
        )
        window.present()

    def send_selected_device(self, cancel=False):
        if cancel:
            times = len(self.devices)
        else:
            times = self.device_index - 1
        for _ in range(times):
            self.send_cmd("\x1b[B", False)
        self.send_cmd("\n", False)

    def verify_flash(self):
        window, grid = self.dialog(self.strings["verify_flash"])
        self.create_label(self.strings["are_you_sure"], 0, 0, grid)
        buttons = [
            {
                "text": self.strings["yes"],
                "command": lambda _: (self.send_cmd("y"), window.destroy()),
            },
            {
                "text": self.strings["no"],
                "command": lambda _: (self.send_cmd("n"), window.destroy()),
            },
        ]
        column = 1
        for btn in buttons:
            self.create_button(btn["text"], column, 1, grid, btn["command"])
            column += 1
        """
        self.create_button(
            self.strings["yes"],
            1,
            1,
            grid,
            lambda _: (self.send_cmd("y"), window.destroy()),
        ).set_margin_end(5)
        self.create_button(
            self.strings["no"],
            2,
            1,
            grid,
            lambda _: (self.send_cmd("n"), window.destroy()),
        )
        """
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

    def remove_blank_lines(self, string):
        lines = string.splitlines()
        filtered_lines = [line for line in lines if line.strip()]
        new_string = "\n".join(filtered_lines)
        return new_string

    def check_command_output(self, vte_term, command, result, timeout):
        old_output = vte_term.get_text_format(Vte.Format(1))
        old_output = self.remove_blank_lines(old_output)
        self.send_cmd(command)

        cycles = 0
        start_time = time.time()

        def check_output():
            nonlocal cycles
            current_output = vte_term.get_text_format(Vte.Format(1))
            current_output = self.remove_blank_lines(current_output)
            # If the output has changed and the command has finished.
            if current_output != old_output and current_output.endswith(">> "):
                lines = current_output.splitlines()
                new_lines = []
                command_index = -1
                # Find the last occurence of the command.
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].startswith(">> " + command):
                        command_index = i
                        break
                # Get all the lines after the command, if it was found.
                # Otherwise get all of the lines.
                # Ignore the last line, which is the prompt.
                if command_index != -1:
                    new_lines = lines[command_index + 1 : -1]
                else:
                    new_lines = lines[:-1]
                cleaned_new_output = "\n".join(new_lines)
                # Check if cleaned_new_output is empty or contains only whitespace.
                if cleaned_new_output.strip():
                    result.append(cleaned_new_output)
                    # print(f'Output from "{command}":\n{cleaned_new_output}')
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

        GLib.idle_add(check_output)

    """
    Given a command, runs that command and returns its output.
    Returns None if the command finished with no output.
    Returns "Timeout" if the command doesn't finish within the number of
    seconds specified by the optional arg timeout, which by default is 2.
    The only issue is it can't see offscreen, so if the output looks the
    exact same as before the command was run, it will timeout.
    (try running "list" with no devices connected repeatedly to see what I mean)
    """

    def get_command_output(self, command, timeout=2):
        result = []
        self.check_command_output(self.vte_term, command, result, timeout)
        while not result:
            GLib.main_context_default().iteration(True)
        return result[0]

    def odin4_select_device(self):
        devices = self.get_command_output("list")
        # TODO: I haven't actually tested this with two devices connected.
        # devices = "/dev/device1\n/dev/device2"
        if not devices or devices == "Timeout":
            return None
        else:
            devices = devices.split("\n")
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

                window, grid = self.dialog(self.strings["connect_device"])
                self.create_label(self.strings["choose_a_device"], 0, 0, grid)
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

    def toggle_changed(self, switch, state, setting):
        active = switch.get_active()
        self.settings[setting] = active
        print(f"{setting} set to: {self.settings[setting]}")
        self.save_settings()

    def on_radiobutton_toggled(self, radiobutton, setting, value):
        # The "toggled" signal emits from a radiobutton that's getting de-selected
        # as well, so ignore signals coming from an inactive radiobutton.
        if radiobutton.get_active():
            self.set_setting(setting, value)

    def set_setting(self, setting, value):
        self.settings[setting] = value
        print(f"{setting} set to: '{value}'")
        self.save_settings()

    def error_dialog(self, message, function):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(f"Error in {function} function")
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
        self.send_cmd(text)

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
        odin_filter.set_name("ODIN files")
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
        column,
        row,
        grid,
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
        self, label, column, row, grid, padding=(0, 0, 0, 0), width=1, height=1
    ):
        check_button = Gtk.CheckButton(label=label)
        self.set_padding(check_button, padding)
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
        self.create_label(name, column, row, grid, padding, font)
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
