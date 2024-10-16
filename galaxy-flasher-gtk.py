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

import os
import platform
import re
import sys
import time
import shared_utils
from flash_tool_plugins import load_plugins

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Vte  # noqa: E402

version = "Alpha v0.5.2"
year = shared_utils.get_current_year()
copyright = f"© {year} ethical_haquer"
config_dir = GLib.get_user_config_dir()
app_dir = "galaxy-flasher"
app_config_dir = os.path.join(config_dir, app_dir)
if not os.path.exists(app_config_dir):
    os.makedirs(app_config_dir)
settings_file = os.path.join(app_config_dir, "settings.json")
swd = os.path.dirname(os.path.realpath(__file__))
machine = platform.machine()
system = platform.system().lower()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.last_output = ""
        self.i = 1
        self.glib = GLib
        self.time = time
        self.shared_utils = shared_utils
        self.gtk = Gtk
        self.re = re
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
        # Get the system language.
        self.lang = shared_utils.get_system_lang()
        # Load strings.
        # TODO: Update en.json.
        locale_file = shared_utils.get_locale_file(swd, self.lang)
        self.strings = shared_utils.load_strings(locale_file)
        # Load settings
        self.settings = shared_utils.load_settings(settings_file)
        self.flashtool = self.settings.get("flash_tool", "odin4")
        # Load plug-ins
        flash_tool_options = []
        try:
            plugins = load_plugins(self)
            if not plugins:
                print("No flash-tool plugins found.")
                return

            for plugin in plugins:
                print(f"Available flash-tool plugin: {plugin.name}")
                flash_tool_options.append(
                    {"name": plugin.displayed_name, "value": plugin.name}
                )

            plugin_name = self.flashtool
            for plugin in plugins:
                if plugin.__class__.__name__.lower() == plugin_name.lower():
                    self.ft_plugin = plugin
                    break
            else:
                print(f"Plugin {plugin_name} not found")

        except Exception as e:
            print(f"Error: {e}")
        self.ft_plugin.test()
        # Check if the app is running as a flatpak.
        self.is_flatpak = shared_utils.get_is_flatpak()
        # If the system isn't linux.
        if system != "linux":
            self.prompt = "never going to happen :)"
            print("Currently, Galaxy Flasher only supports Linux.")
            self.connect(
                "show",
                lambda _: self.create_alert_dialog(
                    "Unsupported OS",
                    "Currently, Galaxy Flasher only supports Linux.\nIf you think this is incorrect, please open an issue on GitHub, or let me know on XDA.",
                ),
            )
            flashtool_exec = [
                "echo",
                f"{system} is currently not supported by Galaxy Flasher.\nIf you think this is incorrect, please open an issue on GitHub, or let me know on XDA.",
            ]
        # If the system is Linux.
        else:
            # Set the flash-tool path.
            self.odin4_wrapper_file = f"{swd}/odin4-wrapper.sh"
            self.flashtool_file = self.settings.get(f"{self.flashtool}_file", None)
            self.prompt = self.ft_plugin.prompt

            if self.flashtool_file:
                if os.path.isfile(self.flashtool_file):
                    if self.flashtool == "odin4":
                        if os.path.isfile(self.odin4_wrapper_file):
                            if self.is_flatpak:
                                # Works when the file-system isn't host.
                                """
                                flashtool_exec = [
                                    "flatpak-spawn",
                                    "--host",
                                    "--env=TERM=xterm-256color",
                                    #f"--directory={swd}/app",
                                    self.odin4_wrapper_file,
                                    self.flashtool_file,
                                ]
                                """
                                # Works when the filesystem is host.
                                """
                                flashtool_exec = [
                                    "flatpak-spawn",
                                    "--env=TERM=xterm-256color",
                                    self.odin4_wrapper_file,
                                    self.flashtool_file,
                                ]
                                """
                                # Also works when the filesystem is host.
                                flashtool_exec = [
                                    self.odin4_wrapper_file,
                                    self.flashtool_file,
                                ]
                            else:
                                flashtool_exec = [
                                    self.odin4_wrapper_file,
                                    self.flashtool_file,
                                ]
                    else:
                        flashtool_exec = [
                            self.flashtool_file,
                        ]
                else:
                    flashtool_exec = [
                        "echo",
                        f'The {self.flashtool} executable you chose:\n"{self.flashtool_file}",\nwas not found. Please select a new executable by going to:\n"Settings - General - Flash Tool".',
                    ]
                    self.connect(
                        "show",
                        lambda _: self.create_alert_dialog(
                            "File not found",
                            f'The {self.flashtool} executable you chose:\n"{self.flashtool_file}",\nwas not found. Please select a new executable by going to: "Settings - General - Flash Tool".',
                        ),
                    )
            else:
                flashtool_exec = [
                    "echo",
                    'Welcome to Galaxy Flasher!\nPlease select a flash-tool to use by going to:\n"Settings - General - Flash Tool".',
                ]
                self.connect(
                    "show",
                    lambda _: self.create_alert_dialog(
                        "Welcome to Galaxy Flasher!",
                        'Please select a flash-tool to use by going to:\n"Settings - General - Flash Tool".',
                    ),
                )
        self.window_title = Adw.WindowTitle.new("Galaxy Flasher", f"{version}")

        # Create toolbar_view
        toolbar_view = Adw.ToolbarView.new()
        self.props.content = toolbar_view

        # Setup header
        self.header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(self.header_bar)

        # Create a toggle button for the command bar
        self.command_button = Gtk.ToggleButton.new()
        self.command_button.set_tooltip_text("Command")
        self.command_button.set_icon_name("utilities-terminal-symbolic")

        # Create command_entry
        self.command_entry = Gtk.Entry.new()
        self.command_entry.set_hexpand(True)
        self.command_entry.set_icon_from_icon_name(0, "utilities-terminal-symbolic")
        self.command_entry.set_placeholder_text("Run a command")
        self.command_entry.connect(
            "activate", lambda _, __: self.on_command_enter(), None
        )

        # Create command_bar
        self.command_bar = Gtk.ActionBar.new()
        self.command_bar.set_center_widget(self.command_entry)
        self.command_bar.set_revealed(False)  # Hide the command bar initially
        toolbar_view.add_top_bar(self.command_bar)

        # Connect the toggled signal to toggle_command_bar
        self.command_button.connect("toggled", self.toggle_command_bar)
        self.header_bar.pack_start(self.command_button)

        # Create about action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.create_about_dialog)
        self.add_action(about_action)

        self.preferences_dialog_layout = [
            {
                "title": "General",
                "rows": [
                    {
                        "type": "expander",
                        "title": "Flash Tool",
                        "subtitle": "The flash-tool Galaxy Flasher should use.",
                        "setting": "flash_tool",
                        "options": flash_tool_options,
                    },
                ],
            },
            {
                "title": "Appearance",
                "rows": [
                    {
                        "type": "combo",
                        "title": "Theme",
                        "function": self.on_combo_row_changed,
                        "function_args": ["$$combo_row", "$value_list", "$row_setting"],
                        "setting": "theme",
                        "options": [
                            {"name": "System", "value": "system"},
                            {"name": "Light", "value": "light"},
                            {"name": "Dark", "value": "dark"},
                        ],
                    },
                    {
                        "type": "switch",
                        "title": "Keep Log dark",
                        "subtitle": "Keep the Log Tab dark, regardless of the theme.",
                        "function": self.on_dark_log_switch_changed,
                        "function_args": ["$$switch_row", "$$active", "$row_setting"],
                        "setting": "keep_log_dark",
                        "default_value": False,
                    },
                ],
            },
            {
                "title": "Thor",
                "rows": [
                    {
                        "type": "switch",
                        "title": "Automatically select all partitions",
                        "subtitle": "Instead of asking what partitions to flash, automatically select them all.",
                        "function": self.on_switch_row_changed,
                        "function_args": ["$$switch_row", "$$active", "$row_setting"],
                        "setting": "auto_partitions",
                        "default_value": False,
                    },
                ],
            },
        ]

        # Create preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.create_preferences_dialog)

        # Connect the signal to the handler
        self.add_action(preferences_action)

        # Create menu
        menu = Gio.Menu.new()
        menu.append("Preferences", "win.preferences")
        menu.append("About Galaxy Flasher", "win.about")

        # Create popover
        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu)

        # Create hamburger
        hamburger = Gtk.MenuButton()
        hamburger.set_popover(popover)
        hamburger.set_icon_name("open-menu-symbolic")
        self.header_bar.pack_end(hamburger)

        # Create main grid
        self.grid = Gtk.Grid()
        toolbar_view.set_content(self.grid)
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)

        # Define the stack to hold tabs
        self.stack = Adw.ViewStack()

        # Create view_switcher
        self.view_switcher = Adw.ViewSwitcher()
        self.view_switcher.set_stack(self.stack)
        self.view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        # Set view_switcher as the title widget for header_bar
        self.header_bar.set_title_widget(self.view_switcher)

        # Create view_switcher_bar
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.stack)

        # Add view_switcher_bar to the toolbar_view
        toolbar_view.add_bottom_bar(self.view_switcher_bar)

        # Attach stack to grid
        self.grid.attach(self.stack, 0, 0, 1, 7)

        # Create breakpoint
        condition = Adw.BreakpointCondition.new_length(1, 700, Adw.LengthUnit.SP)
        self.breakpoint = Adw.Breakpoint.new(condition)
        self.breakpoint.connect("apply", self.on_width_breakpoint_applied)
        self.breakpoint.connect("unapply", self.on_width_breakpoint_unapplied)

        # Attach setters to breakpoint
        self.breakpoint.add_setter(self.view_switcher_bar, "reveal", True)

        # Add breakpoint
        self.add_breakpoint(self.breakpoint)

        # Specify what tabs to display
        tabs = self.ft_plugin.tabs

        # Create tabs
        for tab in tabs:
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            self.stack.add_titled(grid, tab, tab)
            setattr(self, f"{tab.lower()}_grid", grid)

        # Create flash-tool output box
        self.vte_term = Vte.Terminal()
        self.vte_term.spawn_async(
            Vte.PtyFlags.DEFAULT,  # Pty Flags
            swd,  # Working directory
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

        # Create scrolled_window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.vte_term)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_halign(Gtk.Align.FILL)
        scrolled_window.set_valign(Gtk.Align.FILL)
        self.log_grid.attach(scrolled_window, 0, 0, 1, 1)

        # Set the style_manager
        self.style_manager = Adw.StyleManager.get_default()

        # Set the theme
        theme = self.settings.get("theme") or "system"
        self.set_theme(theme)
        self.on_theme_changed(self.style_manager, None)

        # Detect whenever the theme changes.
        self.style_manager.connect("notify::dark", self.on_theme_changed)

        # Create the main buttons.
        buttons = self.ft_plugin.buttons

        button_grid = Gtk.Grid(column_spacing=10)
        self.set_padding(button_grid, (10, 10, 10, 10))

        for column, btn in enumerate(buttons):
            name = btn["name"]
            text = btn["text"]
            command = btn["command"]
            button = self.create_button(
                text,
                column=column,
                row=0,
                grid=button_grid,
                command=command,
            )
            button.set_hexpand(True)
            button.set_halign(Gtk.Align.FILL)
            setattr(self, name, button)

        self.log_grid.attach(button_grid, column=0, row=1, width=1, height=1)

        # Initialise the main buttons
        self.ft_plugin.initialise_buttons(self)

        # Create the Option Tab widgets.
        row = 0
        options_list = self.ft_plugin.options_list
        if options_list:
            self.create_preferences(options_list, self.options_grid)

        # Create the File Tab widgets.
        row = 0
        padding = (10, 0, 0, 0)
        entry_padding = (0, 10, 0, 0)
        slots = ["BL", "AP", "CP", "CSC", "USERDATA"]
        for slot in slots:
            if slot is slots[-1]:
                padding = (10, 0, 0, 10)
                entry_padding = (0, 10, 0, 10)
            button = self.create_button(
                slot,
                1,
                row,
                self.files_grid,
                lambda _, x=slot: self.open_file(x),
                padding,
            )
            width = 1
            entry = self.create_entry(
                2, row, self.files_grid, entry_padding, width, 1, True
            )
            setattr(self, f"{slot}_button", button)
            setattr(self, f"{slot}_entry", entry)
            if self.flashtool == "pythor":
                button.set_sensitive(False)
                entry.set_sensitive(False)
            row += 1

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
        self.vte_term.connect(
            "contents-changed", lambda *args: self.scan_output(*args, self.i)
        )

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

    def on_width_breakpoint_applied(self, breakpoint):
        self.header_bar.set_title_widget(self.window_title)

    def on_width_breakpoint_unapplied(self, breakpoint):
        self.header_bar.set_title_widget(self.view_switcher)

    def toggle_command_bar(self, button):
        active = button.get_active()
        if active:
            self.command_entry.grab_focus()
        self.command_bar.set_revealed(active)

    def thor_select_partitions(self, files, base_dir, auto):
        self.ft_plugin.select_partitions(self, files, base_dir, auto)

    def create_window(self, title):
        grid = Gtk.Grid()
        window = Gtk.Window()
        window.set_modal(True)
        window.set_title(title)
        window.set_child(grid)
        window.set_transient_for(self)
        return window, grid

    def scan_output(self, vte, i):
        # print(f"contents changed: {i}")
        self.i += 1
        strings_to_commands = self.ft_plugin.strings_to_commands
        # This is a pretty bad way to do this.
        # 10000 should be replaced with the actual value, But it works.
        num_cols = vte.get_column_count()
        term_text = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, num_cols)[0]
        prompt = self.prompt.strip()
        parts = term_text.strip().rsplit(prompt)
        for part in reversed(parts):
            latest_output = part.strip()
            if latest_output:
                break
        else:
            latest_output = ""
        if latest_output != self.last_output:
            for string, commands in strings_to_commands.items():
                if string in latest_output and string not in self.last_output:
                    for command in commands:
                        command()
            self.last_output = latest_output

    def check_output(self, vte, command, result, start, end, wait, add_enter, timeout):
        # This is a pretty bad way to do this.
        # 10000 should be replaced with the actual value, But it works.
        num_cols = vte.get_column_count()
        old_output = vte.get_text_range_format(Vte.Format(1), 0, 0, 10000, num_cols)[0]
        old_output = shared_utils.remove_blank_lines(old_output)
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
            num_cols = vte.get_column_count()
            current_output = vte.get_text_range_format(
                Vte.Format(1), 0, 0, 10000, num_cols
            )[0]
            current_output = shared_utils.remove_blank_lines(current_output)
            # If the output has changed or wait is False.
            if current_output != old_output or wait is False:
                lines = current_output.splitlines()
                new_lines = []
                start_index = -1
                """
                trimmed_start = start[:num_cols]
                print(f"trimmed_start: {trimmed_start}")
                # Find the last occurence of trimmed_start.
                for i in range(len(lines) - 1, -1, -1):
                    if trimmed_start in lines[i]:
                        start_index = i
                        break
                    """
                words = start.split()  # split the start string into a list of words
                shortened_start = ""  # initialize an empty string
                for word in words:
                    if (
                        len(shortened_start) + len(word) + 1 <= num_cols
                    ):  # check if adding the word fits in num_cols space
                        shortened_start += word + " "
                    else:
                        break

                shortened_start = shortened_start.strip()  # remove the trailing space

                print(f"shortened_start: {shortened_start}")

                for i in range(len(lines) - 1, -1, -1):
                    if shortened_start in lines[i]:
                        start_index = i
                        break
                    # start_match = re.search(trimmed_start, lines[i])
                    # if start_match:
                # Get all the lines after start and up to end, if it's
                # found, otherwise get everything after start.
                if start_index != -1:
                    new_lines = lines[start_index + 1 :]
                end_index = None
                if end:
                    words = end.split()  # split the start string into a list of words
                    shortened_end = ""  # initialize an empty string
                    for word in words:
                        if (
                            len(shortened_end) + len(word) + 1 <= num_cols
                        ):  # check if adding the word fits in num_cols space
                            shortened_end += word + " "
                        else:
                            break

                    shortened_end = shortened_end.strip()  # remove the trailing space

                    print(f"shortened_end: {shortened_end}")
                    for i, line in enumerate(new_lines):
                        line = line.strip()
                        if shortened_end in line:
                            end_index = i
                            break
                # If end was found or was None, return the result,
                # otherwise continue.
                if end_index is not None or end is None:
                    if end is not None:
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

    # TODO: This could be improved.
    def select_device(self, function=None):
        self.ft_plugin.select_device(self, function=None)

    # TODO: Display the partitions that are to be flashed.
    def verify_flash(self, n, partitions, auto):
        def callback(dialog, result):
            response_id = dialog.choose_finish(result)
            if response_id == "no":
                self.send_cmd("n")
            elif response_id == "yes":
                self.send_cmd("y")

        noun = "The computer" if auto else "You"
        responses = [
            {"id": "yes", "label": "Yes", "appearance": "0"},
            {"id": "no", "label": "No", "appearance": "0"},
        ]
        self.create_alert_dialog(
            "Verify flash",
            f"{noun} selected {n} partitions to flash.\nAre you absolutely sure you want to flash them?",
            responses,
            callback,
            "no",
        )

    def set_setting(self, setting, value):
        if setting == "theme":
            self.set_theme(value)
        self.settings[setting] = value
        print(f"{setting} set to: '{value}'")
        shared_utils.save_settings(self.settings, settings_file)

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
        self.style_manager.set_color_scheme(color_scheme)

    def on_dark_log_switch_changed(self, switch, state, setting):
        active = switch.get_active()
        self.set_setting(setting, active)
        self.on_theme_changed(self.style_manager, None)

    def on_theme_changed(self, style_manager, gparam):
        dark = style_manager.props.dark
        if dark:
            terminal_foreground = "#ffffff"
            terminal_background = "#242424"
        else:
            if self.settings.get("keep_log_dark"):
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

    def send_cmd(self, cmd, add_enter=True):
        if add_enter:
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
                self.ft_plugin.select_device()
            if cmd == "flashTar\n":
                special = True
                self.ft_plugin.flash(self)
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

    # Given a widget, prints it's widget tree.
    def print_widget_tree(
        self, widget, indent_str: str = "", top_level: bool = True
    ) -> None:
        if top_level:
            print(f"{indent_str}{widget.__class__.__name__}")

        child_widgets = []
        child = widget.get_first_child()
        while child:
            child_widgets.append(child)
            child = child.get_next_sibling()

        for i, child in enumerate(child_widgets):
            if i == len(child_widgets) - 1:
                connector = "└─"
                sub_indent = "   "
            else:
                connector = "├─"
                sub_indent = "│  "
            print(f"{indent_str}{connector} {child.__class__.__name__}")
            if child.get_first_child():
                self.print_widget_tree(child, indent_str + sub_indent, False)

    def create_switch_row(
        self,
        name: str,
        title: str = None,
        subtitle: str = None,
        active: bool = None,
        sensitive: bool = None,
        signal: str = "notify::active",
        function: callable = None,
        function_args: list = None,
        commands: list = None,
    ) -> Adw.SwitchRow:
        """
        Creates a new Adw.SwitchRow instance.

        Args:
            name (str): The name of the switch row.
            title (str, optional): The title of the switch row. Defaults to None.
            subtitle (str, optional): The subtitle of the switch row. Defaults to None.
            active (bool, optional): Whether the switch row is active. Defaults to None.
            sensitive (bool, optional): Whether the switch row is sensitive. Defaults to None.
            signal (str, optional): The signal to connect the function to. Defaults to 'notify::active'.
            function (callable, optional): The function to connect to the switch row's signal. Defaults to None.
            function_args (list, optional): The arguments to pass to the function. Defaults to None.
            commands (list, optional): A list of commands to execute after creating the switch_row. The format is:
            [(example_command, ["example_string", "$example_variable", example_variable])] Strings starting with "$"
            are converted to variables defined in this function at run-time. Defaults to None.

        Returns:
            Adw.SwitchRow: The created switch row.
        """

        switch_row = Adw.SwitchRow.new()
        setattr(self, name, switch_row)
        switch_row.name = name
        switch_row.switch = switch_row.get_child().get_last_child().get_first_child()

        if title:
            switch_row.set_title(title)
        if subtitle:
            switch_row.set_subtitle(subtitle)
        if active is not None:
            switch_row.set_active(active)
        if sensitive is not None:
            switch_row.set_sensitive(sensitive)
        if function:
            if signal is None:
                signal = "notify::active"
            if function_args is None:
                switch_row.connect(signal, function)
            else:
                args = []
                for arg in function_args:
                    if isinstance(arg, str) and arg.startswith("$$"):
                        args.append(locals()[arg[2:]])
                    else:
                        args.append(arg)
                switch_row.connect(signal, lambda *_, args=args: function(*args))
        if commands:
            for command, arg_names in commands:
                args = []
                for arg_name in arg_names:
                    if isinstance(arg_name, str) and arg_name.startswith("$"):
                        args.append(locals()[arg_name[1:]])
                    else:
                        args.append(arg_name)
                command(*args)

        return switch_row

    def create_combo_row(
        self,
        name: str,
        title: str = None,
        subtitle: str = None,
        model: Gtk.StringList = None,
        selected: str = None,
        function: callable = None,
        function_args: list = None,
        commands: list = None,
    ) -> Adw.ComboRow:
        """
        Creates a new Adw.ComboRow instance.

        Args:
            name (str): The name of the combo row.
            title (str, optional): The title of the combo row. Defaults to None.
            subtitle (str, optional): The subtitle of the combo row. Defaults to None.
            model (Gtk.StringList, optional): The model to use for the combo row. Defaults to None.
            selected (str, optional): The selected item in the combo row. Defaults to None.
            function (callable, optional): The function to connect to the combo row's "notify::selected" signal. Defaults to None.
            function_args (list, optional): The arguments to pass to the function. Defaults to None.
            commands (list, optional): A list of commands to execute after creating the switch_row. The format is:
            [(example_command, ["example_string", "$example_variable", example_variable])] Strings starting with "$"
            are converted to variables defined in this function at run-time. Defaults to None.

        Returns:
            Adw.ComboRow: The created combo row.
        """
        combo_row = Adw.ComboRow()
        setattr(self, name, combo_row)
        if title:
            combo_row.set_title(title)
        if subtitle:
            combo_row.set_subtitle(subtitle)
        if model:
            combo_row.set_model(model)
        if selected:
            combo_row.set_selected(selected)
        if function:
            if function_args is None:
                combo_row.connect("notify::selected", function)
            else:
                args = []
                for arg in function_args:
                    if isinstance(arg, str) and arg.startswith("$$"):
                        args.append(locals()[arg[2:]])
                    else:
                        args.append(arg)
                combo_row.connect(
                    "notify::selected", lambda *_, args=args: function(*args)
                )
        if commands:
            for command, arg_names in commands:
                args = []
                for arg_name in arg_names:
                    if isinstance(arg_name, str) and arg_name.startswith("$"):
                        args.append(locals()[arg_name[1:]])
                    else:
                        args.append(arg_name)
                command(*args)
        return combo_row

    def create_expander_row(
        self,
        name: str,
        title: str = None,
        subtitle: str = None,
        rows: list = None,
    ) -> Adw.ExpanderRow:
        """
        Creates a new Adw.ExpanderRow instance.

        Args:
            name (str): The name of the expander row.
            title (str, optional): The title of the expander row. Defaults to None.
            subtitle (str, optional): The subtitle of the expander row. Defaults to None.
            rows (list, optional): The rows to add to the expander row. Defaults to None.

        Returns:
            Adw.ExpanderRow: The created expander row.
        """
        expander_row = Adw.ExpanderRow()
        setattr(self, name, expander_row)
        if title:
            expander_row.set_title(title)
        if subtitle:
            expander_row.set_subtitle(subtitle)
        if rows:
            for row in rows:
                expander_row.add_row(row)

        return expander_row

    def add_custom_expander_row_label(
        self,
        text: str,
        expander_row: Adw.ExpanderRow,
    ) -> None:
        expander_row.added_label = Gtk.Label(label=text)

        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label_box.append(expander_row.added_label)
        action_row_box = (
            expander_row.get_first_child()  # box
            .get_first_child()  # list_box
            .get_first_child()  # action_row
            .get_first_child()  # action_row_box
        )
        last_box = action_row_box.get_last_child()
        label_box.insert_before(action_row_box, last_box)

    def create_action_row(
        self, name, title, subtitle, prefixes, suffixes, activatable_widget
    ):
        action_row = Adw.ActionRow.new()
        setattr(self, name, action_row)
        if title:
            action_row.set_title(title)
        if subtitle:
            action_row.set_subtitle(subtitle)
        if prefixes:
            for prefix in prefixes:
                action_row.add_prefix(prefix)
        if suffixes:
            for suffix in suffixes:
                action_row.add_suffix(suffix)
        if activatable_widget:
            action_row.set_activatable_widget(activatable_widget)

        return action_row

    def create_preferences(self, main_preferences_list: list, grid: Gtk.Grid) -> None:
        # TODO: Good in-code documentation takes up too much space, is hard to maintain, and is hard to read.
        # I need to look into alternative solutions.
        """
        Creates a preferences page based on the provided main_preferences_list.

        This function creates an Adw.PreferencesPage and populates it with sections and settings
        based off the items in main_preferences_list. Each section is represented by an Adw.PreferencesGroup,
        and each row is represented by a row within the group. The type of row depends on the type
        specified in the row dictionary, which can be "switch", "combo", or "expander".

        Parameters:
            main_preferences_list (list): A list of dictionaries, where each dictionary represents a section
            of the preferences page. Each section dictionary should contain:
                - "title" (str): The title of the section.
                - "section_sensitive" (bool, optional): Refer to the description of the sensitive arg below.
                - "section_signal" (str, optional): Refer to the description of the signal arg below.
                - "section_function" (function, optional): Refer to the description of the function arg below.
                - "section_function_args" (list, optional): Refer to the description of the function_args argument below.
                NOTE: If a row-specific option is specified, it overides a section-wide option.
                - "section_commands" (list, optional):
                - "rows" (list): A list of dictionaries, where each dictionary represents a row in the section.
                    Each row dictionary can contain:
                    - "type" (str): The type of row, which can be "switch", "combo", or "expander".
                    - "title" (str): The title of the row.
                    - "subtitle" (str, optional): The subtitle of the row. Only applies to switch rows.
                    - "active" (bool, optional): Whether the row is active. Only applies to switch rows.
                    - "sensitive" (bool, optional): Whether the row is sensitive.
                    - "signal" (str, optional): The signal to connect the function to. Only applies to switch rows.
                    - "function" (function, optional): A function to be executed when the row is interacted with.
                    - "function_args" (list, optional): A list of args to pass to the function. Oftentimes, you want to
                    pass a variable to the function that is set in this function, say row_setting. Or maybe you want to
                    pass a variable that is set in the function that creates the row, like switch_row in create_switch_row.
                    You can do this by taking the variable you want to pass to the function, making it a string, and then
                    adding a "$" to the beggining of it. For example, row_setting becomes "$row_setting". You can do
                    the same with variables that should be set in the function that creates the individual
                    row (create_switch_row, create_combo_row, and create_expander_row), just add two "$"s instead of one.
                    For, example, switch_row would become "$$switch_row" in command_args.
                    - "commands" (list, optional): A list of commands to execute after creating the row. The format is:
                    [(example_command, ["example_string", "$example_variable", example_variable])]
                    Strings starting with "$" are converted to variables defined in create_{type}_switch at run-time.
                    - "setting" (str): The name of the setting associated with the row.

            grid (Gtk.Grid): The grid to which the preferences page should be attached.

        Returns:
            None
        """
        preferences_page = Adw.PreferencesPage.new()
        preferences_page.set_hexpand(True)
        for section in main_preferences_list:
            preferences_group = Adw.PreferencesGroup.new()
            preferences_page.add(preferences_group)
            group_title = section.get("title")
            section_sensitive = section.get("section_sensitive")
            section_signal = section.get("section_signal")
            section_function = section.get("section_function")
            section_function_args = section.get("section_function_args")
            section_commands = section.get("section_commands")
            rows = section.get("rows")
            if group_title:
                preferences_group.set_title(group_title)
            for row in rows:
                row_type = row.get("type")
                row_title = row.get("title")
                row_subtitle = row.get("subtitle")
                row_sensitive = row.get("sensitive")
                row_signal = row.get("signal")
                row_function = row.get("function")
                row_function_args = row.get("function_args")
                row_commands = row.get("commands")
                row_setting = row.get("setting")
                if not row_type:
                    print(
                        'Error in create_preferences: The "type" arg must be specified.'
                    )
                    break
                if not row_setting:
                    print(
                        'Error in create_preferences: The "setting" arg must be specified.'
                    )
                    break
                if row_type == "switch":
                    name = f"{row_setting}_switch_row"
                    default_value = row.get("default_value", False)
                    active = self.settings.get(row_setting, default_value)
                elif row_type == "combo":
                    options = row.get("options")
                    default_value = next(
                        (
                            option["value"]
                            for option in options
                            if option["value"] == self.settings.get(row_setting)
                        ),
                        options[0]["value"],
                    )
                    value_name_list = Gtk.StringList.new()
                    value_list = [option["value"] for option in options]
                    for option in options:
                        value_name_list.append(option["name"])
                    name = f"{row_setting}_combo_row"
                    model = value_name_list
                    selected = value_list.index(default_value)
                if row_type == "switch" or row_type == "combo":
                    if row_sensitive is not None:
                        sensitive = row_sensitive
                    else:
                        sensitive = section_sensitive
                    if row_signal is not None:
                        signal = row_signal
                    else:
                        signal = section_signal
                    if row_function:
                        function = row_function
                    elif section_function:
                        function = section_function
                    else:
                        if row_type == "switch":
                            function = self.on_switch_row_changed
                        elif row_type == "combo":
                            function = self.on_combo_row_changed
                    args = None
                    if row_function_args is not None:
                        args = row_function_args
                    else:
                        args = section_function_args
                    if args:
                        function_args = []
                        for arg in args:
                            if arg.startswith("$") and len(arg) > 1 and arg[1] != "$":
                                function_args.append(locals()[arg[1:]])
                            else:
                                function_args.append(arg)
                    else:
                        function_args = None
                    if row_commands is not None:
                        commands = row_commands
                    else:
                        commands = section_commands
                if row_type == "switch":
                    switch_row = self.create_switch_row(
                        name,
                        row_title,
                        row_subtitle,
                        active,
                        sensitive,
                        signal,
                        function,
                        function_args,
                        commands,
                    )
                    preferences_group.add(switch_row)
                elif row_type == "combo":
                    combo_row = self.create_combo_row(
                        name,
                        row_title,
                        row_subtitle,
                        model,
                        selected,
                        function,
                        function_args,
                    )
                    preferences_group.add(combo_row)
                elif row_type == "expander":
                    options = row["options"]
                    default_value = next(
                        (
                            option["value"]
                            for option in options
                            if option["value"] == self.settings.get(row_setting)
                        ),
                        options[0]["value"],
                    )
                    value_name_list = [option["name"] for option in options]
                    value_list = [option["value"] for option in options]
                    current_value_name = "Not set"
                    radio_group = None
                    rows = []
                    for i, option in enumerate(options):
                        name = option.get("name")
                        value = option.get("value")
                        action_row = Adw.ActionRow(title=name)
                        flashtool_file = self.settings.get(f"{value}_file", None)
                        if flashtool_file:
                            action_row.set_subtitle(flashtool_file)
                        setattr(self, f"{value}_action_row", action_row)
                        check_button = Gtk.CheckButton()
                        setattr(action_row, "check_button", check_button)
                        check_button.set_group(radio_group)
                        if value == default_value and self.settings.get(
                            f"{value}_file", None
                        ):
                            check_button.set_active(True)
                            current_value_name = name
                        setattr(self, f"{row_setting}_expander_row", None)
                        check_button.connect(
                            "toggled",
                            lambda _, action_row=action_row, check_button=check_button, setting=row_setting, value=value: self.on_action_row_checkbutton_clicked(
                                action_row, check_button, setting, value
                            ),
                        )
                        radio_group = check_button
                        action_row.add_prefix(check_button)
                        button_box = Gtk.Box(spacing=0)
                        file_chooser_button = Gtk.Button()
                        info_button = Gtk.Button()
                        self.set_padding(file_chooser_button, [0, 0, 10, 10])
                        self.set_padding(info_button, [0, 0, 10, 10])
                        file_chooser_button_content = Adw.ButtonContent(
                            label="", icon_name="document-open-symbolic"
                        )
                        info_button_content = Adw.ButtonContent(
                            label="", icon_name="help-about-symbolic"
                        )
                        file_chooser_button.set_child(file_chooser_button_content)
                        info_button.set_child(info_button_content)
                        file_chooser_button.set_has_frame(False)
                        info_button.set_has_frame(False)
                        file_chooser_button.connect(
                            "clicked",
                            lambda _, action_row=action_row, setting=row_setting, name=name, value=value: self.on_action_row_file_button_clicked(
                                action_row, setting, name, value
                            ),
                        )
                        info_button.connect(
                            "clicked",
                            lambda _, action_row=action_row, setting=row_setting, name=name, value=value: self.on_info_button_clicked(
                                action_row, setting, name, value
                            ),
                        )
                        button_box.append(file_chooser_button)
                        button_box.append(info_button)
                        action_row.add_suffix(button_box)
                        if self.settings.get(f"{value}_file", None):
                            action_row.set_activatable_widget(check_button)
                        else:
                            action_row.set_activatable_widget(file_chooser_button)
                        rows.append(action_row)
                    name = f"{row_setting}_expander_row"
                    expander_row = self.create_expander_row(
                        name, row_title, row_subtitle, rows
                    )
                    self.add_custom_expander_row_label(current_value_name, expander_row)
                    expander_row.added_label.set_label(current_value_name)
                    preferences_group.add(expander_row)
                else:
                    print(
                        f'Error in create_preferences: "{row_type}" is not a valid type. Valid types are "switch", "combo", and "expander".'
                    )
        grid.attach(preferences_page, 0, 0, 1, 1)

    def create_preferences_dialog(self, *_):
        """
        Creates a preferences dialog based on the provided main_preferences_list.

        This function creates an Adw.PreferencesPage and populates it with sections and settings
        based off the items in main_preferences_list. Each section is represented by an Adw.PreferencesGroup,
        and each row is represented by a row within the group. The type of row depends on the type
        specified in the row dictionary, which can be "switch", "combo", or "expander".

        Parameters:
            main_preferences_list (list): A list of dictionaries, where each dictionary represents a section
            of the preferences page. Each section dictionary should contain:
                - "title" (str): The title of the section.
                - "section_sensitive" (bool, optional): Refer to the description of the sensitive arg below.
                - "section_signal" (str, optional): Refer to the description of the signal arg below.
                - "section_function" (function, optional): Refer to the description of the function arg below.
                - "section_function_args" (list, optional): Refer to the description of the function_args argument below.
                NOTE: If a row-specific option is specified, it overides a section-wide option.
                - "section_commands" (list, optional):
                - "rows" (list): A list of dictionaries, where each dictionary represents a row in the section.
                    Each row dictionary can contain:
                    - "type" (str): The type of row, which can be "switch", "combo", or "expander".
                    - "title" (str): The title of the row.
                    - "subtitle" (str, optional): The subtitle of the row. Only applies to switch rows.
                    - "active" (bool, optional): Whether the row is active. Only applies to switch rows.
                    - "sensitive" (bool, optional): Whether the row is sensitive.
                    - "signal" (str, optional): The signal to connect the function to. Only applies to switch rows.
                    - "function" (function, optional): A function to be executed when the row is interacted with.
                    - "function_args" (list, optional): A list of args to pass to the function. Oftentimes, you want to
                    pass a variable to the function that is set in this function, say row_setting. Or maybe you want to
                    pass a variable that is set in the function that creates the row, like switch_row in create_switch_row.
                    You can do this by taking the variable you want to pass to the function, making it a string, and then
                    adding a "$" to the beggining of it. For example, row_setting becomes "$row_setting". You can do
                    the same with variables that should be set in the function that creates the individual
                    row (create_switch_row, create_combo_row, and create_expander_row), just add two "$"s instead of one.
                    For, example, switch_row would become "$$switch_row" in command_args.
                    - "commands" (list, optional): A list of commands to execute after creating the row. The format is:
                    [(example_command, ["example_string", "$example_variable", example_variable])]
                    Strings starting with "$" are converted to variables defined in create_{type}_switch at run-time.
                    - "setting" (str): The name of the setting associated with the row.

            grid (Gtk.Grid): The grid to which the preferences page should be attached.

        Returns:
            None
        """
        main_preferences_list = self.preferences_dialog_layout
        preferences_dialog = Adw.PreferencesDialog.new()
        preferences_page = Adw.PreferencesPage.new()
        preferences_page.set_hexpand(True)
        preferences_dialog.add(preferences_page)
        for section in main_preferences_list:
            preferences_group = Adw.PreferencesGroup.new()
            preferences_page.add(preferences_group)
            group_title = section.get("title")
            section_sensitive = section.get("section_sensitive")
            section_signal = section.get("section_signal")
            section_function = section.get("section_function")
            section_function_args = section.get("section_function_args")
            section_commands = section.get("section_commands")
            rows = section.get("rows")
            if group_title:
                preferences_group.set_title(group_title)
            for row in rows:
                row_type = row.get("type")
                row_title = row.get("title")
                row_subtitle = row.get("subtitle")
                row_sensitive = row.get("sensitive")
                row_signal = row.get("signal")
                row_function = row.get("function")
                row_function_args = row.get("function_args")
                row_commands = row.get("commands")
                row_setting = row.get("setting")
                if not row_type:
                    print(
                        'Error in create_preferences: The "type" arg must be specified.'
                    )
                    break
                if not row_setting:
                    print(
                        'Error in create_preferences: The "setting" arg must be specified.'
                    )
                    break
                if row_type == "switch":
                    name = f"{row_setting}_switch_row"
                    default_value = row.get("default_value", False)
                    active = self.settings.get(row_setting, default_value)
                elif row_type == "combo":
                    options = row.get("options")
                    default_value = next(
                        (
                            option["value"]
                            for option in options
                            if option["value"] == self.settings.get(row_setting)
                        ),
                        options[0]["value"],
                    )
                    value_name_list = Gtk.StringList.new()
                    value_list = [option["value"] for option in options]
                    for option in options:
                        value_name_list.append(option["name"])
                    name = f"{row_setting}_combo_row"
                    model = value_name_list
                    selected = value_list.index(default_value)
                if row_type == "switch" or row_type == "combo":
                    if row_sensitive is not None:
                        sensitive = row_sensitive
                    else:
                        sensitive = section_sensitive
                    if row_signal is not None:
                        signal = row_signal
                    else:
                        signal = section_signal
                    if row_function:
                        function = row_function
                    elif section_function:
                        function = section_function
                    else:
                        if row_type == "switch":
                            function = self.on_switch_row_changed
                        elif row_type == "combo":
                            function = self.on_combo_row_changed
                    args = None
                    if row_function_args is not None:
                        args = row_function_args
                    else:
                        args = section_function_args
                    if args:
                        function_args = []
                        for arg in args:
                            if arg.startswith("$") and len(arg) > 1 and arg[1] != "$":
                                function_args.append(locals()[arg[1:]])
                            else:
                                function_args.append(arg)
                    else:
                        function_args = None
                    if row_commands is not None:
                        commands = row_commands
                    else:
                        commands = section_commands
                if row_type == "switch":
                    switch_row = self.create_switch_row(
                        name,
                        row_title,
                        row_subtitle,
                        active,
                        sensitive,
                        signal,
                        function,
                        function_args,
                        commands,
                    )
                    preferences_group.add(switch_row)
                elif row_type == "combo":
                    combo_row = self.create_combo_row(
                        name,
                        row_title,
                        row_subtitle,
                        model,
                        selected,
                        function,
                        function_args,
                    )
                    preferences_group.add(combo_row)
                elif row_type == "expander":
                    options = row["options"]
                    default_value = next(
                        (
                            option["value"]
                            for option in options
                            if option["value"] == self.settings.get(row_setting)
                        ),
                        options[0]["value"],
                    )
                    value_name_list = [option["name"] for option in options]
                    value_list = [option["value"] for option in options]
                    current_value_name = "Not set"
                    radio_group = None
                    rows = []
                    for i, option in enumerate(options):
                        name = option.get("name")
                        value = option.get("value")
                        action_row = Adw.ActionRow(title=name)
                        flashtool_file = self.settings.get(f"{value}_file", None)
                        if flashtool_file:
                            action_row.set_subtitle(flashtool_file)
                        setattr(self, f"{value}_action_row", action_row)
                        check_button = Gtk.CheckButton()
                        setattr(action_row, "check_button", check_button)
                        check_button.set_group(radio_group)
                        if value == default_value and self.settings.get(
                            f"{value}_file", None
                        ):
                            check_button.set_active(True)
                            current_value_name = name
                        setattr(self, f"{row_setting}_expander_row", None)
                        check_button.connect(
                            "toggled",
                            lambda _, action_row=action_row, check_button=check_button, setting=row_setting, value=value: self.on_action_row_checkbutton_clicked(
                                action_row, check_button, setting, value
                            ),
                        )
                        radio_group = check_button
                        action_row.add_prefix(check_button)
                        button_box = Gtk.Box(spacing=0)
                        file_chooser_button = Gtk.Button()
                        info_button = Gtk.Button()
                        self.set_padding(file_chooser_button, [0, 0, 10, 10])
                        self.set_padding(info_button, [0, 0, 10, 10])
                        file_chooser_button_content = Adw.ButtonContent(
                            label="", icon_name="document-open-symbolic"
                        )
                        info_button_content = Adw.ButtonContent(
                            label="", icon_name="help-about-symbolic"
                        )
                        file_chooser_button.set_child(file_chooser_button_content)
                        info_button.set_child(info_button_content)
                        file_chooser_button.set_has_frame(False)
                        info_button.set_has_frame(False)
                        file_chooser_button.connect(
                            "clicked",
                            lambda _, action_row=action_row, setting=row_setting, name=name, value=value: self.on_action_row_file_button_clicked(
                                action_row, setting, name, value
                            ),
                        )
                        info_button.connect(
                            "clicked",
                            lambda _, action_row=action_row, setting=row_setting, name=name, value=value: self.on_info_button_clicked(
                                action_row, setting, name, value
                            ),
                        )
                        button_box.append(file_chooser_button)
                        button_box.append(info_button)
                        action_row.add_suffix(button_box)
                        if self.settings.get(f"{value}_file", None):
                            action_row.set_activatable_widget(check_button)
                        else:
                            action_row.set_activatable_widget(file_chooser_button)
                        rows.append(action_row)
                    name = f"{row_setting}_expander_row"
                    expander_row = self.create_expander_row(
                        name, row_title, row_subtitle, rows
                    )
                    self.add_custom_expander_row_label(current_value_name, expander_row)
                    expander_row.added_label.set_label(current_value_name)
                    preferences_group.add(expander_row)
                else:
                    print(
                        f'Error in create_preferences: "{row_type}" is not a valid type. Valid types are "switch", "combo", and "expander".'
                    )
        preferences_dialog.present(self)

    def on_action_row_checkbutton_clicked(
        self, action_row, check_button, setting, value
    ):
        if check_button.get_active():
            expander_row = getattr(self, f"{setting}_expander_row")
            expander_row.added_label.set_label(action_row.get_title())
            self.set_setting(setting, value)

    def on_action_row_file_button_clicked(self, action_row, setting, name, value):
        if setting == "flash_tool":
            name = "Pythor" if value == "pythor" else name

            def file_dialog_callback(obj, result):
                try:
                    file = obj.open_finish(result)
                    if file:
                        file_path = file.get_path()
                        print(f"Selected {name} executable: {file_path}")
                        self.set_setting(f"{value}_file", file_path)
                        action_row.set_activatable_widget(action_row.check_button)
                        action_row.set_subtitle(file_path)
                        action_row.do_activate(action_row)

                except GLib.Error as e:
                    # If the user cancelled, pass.
                    if e.code == 2:
                        pass
                    else:
                        print(f"Error: {e}")

            file_dialog = Gtk.FileDialog(
                title=f'Select {"an" if value == "odin4" else "a"} {name} executable'
            )
            file_filter = Gtk.FileFilter()
            if value == "thor":
                file_filter.set_name("Thor executable")
                file_filter.add_pattern("TheAirBlow.Thor.Shell")
            if value == "odin4":
                file_filter.set_name("Odin4 executable")
                file_filter.add_pattern("odin4")
            if value == "pythor":
                file_filter.set_name("PyThor executable")
                file_filter.add_pattern("*pythor*")
            filter_list = Gio.ListStore.new(Gtk.FileFilter)
            filter_list.append(file_filter)
            file_dialog.set_filters(filter_list)
            file_dialog.open(self, None, file_dialog_callback)

    def on_info_button_clicked(self, action_row, setting, name, value):
        name = "Pythor" if value == "pythor" else name
        name = "About " + name
        if value == "thor":
            text = """Thor is an open-source flash-tool based off Odin4 and Heimdall.

You can download Thor from <a href="https://github.com/Samsung-Loki/Thor/releases/tag/1.0.4" title="https://github.com/Samsung-Loki/Thor/releases/tag/1.0.4">GitHub</a>, or use
<a href="https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/#post-89123207"
title="https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/#post-89123207">this self-contained build of Thor</a>.

Using the self-contained build is recommended, since you don't have to install .NET to use it, but both will work with Galaxy Flasher."""
        elif value == "odin4":
            text = """Odin4 is a propriatary flash-tool that was leaked from Samsung.

You can download Odin4 from <a href="https://xdaforums.com/t/official-samsung-odin-v4-1-2-1-dc05e3ea-for-linux.4453423/#post-86977569"
title="https://xdaforums.com/t/official-samsung-odin-v4-1-2-1-dc05e3ea-for-linux.4453423/#post-86977569">XDA</a>."""
        elif value == "pythor":
            text = """PyThor is an open-source flash-tool that is still under development. As such, the only reason to use it is if you want to contribute.

<a href="https://github.com/justaCasualCoder/PyThor"
title="https://github.com/justaCasualCoder/PyThor">PyThor's GitHub page</a>"""
        dialog = Adw.Dialog.new()
        dialog.get_accessible_role()
        dialog.set_title(name)
        dialog.set_content_width(420)
        # dialog.set_content_height(480)
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        header_bar = Adw.HeaderBar.new()
        toolbar_view.add_top_bar(header_bar)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_propagate_natural_height(True)
        toolbar_view.set_content(scrolled_window)
        label = Gtk.Label.new()
        self.set_padding(label, [24, 24, 12, 24])
        label.set_markup(text)
        label.set_wrap(True)
        scrolled_window.set_child(label)
        dialog.present(self)

    def on_switch_row_changed(self, switch, state, setting):
        value = switch.get_active()
        self.set_setting(setting, value)

    def on_combo_row_changed(self, combo_row, value_list, setting):
        new_value_index = combo_row.get_selected()
        new_value = value_list[new_value_index]
        self.set_setting(setting, new_value)

    def create_alert_dialog(
        self,
        title,
        text,
        responses=None,
        callback=None,
        default_response="NULL",
        extra_child=None,
    ):
        alert_dialog = Adw.AlertDialog.new(title, text)
        if responses:
            for response in responses:
                id = response["id"]
                label = response["label"]
                appearance = response["appearance"]
                alert_dialog.add_response(id, label)
                alert_dialog.set_response_appearance(id, appearance)
            alert_dialog.set_default_response(default_response)
        else:
            alert_dialog.add_response("ok", "OK")
        if extra_child:
            alert_dialog.set_extra_child(extra_child)
        alert_dialog.choose(self, None, callback)

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

            def handler(widget, value=value):
                return self.on_radiobutton_toggled(widget, setting, value)

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

    def create_about_dialog(self, *_):
        about_dialog = Adw.AboutDialog.new()
        about_dialog.set_application_name("Galaxy Flasher")
        about_dialog.set_developer_name("ethical_haquer")
        about_dialog.set_version(version)
        about_dialog.set_website("https://codeberg.org/ethical_haquer/Galaxy-Flasher")
        about_dialog.set_support_url(
            "https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/"
        )
        about_dialog.set_issue_url(
            "https://codeberg.org/ethical_haquer/Galaxy-Flasher/issues"
        )
        # about_dialog.add_link("Codeberg repo", "https://codeberg.org/ethical_haquer/Galaxy-Flasher")
        # about_dialog.add_link("Report an issue", "https://codeberg.org/ethical_haquer/Galaxy-Flasher/issues")
        # about_dialog.add_link("Documentation", "https://galaxy-flasher-docs.readthedocs.io/en/latest/")
        # about_dialog.add_link("Chat on XDA", "https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/")
        about_dialog.set_developers(
            [
                "ethical_haquer https://codeberg.org/ethical_haquer/",
                "justaCasualCoder https://github.com/justaCasualCoder",
            ]
        )
        about_dialog.add_credit_section(
            "Thor by", ["TheAirBlow https://github.com/TheAirBlow"]
        )
        about_dialog.set_copyright(copyright)
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.present(self)


class GalaxyFlasherGtk(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_default_size(950, 400)
        self.win.present()


if __name__ == "__main__":
    app = GalaxyFlasherGtk(application_id="com.ethicalhaquer.galaxyflasher")
    app.run(sys.argv)
