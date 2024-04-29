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

locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = "_"
lang = locale.split(seperator, 1)[0]

version = "Alpha v0.5.0"
settings_file = "settings.json"
locale_file = f"locales/{lang}.json"
cwd = os.getcwd()
arch = platform.architecture()[0][:2]
system = platform.system().lower()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.last_text = ""
        super().__init__(*args, **kwargs)
        # Load strings
        with open(locale_file) as json_string:
            self.strings = json.load(json_string)
        # Load settings
        self.load_settings()
        thor_path = f"{cwd}/Thor/{system}-x{arch}/TheAirBlow.Thor.Shell"
        if self.settings.get("sudo", False):
            thor_exec = ["sudo", thor_path]
        else:
            thor_exec = [thor_path]
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
        if not os.path.isfile(thor_path):
            print(f"Error: File {thor_path} not found")
            self.realize_id = self.connect(
                "show", lambda _: self.thor_file_not_found_dialog(thor_path)
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
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_halign(Gtk.Align.FILL)
        scrolled_window.set_valign(Gtk.Align.FILL)
        self.stack.add_titled(scrolled_window, "Log", "Log")
        # Creates other tabs
        for tab in ["Options", "Pit", "Settings"]:
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            self.stack.add_titled(grid, tab, tab)
            setattr(self, f"{tab.lower()}_grid", grid)
        # Create file slots
        row = 2
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            button = self.create_button(
                slot, 1, row, self.grid, lambda _, x=slot: self.open_file(x)
            )
            button.set_margin_top(10)
            entry = self.create_entry(2, row, self.grid, 2, 1, True)
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
        self.set_widget_state(
            self.connect_button, self.start_odin_button, self.flash_button, state=False
        )
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
        # Create the option tab widgets
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
        # Create the settings tab widgets
        row = 0
        self.options = [
            {"label": self.strings["run_thor_sudo"], "setting": "sudo"},
        ]
        for item in self.options:
            text = item["label"]
            setting = item["setting"]
            label = self.create_label(
                text, 1, row, self.settings_grid, align=Gtk.Align.START
            )
            switch = self.create_switch(0, row, self.settings_grid)
            switch.set_active(self.settings.get(setting, False))
            switch.connect("state-set", self.switch_changed, setting)
            active = switch.get_active()
            self.settings[setting] = active
            row = row + 1
        # Scan the output whenever it changes
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

    def thor_file_not_found_dialog(self, thor_path):
        self.disconnect(self.realize_id)
        self.error_dialog(
            self.strings["file_not_found2"].format(file=thor_path), "__init__"
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
            self.send_cmd(f"flashTar {base_dir}\n")
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
                    self.connect_button, lambda _: self.send_cmd("disconnect\n")
                ),
            ],
            "Successfully disconnected the device!": [
                lambda: print("Successfully disconnected the device!"),
                lambda: self.set_widget_state(self.start_odin_button, state=False),
                lambda: self.connect_button.set_label("Connect"),
                lambda: self.change_button_command(
                    self.connect_button, lambda _: self.send_cmd("connect\n")
                ),
            ],
            "Successfully began an Odin session!": [
                lambda: print("Successfully began an Odin session!"),
                # TODO: Why do we need to enable the start_odin_button here?
                # It's supposed to be enabled above ^
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
                    self.start_odin_button, lambda _: self.start_odin()
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
            "Choose a device to connect to:": [lambda: self.select_device(term_text)],
        }
        term_text = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, 10000)[0]
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
            checkbutton = self.create_check_button(item.strip(), 0, row, grid)
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
        self.send_cmd(f"options {option} {value}\n")

    def switch_changed(self, switch, state, setting):
        active = switch.get_active()
        self.settings[setting] = active
        print(f"{setting} set to: {self.settings[setting]}")
        self.save_settings()

    def error_dialog(self, message, function):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(f"Error in {function} function")
        dialog.set_detail(message)
        dialog.set_buttons(["OK"])
        dialog.show(self)

    def start_odin(self):
        self.send_cmd("begin odin\n")

    def end_odin(self):
        self.send_cmd("end\n")

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
        self,
        text,
        column,
        row,
        grid,
        font=("monospace", 11),
        width=1,
        height=1,
        align=Gtk.Align.FILL,
    ):
        label = Gtk.Label()
        label.set_markup(f'<span font_desc="{font[0]} {font[1]}">{text}</span>')
        label.set_halign(align)
        grid.attach(label, column, row, width, height)
        return label

    def create_button(self, label, column, row, grid, command, width=1, height=1):
        button = Gtk.Button(label=label)
        button.signal_id = button.connect("clicked", command)
        grid.attach(button, column, row, width, height)
        return button

    def change_button_command(self, button, new_command):
        button.disconnect(button.signal_id)
        button.signal_id = button.connect("clicked", new_command)

    def create_entry(self, column, row, grid, width=1, height=1, expand=False):
        text_entry = Gtk.Entry()
        if expand:
            text_entry.set_hexpand(True)
            # text_entry.set_vexpand(True)
            text_entry.set_halign(Gtk.Align.FILL)
            # text_entry.set_valign(Gtk.Align.FILL)
        grid.attach(text_entry, column, row, width, height)
        return text_entry

    def create_check_button(self, label, column, row, grid, width=1, height=1):
        button = Gtk.CheckButton(label=label)
        grid.attach(button, column, row, width, height)
        return button

    def create_switch(self, column, row, grid, width=1, height=1):
        switch = Gtk.Switch()
        grid.attach(switch, column, row, width, height)
        return switch

    def about_window(self, *_):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Thor GUI")
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
