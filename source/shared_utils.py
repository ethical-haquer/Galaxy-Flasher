#!/usr/bin/env python3
# shared_utils.py

import json
import os
import datetime
import pathlib
import locale
import re
import logging

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject, Gio  # noqa: E402

logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger("shared_utils")


# Huge thanks to https://discourse.gnome.org/t/how-do-you-run-a-blocking-method-asynchronously-with-gio-task-in-a-python-gtk-app/10651
class AsyncWorker(GObject.Object):
    """A class for performing asynchronous operations using Gio.Task."""

    def __init__(
        self,
        async_operation=None,
        operation_inputs=(),
        operation_callback=None,
        operation_callback_inputs=(),
        cancellable=None,
    ):
        super().__init__()
        self.async_operation = async_operation
        self.operation_inputs = operation_inputs
        self.operation_callback = operation_callback
        self.operation_callback_inputs = operation_callback_inputs
        self.cancellable = cancellable

        self.task_pool = {}

    def start(self) -> None:
        """Start the asynchronous operation."""
        logger.info("Starting asynchronous operation...")
        task = Gio.Task.new(
            self,
            self.cancellable,
            self.operation_callback,
            self.operation_callback_inputs,
        )
        if self.cancellable is None:
            task.set_return_on_cancel(False)

        data_id = id(self.operation_inputs)
        self.task_pool[data_id] = self.operation_inputs
        task.set_task_data(data_id, lambda key: self.task_pool.pop(data_id))

        task.run_in_thread(self._thread_callback)

    def _thread_callback(
        self,
        task: Gio.Task,
        source_object: GObject.Object,
        task_data,
        cancellable: Gio.Cancellable,
    ) -> None:
        """A callback function run in a separate thread."""
        logger.debug("Running blocking operation in worker thread")
        try:
            data_id = task.get_task_data()
            data = self.task_pool.get(data_id)

            if self.async_operation is None:
                outcome = self.work(*data)
            else:
                outcome = self.async_operation(*data)

            task.return_value(outcome)
        except Exception as e:
            logger.error(f"Error occurred in worker thread: {e}")

    def return_value(self, result: Gio.Task):
        """Return the value of the asynchronous operation."""
        logger.debug("Returning value of the asynchronous operation")
        value = None

        if Gio.Task.is_valid(result, self):
            value = result.propagate_value().value
        else:
            error = "Gio.Task.is_valid returned False."
            value = {"AsyncWorkerError": error}
            logger.error(f"Error: {error}")

        return value


def load_strings(locale_file):
    """Load strings from a specified JSON file.

    Args:
        locale_file (str): The JSON file to load the strings from.

    Returns:
        dict: The strings contained in the file.
    """
    logger.debug("load_strings is running")
    with open(locale_file) as json_string:
        strings = json.load(json_string)
    return strings


def get_locale_file(swd, lang):
    """Get the location of the locale file.

    Args:
        swd (str): The script working directory.
        lang (str): The lowercase, two-letter abbreviation code of a language.

    Returns:
        str: The path to the locale file, which may or may not exist.
    """
    logger.debug("get_locale_file is running")
    locale_file = f"{swd}/locales/{lang}.json"
    if file_exists(locale_file):
        return locale_file
    else:
        return f"{swd}/locales/en.json"


def file_exists(file):
    """Checks if a file exists.
    Returns True if it does, or False if it doesn't.

    Args:
        file (str): The file to check for.

    Returns:
        bool: Whether the file exists or not.
    """
    logger.debug("file_exists is running")
    file_path = pathlib.Path(file)
    return file_path.is_file()


def load_settings(settings_file):
    """Load settings from the specified JSON file.

    Args:
        settings_file (str): The JSON file to load the settings from.

    Returns:
        dict: The settings contained in the file.
    """
    logger.debug("load_settings is running")
    settings = {}
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            settings = json.load(file)
    return settings


def save_settings(settings, settings_file):
    """Save settings to the specified JSON file.

    Args:
        settings (dict): The settings to save.
        settings_file (str): The JSON file to save the settings to.
    """
    logger.debug("save_settings is running")
    with open(settings_file, "w") as file:
        json.dump(settings, file)


