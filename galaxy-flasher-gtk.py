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
import pexpect
import re
import sys
import time
import shared_utils
import logging
from flash_tool_plugins import load_plugins

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
#gi.require_version("Vte", "3.91")

from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango  # noqa: E402

version = "Alpha v0.6.0"
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
logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_output = ""
        self.glib = GLib
        self.time = time
        self.shared_utils = shared_utils
        self.gtk = Gtk
        self.re = re
        self.selected_files = {}
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
                logger.error("__init__: No flash-tool plugins found.")
                return

            for plugin in plugins:
                logger.info(f"__init__: Available flash-tool plugin: {plugin.name}")
                flash_tool_options.append(
                    {"name": plugin.displayed_name, "value": plugin.name}
                )

            plugin_name = self.flashtool
            for plugin in plugins:
                if plugin.__class__.__name__.lower() == plugin_name.lower():
                    self.ft_plugin = plugin
                    break
            else:
                logger.error(f"__init__: Plugin {plugin_name} not found")

        except Exception as e:
            logger.error(f"__init__: Error: {e}")
        self.ft_plugin.test()
        # Check if the app is running as a flatpak.
        self.is_flatpak = shared_utils.get_is_flatpak()
        # If the system isn't linux.
        if system != "linux":
            self.prompt = "never going to happen :)"
            logger.error("__init__: Currently, Galaxy Flasher only supports Linux.")
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

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["FORCE_COLOR"] = "3"
        self.child = pexpect.spawn(
            "/home/ethical_haquer/TheAirBlow.Thor.Shell",
            env=env,
            timeout=5,
        )
        # self.child.logfile = sys.stdout.buffer

        # Make the whole window draggable and right-clickable.
        self.handle = Gtk.WindowHandle.new()
        self.props.content = self.handle

        # Create the flash button
        self.start_button = self.create_button(
            "Start",
            column=0,
            row=0,
            command=lambda _: self.display_files(),
        )
        self.start_button.set_hexpand(True)
        self.start_button.set_vexpand(True)
        self.start_button.add_css_class("pill")
        self.start_button.add_css_class("suggested-action")

        # Create a box to hold the flash button
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_hexpand(True)
        box.set_vexpand(True)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.append(self.start_button)

        # Create the flash page
        self.flash_page = Adw.StatusPage.new()
        self.flash_page.set_icon_name("com.ethicalhaquer.galaxyflasher")
        self.flash_page.set_title("Galaxy Flasher")
        self.flash_page.set_description(
            "Connect a device in Download Mode, and then click the button to start."
        )
        self.flash_page.set_child(box)

        # Create header bar
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_show_title(False)

        # Create toolbar view
        self.toolbar_view = Adw.ToolbarView.new()
        self.toolbar_view.add_top_bar(self.header_bar)
        self.toolbar_view.set_content(self.flash_page)

        self.toast_overlay = Adw.ToastOverlay.new()
        self.handle.set_child(self.toast_overlay)

        # Create the stack
        self.stack = Gtk.Stack.new()
        # self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.toast_overlay.set_child(self.stack)
        self.stack.add_named(self.toolbar_view, "flash")

        # Create about action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.create_about_dialog)
        self.add_action(about_action)

        # Preferences dialog layout
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
                ],
            },
            {
                "title": "Thor",
                "rows": [
                    {
                        "type": "switch",
                        "title": "Automatically select all partitions",
                        "subtitle": "Automatically select all partitions to flash.",
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
        self.add_action(preferences_action)

        # Create menu
        menu = Gio.Menu.new()
        menu.append("Preferences", "win.preferences")
        menu.append("About Galaxy Flasher", "win.about")

        # Create popover with menu
        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu)

        # Create hamburger menu button
        hamburger = Gtk.MenuButton()
        hamburger.set_popover(popover)
        hamburger.set_icon_name("open-menu-symbolic")
        self.header_bar.pack_end(hamburger)

        # Set the style_manager
        self.style_manager = Adw.StyleManager.get_default()

        # Set the theme
        theme = self.settings.get("theme") or "system"
        self.set_theme(theme)

        # Initialise the main buttons
        self.ft_plugin.initialise_buttons(self)

        self.ft_plugin.setup_flash_tool(self)

        """
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
        """

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

    def display_files(self):
        logger.debug("display_files is running")
        # If the files page hasn't already been made.
        if not self.stack.get_child_by_name("files"):
            grid = Gtk.Grid.new()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)

            button_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            padding = (10, 10, 0, 0)
            self.set_padding(button_box, padding)

            row = 0
            slots = ["BL", "AP", "CP", "CSC", "USERDATA"]

            for slot in slots:
                button = Gtk.Button(label=slot)
                button.signal_id = button.connect(
                    "clicked", lambda _, x=slot: self.open_file(x)
                )
                button.add_css_class("pill")
                button.set_can_shrink(True)
                # button.add_css_class("circular")
                button.set_hexpand(True)
                button.set_halign(Gtk.Align.FILL)
                button.set_valign(Gtk.Align.FILL)

                setattr(self, f"{slot}_button", button)

                button_row_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
                button_row_box.append(button)
                button_box.append(button_row_box)

                row += 1

            nav_buttons = [
                {
                    "title": "Continue",
                    "command": lambda _: self.check_files(),
                },
                {
                    "title": "Cancel",
                    "command": lambda _: self.cancel_flash("files"),
                },
            ]

            self.add_page_to_stack(
                content=button_box, name="files", nav_buttons=nav_buttons
            )

        self.stack.set_visible_child_name("files")

    def check_files(self):
        logger.debug("check_files is running")
        files = []
        paths = {}
        for slot in ["BL", "AP", "CP", "CSC", "USERDATA"]:
            slot_lowered = slot.lower()
            # file_path = main.selected_files[slot_lowered]
            if slot_lowered in self.selected_files:
                file_path = self.selected_files[slot_lowered]
                if file_path:
                    file_name = os.path.basename(file_path)
                    files.append(file_name)
                    paths[slot] = os.path.dirname(file_path)
        if len(paths) == 0:
            logger.info(f'check_files: {self.strings["no_files_selected2"]}')
            self.create_alert_dialog(
                "Invalid files", self.strings["no_files_selected2"]
            )
        elif len(set(paths.values())) > 1:
            logger.info("check_files: The files NEED to be in the same dir...")
            self.create_alert_dialog("Invalid files", self.strings["invalid_files"])
        else:
            self.ft_plugin.selected_files(self, files, paths)

    def display_devices(self, devices):
        logger.debug("display_devices is running")

        def set_selected_device(btn, device):
            if btn.get_active:
                device_number = device

        devices_page = self.stack.get_child_by_name("devices")

        if devices_page:
            self.stack.remove(devices_page)

        checkbutton_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        checkbutton_box.set_hexpand(True)
        # checkbutton_box.set_vexpand(True)
        checkbutton_box.set_halign(Gtk.Align.CENTER)
        checkbutton_box.set_valign(Gtk.Align.START)

        device_number = 1
        group = None
        row = 1

        for i, device in enumerate(devices):
            checkbutton = self.create_checkbutton(device, 0, row)
            checkbutton.add_css_class("selection-mode")
            checkbutton_box.append(checkbutton)
            if i == 0:
                group = checkbutton
                checkbutton.set_active(True)
            else:
                checkbutton.set_group(group)
            checkbutton.connect("toggled", set_selected_device, row)
            row = row + 1

        nav_buttons = [
            {
                "title": "Continue",
                "command": lambda _: self.ft_plugin.selected_device(
                    self, device_number, len(devices)
                ),
            },
            {
                "title": "Cancel",
                "command": lambda _: self.cancel_flash(
                    "devices", num_devices=len(devices)
                ),
            },
        ]

        self.add_page_to_stack(
            content=checkbutton_box, name="devices", nav_buttons=nav_buttons
        )
        self.stack.set_visible_child_name("devices")

    def display_partitions(self, file, partitions, function):
        logger.debug("display_partitions is running")
        selected_partitions = []

        def partition_toggled(button, row):
            if button.get_active():
                selected_partitions[row] = True
            else:
                selected_partitions[row] = False

        partitions_page = self.stack.get_child_by_name("partitions")

        if partitions_page:
            self.stack.remove(partitions_page)
            
        main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        main_box.set_hexpand(True)
        #main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.START)

        checkbutton_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        checkbutton_box.set_hexpand(True)
        # checkbutton_box.set_vexpand(True)
        checkbutton_box.set_halign(Gtk.Align.CENTER)
        checkbutton_box.set_valign(Gtk.Align.START)

        label = Gtk.Label.new()
        label.set_label(f"Select what partitions to flash from {file}")
        label.set_ellipsize(Pango.EllipsizeMode.END)
        
        main_box.append(label)
        main_box.append(checkbutton_box)

        for i, partition in enumerate(partitions):
            checkbutton = self.create_checkbutton(partition)
            #checkbutton.set_halign(Gtk.Align.CENTER)
            checkbutton.add_css_class("selection-mode")
            checkbutton_box.append(checkbutton)
            checkbutton.connect("toggled", partition_toggled, i)
            selected_partitions.append(False)
            #row += 1

        nav_buttons = [
            {
                "title": "Continue",
                "command": lambda _: function(
                    self, selected_partitions
                ),
            },
            {
                "title": "Cancel",
                "command": lambda _: function(
                    self, selected_partitions
                ),
            },
        ]

        self.add_page_to_stack(
            content=main_box, name="partitions", nav_buttons=nav_buttons
        )
        self.stack.set_visible_child_name("partitions")

    def cancel_flash(self, page, num_devices=None):
        logger.debug("cancel_flash is running")
        if page == "devices":
            self.ft_plugin.selected_device(self, None, num_devices)
        self.stack.set_visible_child_full("flash", Gtk.StackTransitionType.SLIDE_RIGHT)

    def on_no_devices_found(self):
        logger.debug("on_no_devices_found is running")
        message = "No Samsung devices were found!"
        logger.info(f"on_no_devices_found: {message}")
        toast = Adw.Toast.new(message)
        toast.set_timeout(5)
        self.toast_overlay.add_toast(toast)

    def display_verify_flash(self, auto, num_partitions, function):
        logger.debug("display_verify_flash is running")

        verify_flash_page = self.stack.get_child_by_name("verify")

        # If the partitions page has already been made.
        if verify_flash_page:
            self.stack.remove(verify_flash_page)

        label_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        label_box.set_hexpand(True)
        # checkbutton_box.set_vexpand(True)
        label_box.set_halign(Gtk.Align.CENTER)
        label_box.set_valign(Gtk.Align.START)

        row = 0

        main_label = Gtk.Label.new()
        main_label.set_label("Verify Flash")

        secondary_label = Gtk.Label.new()
        noun = "The computer" if auto else "You"
        secondary_label.set_label(
            f"{noun} selected {num_partitions} partitions in total. Are you absolutely sure you want to flash them?"
        )

        label_box.append(main_label)
        label_box.append(secondary_label)

        nav_buttons = [
            {
                "title": "Yes",
                "command": lambda _: function(self, True),
            },
            {
                "title": "No",
                "command": lambda _: function(self, False),
            },
        ]

        self.add_page_to_stack(
            content=label_box, name="verify", nav_buttons=nav_buttons
        )
        self.stack.set_visible_child_name("verify")

    # Original verify_flash.
    """
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
    """

    def on_flash(self):
        logger.debug("on_flash is running")
        logger.info("on_flash: Would show you a progress bar.")
        self.ft_plugin.flash(self)

    def add_page_to_stack(self, content, name, nav_buttons):
        logger.debug("add_page_to_stack is running")
        # Create a box to hold the navigation buttons
        navigation_button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        navigation_button_box.set_hexpand(True)
        navigation_button_box.set_vexpand(True)
        navigation_button_box.set_halign(Gtk.Align.CENTER)
        navigation_button_box.set_valign(Gtk.Align.START)
        padding = (0, 0, 10, 0)
        self.set_padding(navigation_button_box, padding)

        # Create the navigation buttons.
        for button_desc in nav_buttons:
            title = button_desc["title"]
            command = button_desc["command"]
            button = self.create_button(
                title,
                column=0,
                row=0,
                command=command,
            )
            button.set_hexpand(True)
            button.set_vexpand(True)
            button.add_css_class("pill")
            navigation_button_box.append(button)
            # button.add_css_class("suggested-action")

        main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        main_box.append(content)
        main_box.append(navigation_button_box)

        # Create an adw.clamp to limit the button box size
        clamp = Adw.Clamp.new()
        clamp.set_child(main_box)
        clamp.set_maximum_size(800)

        # Create header bar
        header_bar = Adw.HeaderBar()
        header_bar.set_show_title(False)

        # Create toolbar view
        toolbar_view = Adw.ToolbarView.new()
        toolbar_view.add_top_bar(header_bar)
        toolbar_view.set_content(clamp)

        # Create the page
        self.stack.add_named(toolbar_view, name)

    def remove_ansi_escape_sequences(self, string):
        logger.debug("remove_ansi_escape_sequences is running")
        cleaned_string = self.shared_utils.remove_ansi_escape_sequences(string)
        return cleaned_string

    def remove_newlines(self, string):
        logger.debug("remove_newlines is running")
        cleaned_string = self.shared_utils.remove_newlines(string)
        return cleaned_string

    def on_width_breakpoint_applied(self, breakpoint):
        logger.debug("on_width_breakpoint_applied is running")
        self.header_bar.set_title_widget(self.window_title)

    def on_width_breakpoint_unapplied(self, breakpoint):
        logger.debug("on_width_breakpoint_unapplied is running")
        self.header_bar.set_title_widget(self.view_switcher)

    def set_setting(self, setting, value):
        logger.debug("set_setting is running")
        if setting == "theme":
            self.set_theme(value)
        self.settings[setting] = value
        logger.info(f"set_setting: {setting} set to: '{value}'")
        shared_utils.save_settings(self.settings, settings_file)

    def set_theme(self, theme):
        logger.debug("set_theme is running")
        if theme == "system":
            color_scheme = Adw.ColorScheme.PREFER_LIGHT
        elif theme == "light":
            color_scheme = Adw.ColorScheme.FORCE_LIGHT
        elif theme == "dark":
            color_scheme = Adw.ColorScheme.FORCE_DARK
        else:
            logger.error(
                "set_theme: The theme argument can be either "
                f'"system", "light", or "dark". Not "{theme}".'
            )
            return
        self.style_manager.set_color_scheme(color_scheme)

    def set_widget_state(self, *args, state=True):
        logger.debug("set_widget_state is running")
        for widget in args:
            widget.set_sensitive(state)

    def open_file(self, file_type):
        logger.debug("open_file is running")
        def file_dialog_callback(obj, result):
            try:
                file = obj.open_finish(result)
                if file:
                    file_path = file.get_path()
                    file_name = file.get_basename()
                    logger.info(f"open_file: Selected file: {file_path}")

                    file_type_lowered = file_type.lower()
                    self.selected_files[file_type_lowered] = file_path
                    file_button = getattr(self, f"{file_type}_button")
                    button_label = file_button.get_label()
                    button_row_box = file_button.get_parent()

                    # if ":" in button_label:
                    if button_label != file_type:
                        new_label = f'{file_type}: "{file_name}"'
                        file_button.set_label(new_label)
                    else:
                        new_label = f'{button_label}: "{file_name}"'
                        file_button.set_label(new_label)

                        close_button = Gtk.Button.new_from_icon_name("window-close")
                        close_button.set_halign(Gtk.Align.CENTER)
                        close_button.set_valign(Gtk.Align.CENTER)
                        # close_button.set_hexpand(True)
                        # close_button.set_vexpand(True)
                        close_button.add_css_class("circular")
                        # close_button.add_css_class("pill")
                        close_button.add_css_class("destructive-action")
                        close_button.signal_id = close_button.connect(
                            "clicked",
                            lambda button=file_button, file_type=file_type: self.remove_file(
                                button, file_type
                            ),
                        )
                        button_row_box.append(close_button)

            except GLib.Error as e:
                # If the user cancelled, pass.
                if e.code == 2:
                    pass
                else:
                    logger.error(f"open_file: {e}")

        file_dialog = Gtk.FileDialog(title=f"Select a {file_type} file")
        odin_filter = Gtk.FileFilter()
        odin_filter.set_name("Odin files")
        odin_filter.add_mime_type("application/x-tar")
        odin_filter.add_pattern("*.tar.md5")
        odin_filter.add_pattern("*.tar")
        filter_list = Gio.ListStore.new(Gtk.FileFilter)
        filter_list.append(odin_filter)
        file_dialog.set_filters(filter_list)
        file_dialog.open(self, None, file_dialog_callback)

    def remove_file(self, close_button, file_type):
        logger.debug("remove_file is running")
        file_type_lowered = file_type.lower()
        self.selected_files.pop(file_type_lowered)
        logger.info(f"remove_file: Removing {file_type} file")
        button_row_box = close_button.get_parent()
        close_button = button_row_box.get_last_child()
        file_button = button_row_box.get_first_child()
        button_row_box.remove(close_button)
        button_label = file_button.get_label()
        #file_type = button_label.split(': ', 1)[0]
        file_button.set_label(file_type)

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
        logger.debug("create_label is running")
        label = Gtk.Label()
        self.set_padding(label, padding)
        label.set_markup(f'<span font_desc="{font[0]} {font[1]}">{text}</span>')
        label.set_halign(align)
        grid.attach(label, column, row, width, height)
        return label

    def create_button(
        self,
        label,
        column,
        row,
        command,
        grid=None,
        padding=(0, 0, 0, 0),
        width=1,
        height=1,
    ):
        logger.debug("create_button is running")
        button = Gtk.Button(label=label)
        self.set_padding(button, padding)
        button.signal_id = button.connect("clicked", command)
        if grid:
            grid.attach(button, column, row, width, height)
        return button

    # Given a widget, prints it's widget tree.
    def print_widget_tree(
        self, widget, indent_str: str = "", top_level: bool = True
    ) -> None:
        logger.debug("print_widget_tree is running")
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
        logger.debug("create_switch_row is running")
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
        logger.debug("create_combo_row is running")
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
        logger.debug("create_expander_row is running")
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
        logger.debug("add_custom_expander_row_label is running")
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
        logger.debug("create_action_row is running")
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
        logger.debug("create_preferences_dialog is running")
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
                    logger.error(
                        'create_preferences_dialog: The "type" arg must be specified.'
                    )
                    break
                if not row_setting:
                    logger.error(
                        'create_preferences_dialog: The "setting" arg must be specified.'
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
                    logger.error(
                        f'create_preferences_dialog: "{row_type}" is not a valid type. Valid types are "switch", "combo", and "expander".'
                    )
        preferences_dialog.present(self)

    def on_action_row_checkbutton_clicked(
        self, action_row, check_button, setting, value
    ):
        logger.debug("on_action_row_checkbutton_clicked is running")
        if check_button.get_active():
            expander_row = getattr(self, f"{setting}_expander_row")
            expander_row.added_label.set_label(action_row.get_title())
            self.set_setting(setting, value)

    def on_action_row_file_button_clicked(self, action_row, setting, name, value):
        logger.debug("on_action_row_file_button_clicked is running")
        if setting == "flash_tool":
            name = "Pythor" if value == "pythor" else name

            def file_dialog_callback(obj, result):
                try:
                    file = obj.open_finish(result)
                    if file:
                        file_path = file.get_path()
                        logger.info(f"on_action_row_file_button_clicked: Selected {name} executable: {file_path}")
                        self.set_setting(f"{value}_file", file_path)
                        action_row.set_activatable_widget(action_row.check_button)
                        action_row.set_subtitle(file_path)
                        action_row.do_activate(action_row)

                except GLib.Error as e:
                    # If the user cancelled, pass.
                    if e.code == 2:
                        pass
                    else:
                        logger.error(f"on_action_row_file_button_clicked: {e}")

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
        logger.debug("on_info_button_clicked is running")
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
        logger.debug("on_switch_row_changed is running")
        value = switch.get_active()
        self.set_setting(setting, value)

    def on_combo_row_changed(self, combo_row, value_list, setting):
        logger.debug("on_combo_row_changed is running")
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
        logger.debug("create_alert_dialog is running")
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
        logger.debug("change_button_command is running")
        button.disconnect(button.signal_id)
        button.signal_id = button.connect("clicked", new_command)

    def create_entry(
        self, column, row, grid, padding=(0, 0, 0, 0), width=1, height=1, expand=False
    ):
        logger.debug("create_entry is running")
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
        grid=None,
        column=0,
        row=0,
        padding=(0, 0, 0, 0),
        align=Gtk.Align.START,
        width=1,
        height=1,
    ):
        logger.debug("create_checkbutton is running")
        check_button = Gtk.CheckButton(label=label)
        self.set_padding(check_button, padding)
        check_button.set_halign(align)
        if grid:
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
        logger.debug("create_radiobuttons is running")
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
        logger.debug("create_toggle_switch is running")
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
        logger.debug("set_padding is running")
        widget.set_margin_start(padding[0])
        widget.set_margin_end(padding[1])
        widget.set_margin_top(padding[2])
        widget.set_margin_bottom(padding[3])

    def create_about_dialog(self, *_):
        logger.debug("create_about_dialog is running")
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
        self.win.set_default_size(600, 600)
        self.win.present()


if __name__ == "__main__":
    app = GalaxyFlasherGtk(application_id="com.ethicalhaquer.galaxyflasher")
    app.run(sys.argv)
