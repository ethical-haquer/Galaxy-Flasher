"""
Thor GUI - A GUI for the Thor Flash Utility
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

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
from gi.repository import Adw, Gio, GLib, Gtk, Vte

version = "Alpha v0.4.6"
locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = "_"
lang = locale.split(seperator, 1)[0]
json_file = f"locales/{lang}.json"
cwd = os.getcwd()
arch = platform.architecture()[0][:2]
system = platform.system().lower()
# TODO: Add option for sudo/no sudo
thor_exec = ["sudo", f"{cwd}/Thor/{system}-x{arch}/TheAirBlow.Thor.Shell"]


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.currently_running = False
        self.last_text = ""
        super().__init__(*args, **kwargs)
        with open(json_file) as json_string:
            self.strings = json.load(json_string)
        # Define main grid
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)
        self.set_child(self.grid)
        # Set window title
        self.set_title(f"Thor GUI - {version}")
        self.create_label("Thor Flash Utility", 0, 0, self.grid, ("Monospace", 20))
        # Define stack to hold tabs
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)
        # Setup StackSwitcher
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        # Attach stack/StackSwitcher
        self.grid.attach(self.stack_switcher, 0, 1, 1, 1)
        self.grid.attach_next_to(
            self.stack, self.stack_switcher, Gtk.PositionType.BOTTOM, 1, 6
        )
        # Check if Thor file exists
        if not os.path.isfile(thor_exec[1]):
            print(f"Error: File {thor_exec[1]} not found")
            # TODO: Wait until main window is fully created
            self.error_dialog(
                self.strings["file_not_found2"].format(file=thor_exec[1]), "__init__"
            )
        # Create Thor output box
        self.vte_term = Vte.Terminal()
        self.vte_term.spawn_async(
            Vte.PtyFlags.DEFAULT,  # Pty Flags
            cwd,  # Working DIR
            thor_exec,  # Command/BIN (argv)
            None,  # Environmental Variables (env)
            GLib.SpawnFlags.DEFAULT,  # Spawn Flags
            None,
            None,  # Child Setup
            -1,  # Timeout (-1 for indefinitely)
            None,  # Cancellable
            None,  # Callback
            None,  # User Data
        )
        # Set clear background
        self.vte_term.set_clear_background(False)
        # Create scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.vte_term)
        self.stack.add_titled(scrolled_window, "Log", "Log")
        # Creates other tabs
        for tab in ["Options", "Pit", "Settings"]:
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            self.stack.add_titled(grid, tab, tab)
            setattr(self, f"{tab.lower()}_grid", grid)
        # Set initial row
        row = 2
        # Create file slots
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            button = self.create_button(
                slot, 1, row, self.grid, lambda _, x=slot: self.open_file(x)
            )
            button.set_margin_top(10)
            entry = self.create_entry(2, row, self.grid, 2, 1)
            entry.set_margin_top(10)
            setattr(self, f"{slot}_entry", entry)
            setattr(self, f"{slot}_button", button)
            row = row + 1
        # Create command entry
        self.command_entry = self.create_entry(
            column=1,
            row=1,
            grid=self.grid,
            width=3,
            height=1,
        )
        self.command_entry.connect("activate", self.on_command_enter, None)
        # Create connect, start_odin, and flash buttons
        self.connect_button = self.create_button(
            self.strings["connect"],
            column=1,
            row=0,
            grid=self.grid,
            command=lambda _: self.send_cmd("connect\n"),
        )
        self.start_odin_button = self.create_button(
            self.strings["start_odin_protocol"],
            column=2,
            row=0,
            grid=self.grid,
            command=lambda _: self.start_odin(),
        )
        self.flash_button = self.create_button(
            "Flash!",
            column=3,
            row=0,
            grid=self.grid,
            command=lambda _: self.flash(),
        )
        self.set_widget_state(self.start_odin_button, self.flash_button, state=False)
        # @justaCasualCoder, I don't know which of these comments you want:
        # Setup header
        # Setup HeaderBar
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
        # Set initial row
        row = 0
        self.options = [
            {"option": "T Flash", "label": f"{self.strings['tflash_temporarily']}"},
            {"option": "EFS Clear", "label": ""},
            {"option": "Bootloader Update", "label": ""},
            {"option": "Reset Flash Count", "label": ""},
        ]
        for item in self.options:
            option = item["option"]
            label = item["label"]
            if label:
                self.create_label(label, 0, row, self.options_grid)
                row = row + 1
            check_button = self.create_check_button(option, 0, row, self.options_grid)
            check_button.connect("toggled", self.option_changed)
            row = row + 1
        # Create place-holder label for Pit tab
        self.create_label(
            f"{self.strings['just_a_test']}\n\n{self.strings['pull_requests_welcome']}",
            0,
            0,
            self.pit_grid,
        )
        self.create_label("Thor", 0, 0, self.settings_grid)
        self.create_check_button("Run Thor with sudo", 0, 1, self.settings_grid)
        self.vte_term.connect("contents-changed", self.scan_output)
        print(
            f"""
         _____ _                   ____ _   _ ___
        |_   _| |__   ___  _ __   / ___| | | |_ _|
          | | | '_ \ / _ \| '__| | |  _| | | || |
          | | | | | | (_) | |    | |_| | |_| || |
          |_| |_| |_|\___/|_|     \____|\___/|___|

                      {version}
        """
        )

    def select_partitions(self):
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
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            file_path = getattr(self, f"{slot}_entry").get_text()
            if file_path:
                with tarfile.open(file_path) as tar_file:
                    for member in tar_file.getmembers():
                        self.selected_buttons.append([False, file_path])
                        split = member.name.split(".")
                        # Skip Pit file
                        if split[1] != "pit":
                            name = split[0].upper()
                            file_names.append(name)
                            btn = self.create_check_button(name, 0, row, grid)
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
        # This is a pretty bad way to do this. 10000 should be replaced with the actual value, But it works.
        terminal_text = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, 10000)[0]
        if terminal_text.strip().rsplit("shell>")[-1].strip() == "":
            try:
                terminal_text = terminal_text.strip().rsplit("shell>")[-2].strip()
            except:
                terminal_text = terminal_text.strip().rsplit("shell>")[-1].strip()
        else:
            terminal_text = terminal_text.strip().rsplit("shell>")[-1].strip()
        if terminal_text != self.last_text:
            if (
                "[sudo] password for" in terminal_text
                and "[sudo] password for" not in self.last_text
            ):
                self.set_password_entry(self.command_entry, True)

            if (
                "Welcome to Thor Shell" in terminal_text
                and "Welcome to Thor Shell" not in self.last_text
            ):
                self.set_password_entry(self.command_entry, False)

            if (
                "Successfully connected to the device!" in terminal_text
                and "Successfully connected to the device!" not in self.last_text
            ):
                self.set_widget_state(self.start_odin_button, state=True)

            if (
                "Successfully began an Odin session!" in terminal_text
                and "Successfully began an Odin session!" not in self.last_text
            ):
                self.set_widget_state(self.start_odin_button, self.flash_button, state=True)

            if "> [ ]" in terminal_text and "> [ ]" not in self.last_text:
                self.select_partitions()

            if (
                "Are you absolutely sure you want to flash those?" in terminal_text
                and "Are you absolutely sure you want to flash those?"
                not in self.last_text
            ):
                self.verify_flash()

            if (
                "Choose a device to connect to:" in terminal_text
                and "Choose a device to connect to:" not in self.last_text
            ):
                self.select_device(terminal_text)
            self.last_text = terminal_text

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
            checkbutton = self.create_check_button(item.strip(), 0, row, grid)
            if index == 0:
                group = checkbutton
            else:
                checkbutton.set_group(group)
            checkbutton.connect("toggled", set_selected_device, row)
            row = row + 1
        self.create_button("Cancel", 1, row, grid, lambda _: window.destroy())
        self.create_button(
            "OK",
            2,
            row,
            grid,
            lambda btn: (self.send_selected_device(btn), window.destroy()),
        )
        window.present()

    def send_selected_device(self, btn):
        for _ in range(self.device_index - 1):
            self.send_cmd("\x1b[B")
        self.send_cmd("\n")

    def verify_flash(self):
        window, grid = self.dialog(self.strings["verify_flash"])
        self.create_label(self.strings["are_you_sure"], 0, 0, grid)
        self.create_button(
            self.strings["yes"],
            1,
            1,
            grid,
            lambda _: (self.send_cmd("y" + "\n"), window.destroy()),
        ).set_margin_end(5)
        self.create_button(
            self.strings["no"],
            2,
            1,
            grid,
            lambda _: (self.send_cmd("n" + "\n"), window.destroy()),
        )
        window.present()

    def option_changed(self, button):
        print(
            f"{button.get_label().lower().replace(' ', '_')}_enabled ",
            button.get_active(),
        )
        setattr(
            self,
            f"{button.get_label().lower().replace(' ', '_')}_enabled",
            button.get_active(),
        )
        if button.get_label().lower().replace(" ", "_") == "t_flash":
            self.send_cmd(f"options tflash {button.get_active()}\n")
        if button.get_label().lower().replace(" ", "_") == "efs_clear":
            self.send_cmd(f"options efsclear {button.get_active()}\n")
        if button.get_label().lower().replace(" ", "_") == "reset_flash_count":
            self.send_cmd(f"options resetfc {button.get_active()}\n")
        if button.get_label().lower().replace(" ", "_") == "bootloader_update":
            self.send_cmd(f"options blupdate {button.get_active()}\n")

    def flash(self):
        paths = {}
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            entry = getattr(self, f"{slot}_entry")
            if entry.get_text():
                print(f"Flashing {entry.get_text()} to {slot}")
                path = os.path.dirname(entry.get_text())
                paths[slot] = os.path.dirname(entry.get_text())
        if len(set(paths.values())) > 1:
            print("The files NEED to be in the same dir...")
            self.error_dialog(self.strings["invalid_files"], "flash")
        else:
            self.send_cmd(f"flashTar {list(paths.values())[0]}\n")
            self.scan_output(self.vte_term)

    def send_selected_partitions(self):
        last_file = ""
        for selected, file_path in self.selected_buttons:
            if last_file and last_file != file_path:
                self.send_cmd("\n")
            if selected:
                self.send_cmd("\x20")
            self.send_cmd("\x1b[B")
            last_file = file_path
        self.send_cmd("\n")

    def error_dialog(self, message, function):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(f"Error in {function} function")
        dialog.set_detail(message)
        dialog.set_buttons(["OK"])
        dialog.show()

    def start_odin(self):
        self.send_cmd("begin odin\n")

    def on_command_enter(self, *args):
        text = self.command_entry.get_text()
        # Clear Command entry
        self.command_entry.set_text("")
        self.send_cmd(text + "\n")

    def set_widget_state(self, *args, state=True):
        for widget in args:
            widget.set_sensitive(state)

    def toggle_entry_visibility(self, entry, icon_pos):
        visible = entry.get_visibility()
        if visible:
            entry.set_visibility(False)
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition(icon_pos), "view-reveal-symbolic"
            )
        else:
            entry.set_visibility(True)
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition(icon_pos), "view-conceal-symbolic"
            )

    def set_password_entry(self, entry, state):
        if state:
            entry.set_visibility(False)
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition(1), "view-reveal-symbolic"
            )
        else:
            entry.set_visibility(True)
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition(1), "view-conceal-symbolic"
            )
        self.command_entry.connect("icon-press", self.toggle_entry_visibility)

    def send_cmd(self, cmd):
        self.vte_term.feed_child(cmd.encode("utf-8"))

    def open_file(self, partition):
        def file_dialog_callback(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                file = dialog.get_file()
                if file:
                    print(f"Selected file: {file.get_path()}")
                    entry = getattr(self, f"{partition}_entry")
                    entry.set_text(file.get_path())
            dialog.destroy()

        file_dialog = Gtk.FileChooserDialog(
            title=f"Select a {partition} file",
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self,
        )
        file_dialog.add_buttons(
            "Open", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL
        )
        odin_filter = Gtk.FileFilter()
        odin_filter.set_name("ODIN files")
        odin_filter.add_mime_type("application/x-tar")
        odin_filter.add_pattern("*.tar.md5")
        odin_filter.add_pattern("*.tar")
        file_dialog.add_filter(odin_filter)
        file_dialog.connect("response", file_dialog_callback)
        file_dialog.show()

    def create_label(
        self, text, column, row, grid, font=("monospace", 11), width=1, height=1
    ):
        label = Gtk.Label()
        label.set_markup(f'<span font_desc="{font[0]} {font[1]}">{text}</span>')
        grid.attach(label, column, row, width, height)
        return label

    def create_button(self, label, column, row, grid, command, width=1, height=1):
        button = Gtk.Button(label=label)
        button.connect("clicked", command)
        grid.attach(button, column, row, width, height)
        return button

    def create_entry(self, column, row, grid, width=1, height=1):
        text_entry = Gtk.Entry()
        grid.attach(text_entry, column, row, width, height)
        return text_entry

    def create_check_button(self, label, column, row, grid, width=1, height=1):
        button = Gtk.CheckButton(label=label)
        grid.attach(button, column, row, width, height)
        return button

    def about_window(self, *_):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Thor GUI")
        dialog.set_version(version)
        dialog.set_developer_name("ethical_haquer")
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.add_credit_section(
            "justaCasualCoder", ["Github Profile https://github.com/justaCasualCoder"]
        )
        dialog.add_credit_section(
            "ethical_haquer", ["Github Profile https://github.com/ethical-haquer"]
        )
        dialog.add_credit_section(
            "TheAirBlow", ["Github Profile https://github.com/TheAirBlow"]
        )
        dialog.set_website("https://github.com/ethical-haquer/Thor_GUI")
        dialog.set_issue_url("https://github.com/ethical-haquer/Thor_GUI/issues")
        dialog.set_visible(True)


class ThorGUI(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = ThorGUI(application_id="com.ethicalhaquer.thorgui")
app.run(sys.argv)