def shorten_string(string, length):
    """Shorten a string to a given length.

    Args:
        string (str): The string to shorten.
        length (int): The length to shorten it to.

    Returns:
        str: The shortened string.
    """
    logger.debug("shorten_string is running")
    current_length = len(string)
    if current_length > length:
        shortened_string = string[: length - 3] + "..."
    else:
        shortened_string = string
    return shortened_string


def remove_blank_lines(string):
    """Remove blank lines from a string.

    Args:
        string (str): The string.

    Returns:
        str: The string, without blank lines.
    """
    logger.debug("remove_blank_lines is running")
    lines = string.splitlines()
    filtered_lines = [line for line in lines if line.strip()]
    new_string = "\n".join(filtered_lines)
    return new_string


def remove_ansi_escape_sequences(string):
    """Remove ANSI escape sequences from a string.

    Args:
        string (str): The input string containing ANSI escape sequences.

    Returns:
        str: The input string with ANSI escape sequences removed.
    """
    logger.debug("remove_ansi_escape_sequences is running")
    # pattern = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    pattern = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    cleaned_string = pattern.sub("", string)
    return cleaned_string


def remove_newlines(string):
    logger.debug("remove_newlines is running")
    cleaned_string = "".join(string.split())
    return cleaned_string


def clean_output(output):
    """
    Given (very) messy output, returns a list of cleaned output. Here's an example:
    Input: "\x1b[0m                                 \r\x1b[2K\x1b[1A\x1b[2K\x1b[1
    A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2
    K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[?25h\x1b[?25l\x1b[38;5;2mChoo
    se what partitions to flash from \x1b[0m
    \r\n\x1b[38;5;2mCP_G900AUCS4DPH4_CL8903521_QB11143142_REV00_user_low_ship_MUL
    TI_CERT.tar.md5:\x1b[0m\r\n\r\n\x1b[38;5;12m> [ ] modem.bin (MODEM)\x1b[0m
    \r\n
    \r\n\x1b[38;5;8m"

    Output: ['', 'Choose what partitions to flash from', 'CP_G900AUCS4DPH4_CL8903
    521_QB11143142_REV00_user_low_ship_MULTI_CERT.tar.md5:', '', '> [ ] modem.bin (MODEM)', '']
    """
    logger.debug("clean_output is running")
    # logger.debug(f'cycle: output: "{repr(output)}"')
    cleaned_output = remove_ansi_escape_sequences(output)
    # logger.debug(f'cycle: semi_cleaned: "{repr(cleaned_output)}"')
    output_lines = cleaned_output.splitlines()
    # logger.debug(f'cycle: output_lines: "{repr(output_lines)}"')
    # Only include lines that aren't an empty string.
    stripped_lines = [line.strip() for line in output_lines if line.strip()]
    # logger.debug(f'cycle: stripped_lines: "{repr(stripped_lines)}"')
    return stripped_lines


def list_to_string(input_list, separator=""):
    logger.debug("list_to_string is running")
    string = separator.join(input_list)
    return string


def get_current_year():
    """Returns the current year.

    Returns:
        str: The current year.
    """
    logger.debug("get_current_year is running")
    return datetime.date.today().year


def open_link(link):
    """Opens a link in the user's preferred browser.

    Args:
        link (str): The link to open.
    """
    logger.debug("open_link is running")
    launcher = Gtk.UriLauncher.new(link)
    launcher.launch()


def get_system_lang():
    """Returns the lowercase, two-letter abbreviation code of the system language.

    Returns:
        str: The lowercase, two-letter abbreviation code of the system language.
    """
    logger.debug("get_system_lang is running")
    locale.setlocale(locale.LC_ALL, "")
    system_locale = locale.getlocale(locale.LC_MESSAGES)[0]
    separator = "_"
    lang = system_locale.split(separator, 1)[0]
    return lang


def get_is_flatpak():
    logger.debug("get_is_flatpak is running")
    is_flatpak = "FLATPAK_ID" in os.environ or "FLATPAK_APP_ID" in os.environ
    return is_flatpak


def setup_logger(name):
    logging.basicConfig(
        format="%(levelname)s: %(name)s: %(message)s", level=logging.DEBUG
    )
    logger = logging.getLogger(name)
    return logger
