#!/usr/bin/env python3

import json
import os
import datetime
import pathlib
import locale
import re

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


def load_strings(locale_file):
    """Load strings from a specified JSON file.

    Args:
        locale_file (str): The JSON file to load the stringgs from.

    Returns:
        dict: The strings contained in the file.
    """
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
    file_path = pathlib.Path(file)
    return file_path.is_file()


def load_settings(settings_file):
    """Load settings from the specified JSON file.

    Args:
        settings_file (str): The JSON file to load the settings from.

    Returns:
        dict: The settings contained in the file.
    """
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
    # pattern = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    pattern = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    cleaned_string = pattern.sub("", string)
    return cleaned_string


def remove_newlines(string):
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
    #logger.debug(f'cycle: output: "{repr(output)}"')
    cleaned_output = remove_ansi_escape_sequences(output)
    #logger.debug(f'cycle: semi_cleaned: "{repr(cleaned_output)}"')
    output_lines = cleaned_output.splitlines()
    #logger.debug(f'cycle: output_lines: "{repr(output_lines)}"')
    stripped_lines = [line.strip() for line in output_lines]
    #logger.debug(f'cycle: stripped_lines: "{repr(stripped_lines)}"')
    return stripped_lines

def list_to_string(input_list, separator=""):
    string = separator.join(input_list)
    return string

def get_current_year():
    """Returns the current year.

    Returns:
        str: The current year.
    """
    return datetime.date.today().year


def open_link(link):
    """Opens a link in the user's preferred browser.

    Args:
        link (str): The link to open.
    """
    launcher = Gtk.UriLauncher.new(link)
    launcher.launch()


def get_system_lang():
    """Returns the lowercase, two-letter abbreviation code of the system language.

    Returns:
        str: The lowercase, two-letter abbreviation code of the system language.
    """
    locale.setlocale(locale.LC_ALL, "")
    system_locale = locale.getlocale(locale.LC_MESSAGES)[0]
    separator = "_"
    lang = system_locale.split(separator, 1)[0]
    return lang


def get_is_flatpak():
    is_flatpak = "FLATPAK_ID" in os.environ or "FLATPAK_APP_ID" in os.environ
    return is_flatpak
