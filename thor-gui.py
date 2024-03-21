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

import gi
import os
import sys
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
from gi.repository import Gtk, Adw, GLib, Gio, Vte

version = "Alpha v0.4.6"
json_file = "locales/en_US.json"
cwd = os.getcwd()
# TODO: Base this off of OS.
thor_exec = [f"{cwd}/Thor/linux-x64/TheAirBlow.Thor.Shell"]


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.currently_running = False
        super().__init__(*args, **kwargs)
        with open(json_file) as json_string:
            self.strings = json.load(json_string)
        self.tool = "thor"
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
        # Setup Thor output box
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
        self.vte_term.set_opacity(0.8)
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
        # Define current row
        row = 3
        # Setup slots
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
        # Setup command entry
        self.command_entry = self.create_entry(1, 1, self.grid, 2, 1)
        self.command_entry.connect("activate", self.on_command_enter)
        # Setup enter, pgup, pgdown, start_thor, start_odin and space button
        self.connect_button = self.create_button(
            self.strings["connect"],
            2,
            0,
            self.grid,
            lambda _: self.send_cmd("connect\n"),
        )
        self.enter_button = self.create_button(
            self.strings["enter"], 3, 1, self.grid, lambda _: self.send_cmd("\n")
        )
        self.space_button = self.create_button(
            self.strings["space"], 1, 2, self.grid, lambda _: self.send_cmd("\x20")
        )
        self.page_up_button = self.create_button(
            "PgUp", 2, 2, self.grid, lambda _: self.send_cmd("\x1b[A")
        )
        self.page_down_button = self.create_button(
            "PgDn", 3, 2, self.grid, lambda _: self.send_cmd("\x1b[B")
        )
        self.start_odin_button = self.create_button(
            self.strings["start_odin_protocol"],
            3,
            0,
            self.grid,
            lambda _: self.start_odin(),
        )
        # self.set_widget_state(self.command_entry, self.enter_button, self.space_button, self.page_up_button, self.page_down_button, self.connect_button, state=False)
        # Setup header
        # Setup HeaderBar
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        # Connect about action
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
        self.create_button("Flash!", 1, 0, self.grid, lambda _: self.flash())
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
        self.create_label(
            f"{self.strings['just_a_test']}\n\n{self.strings['pull_requests_welcome']}",
            0,
            0,
            self.pit_grid,
        )
        self.create_label("Thor", 0, 0, self.settings_grid)
        self.create_check_button("Run Thor with sudo", 0, 1, self.settings_grid)
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
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            entry = getattr(self, f"{slot}_entry")
            if entry.get_text():
                # TODO Implement flashing here
                print(f"Flashing {entry.get_text()} to {slot}")

    def start_odin(self):
        self.send_cmd("begin odin\n")
        self.set_widget_state(self.start_odin_button, state=False)

    def on_command_enter(self, *args):
        text = self.command_entry.get_text()
        # Clear Command entry
        self.command_entry.set_text("")
        self.send_cmd(text + "\n")

    def set_widget_state(*args, state=True):
        for widget in args:
            # TODO This NEEDS to be fixed. I have not looked into it yet.
            if widget.get_name() == "__main__+MainWindow":
                pass
            else:
                widget.set_sensitive(state)

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
            "TheAirBlow", ["Github Profile https://github.com/TheAirBlow"]
        )
        dialog.add_credit_section(
            "ethical_haquer", ["Github Profile https://github.com/ethical-haquer"]
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
