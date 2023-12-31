'''
Thor GUI - A GUI for the Thor Flash Utility
Copyright (C) 2023  ethical_haquer

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
'''

import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import pexpect
from threading import Thread
import re
import webbrowser
from time import sleep
import tarfile
import os
from functools import partial
import zipfile
from collections import deque
import sv_ttk
from tkinter import ttk
import pickle
import sys
from tktooltip import ToolTip
from tkinterdnd2 import DND_FILES, TkinterDnD
import platform
from threading import Timer
import typing as typ

version = 'Alpha v0.4.3'

path_to_thor_gui = os.path.dirname(os.path.abspath(sys.argv[0]))
currently_running = False
odin_running = False
Thor = None
connection = False
tag = 'green'
graphical_flash = False
prompt_available = False
sudo_prompt_available = False
operating_system = platform.system()
architecture = platform.machine()

successful_commands = []

odin_archives = []

tooltip_dict = {
    'Start_Button': 'Start Thor',
    'Connect_Button': 'Connect a device in download mode',
    'Begin_Button': 'Start an Odin session',
    'Command_Entry': 'You can enter a Thor command here,\nand press enter to send it',
    'Enter_Button': "Send Thor an 'Enter'",
    'Space_Button': "Send Thor a 'Space'",
    'Page_Up_Button': "Send Thor a 'Page Up'",
    'Page_Down_Button': "Send Thor a 'Page Down'",
    'BL_Checkbutton': 'The Odin archives selected with these check-boxes will be flashed',
    'AP_Checkbutton': 'The Odin archives selected with these check-boxes will be flashed',
    'CP_Checkbutton': 'The Odin archives selected with these check-boxes will be flashed',
    'CSC_Checkbutton': 'The Odin archives selected with these check-boxes will be flashed',
    'USERDATA_Checkbutton': 'The Odin archives selected with these check-boxes will be flashed',
    'BL_Button': 'Select a BL file',
    'AP_Button': 'Select an AP file',
    'CP_Button': 'Select a CP file',
    'CSC_Button': 'Select a CSC file',
    'USERDATA_Button': 'Select a USERDATA file',
    'BL_Entry': "Drag and drop a BL file here, or paste it's path",
    'AP_Entry': "Drag and drop an AP file here, or paste it's path",
    'CP_Entry': "Drag and drop a CP file here, or paste it's path",
    'CSC_Entry': "Drag and drop a CSC file here, or paste it's path",
    'USERDATA_Entry': "Drag and drop a USERDATA file here, or paste it's path",
    'Log_Button': 'Log Tab',
    'Options_Button': 'Options Tab',
    'Pit_Button': 'Pit Tab',
    'Settings_Button': 'Settings Tab',
    'Help_Button': 'Help Tab',
    'About_Button': 'About Tab',
    'Apply_Options_Button': 'Apply the above options',
    'Theme_Checkbutton': 'Toggle Theme',
    'Tooltip_Checkbutton': 'Toggle Tooltips',
    'Thor_Checkbutton': 'Toggle using an internal/external Thor build',
    'Thor_Entry': 'Thor GUI will look for the external Thor build in this directory',
    'Sudo_Checkbutton': 'Toggle running Thor with/without sudo',
    'Default_Directory_Entry': 'The file picker will open to this directory',
    'Start_Flash_Button': 'Start a flash',
    'Reset_Button': 'Reset the options in the Options Tab to defaults, and clear the Odin archive check-boxes and archive entries'
}

print(f'''
 _____ _                   ____ _   _ ___
|_   _| |__   ___  _ __   / ___| | | |_ _|
  | | | '_ \ / _ \| '__| | |  _| | | || |
  | | | | | | (_) | |    | |_| | |_| || |
  |_| |_| |_|\___/|_|     \____|\___/|___|

              {version}
''')

# Can be made smaller
# This loads the 'thor-gui-settings.pkl' file, which contains variables
if os.path.isfile(f'{path_to_thor_gui}/thor-gui-settings.pkl'):
    f2 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'rb')
    filed_version = pickle.load(f2)
    f2.close()
    if filed_version != version:
        print("The found 'thor-gui-settings.pkl' file was not created by this version of Vidar_GUI, so Thor GUI is updating it.")
        if filed_version == 'Alpha v0.4.0':
            filed_version = version
            initial_directory = '~'
            thor = "internal"
            thor_directory = "~"
            keep_dark_term = False

            f2 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'rb')
            # Has to be filed_version_2, otherwise it will overwrite the 'filed_version = version' line above
            filed_version_2 = pickle.load(f2)
            theme = pickle.load(f2)
            tooltips = pickle.load(f2)
            sudo = pickle.load(f2)
            first_run = pickle.load(f2)
            f2.close()

            f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
            pickle.dump(filed_version, f1)
            pickle.dump(theme, f1)
            pickle.dump(tooltips, f1)
            pickle.dump(sudo, f1)
            pickle.dump(initial_directory, f1)
            pickle.dump(first_run, f1)
            pickle.dump(thor, f1)
            pickle.dump(thor_directory, f1)
            pickle.dump(keep_dark_term, f1)
            f1.close()
        elif filed_version == "Alpha v0.4.1":
            filed_version = version
            thor = "internal"
            thor_directory = "~"
            keep_dark_term = False

            f2 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'rb')
            # Has to be filed_version_2, otherwise it will overwrite the 'filed_version = version' line above
            filed_version_2 = pickle.load(f2)
            theme = pickle.load(f2)
            tooltips = pickle.load(f2)
            sudo = pickle.load(f2)
            initial_directory = pickle.load(f2)
            first_run = pickle.load(f2)
            f2.close()

            f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
            pickle.dump(filed_version, f1)
            pickle.dump(theme, f1)
            pickle.dump(tooltips, f1)
            pickle.dump(sudo, f1)
            pickle.dump(initial_directory, f1)
            pickle.dump(first_run, f1)
            pickle.dump(thor, f1)
            pickle.dump(thor_directory, f1)
            pickle.dump(keep_dark_term, f1)
            f1.close()
        elif filed_version == "Alpha v0.4.2":
            filed_version = version
            keep_dark_term = False

            f2 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'rb')
            # Has to be filed_version_2, otherwise it will overwrite the 'filed_version = version' line above
            filed_version_2 = pickle.load(f2)
            theme = pickle.load(f2)
            tooltips = pickle.load(f2)
            sudo = pickle.load(f2)
            initial_directory = pickle.load(f2)
            first_run = pickle.load(f2)
            f2.close()

            f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
            pickle.dump(filed_version, f1)
            pickle.dump(theme, f1)
            pickle.dump(tooltips, f1)
            pickle.dump(sudo, f1)
            pickle.dump(initial_directory, f1)
            pickle.dump(first_run, f1)
            pickle.dump(thor, f1)
            pickle.dump(thor_directory, f1)
            pickle.dump(keep_dark_term, f1)
            f1.close()
else:
    print(f"The 'thor-gui-settings.pkl' file was not found in the directory that this program is being run from ({path_to_thor_gui}), so Thor GUI is creating it.")
    filed_version = version
    theme = 'light'
    tooltips = True
    sudo = False
    initial_directory = '~'
    first_run = True
    thor = "internal"
    thor_directory = "~"
    keep_dark_term = False
    f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
    pickle.dump(filed_version, f1)
    pickle.dump(theme, f1)
    pickle.dump(tooltips, f1)
    pickle.dump(sudo, f1)
    pickle.dump(initial_directory, f1)
    pickle.dump(first_run, f1)
    pickle.dump(thor, f1)
    pickle.dump(thor_directory, f1)
    pickle.dump(keep_dark_term, f1)
    f1.close()

f2 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'rb')
filed_version = pickle.load(f2)
theme = pickle.load(f2)
tooltips = pickle.load(f2)
sudo = pickle.load(f2)
initial_directory = pickle.load(f2)
first_run = pickle.load(f2)
thor = pickle.load(f2)
thor_directory = pickle.load(f2)
keep_dark_term = pickle.load(f2)
f2.close()

# This starts and stops Thor
def start_thor():
    global Thor, output_thread, currently_running, prompt_available, sudo, start_button_message, thor, thor_directory
    try:
        if currently_running:
            on_window_close()
        elif not currently_running:
            if thor == "internal":
                if sudo == False:
                    if architecture == 'x86_64':
                        Thor = pexpect.spawn(f'{path_to_thor_gui}/Thor/linux-x64/TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
                    elif architecture == 'arm64' or architecture == "aarch64":
                        Thor = pexpect.spawn(f'{path_to_thor_gui}/Thor/linux-arm64/TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
                    else:
                        print(f"The {architecture} architecture is currently not supported by Thor GUI. If you think the {architecture} architecture should be supported, feel free to open a feature request on GitHub.")
                        show_message('Unsupported architecture', f'The {architecture} architecture is currently not supported by Thor GUI.\nIf you think the {architecture} architecture should be supported, feel free to open a feature request on GitHub.', [{'text': 'OK', 'fg': 'black'}], window_size=(700, 140))
                        return
                elif sudo == True:
                    if architecture == 'x86_64':
                        Thor = pexpect.spawn(f'sudo {path_to_thor_gui}/Thor/linux-x64/TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
                    elif architecture == 'arm64' or architecture == "aarch64":
                        Thor = pexpect.spawn(f'sudo {path_to_thor_gui}/Thor/linux-arm64/TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
                    else:
                        print(f"The {architecture} architecture is currently not supported by Thor GUI. If you think the {architecture} architecture should be supported, feel free to open a feature request on GitHub.")
                        show_message('Unsupported architecture', f'The {architecture} architecture is currently not supported by Thor GUI.\nIf you think the {architecture} architecture should be supported, feel free to open a feature request on GitHub.', [{'text': 'OK', 'fg': 'black'}], window_size=(700, 140))
                        return
            elif thor == "external":
                thor_path = Thor_Entry.get()
                if thor_path[-1] != "/" and thor_path != '~':
                    thor_path = thor_path + "/"
                if thor_path == '~' or os.path.isdir(thor_path) == True:
                    if os.path.isfile(f'{thor_path}/TheAirBlow.Thor.Shell'):
                        thor_directory = thor_path
                    else:
                        print(f'Invalid Path to Thor - The directory: "{thor_path}" does not contain a Thor build, in particular the "TheAirBlow.Thor.Shell" file. You can set the path to your external Thor build by going to: Settings - Thor - Path to external Thor build')
                        show_message('Invalid Path to Thor', f'The directory: \'{thor_path}\' does not contain a Thor build, in particular the\n"TheAirBlow.Thor.Shell" file.\nYou can set the path to your external Thor build by going to:\nSettings - Thor - Path to external Thor build', [{'text': 'OK', 'fg': 'black'}], window_size=(500, 160))
                        return
                else:
                    print(f'Invalid Path to Thor - The directory: \'{thor_path}\' does not exist. You can set the path to your external Thor build by going to: Settings - Thor - Path to external Thor build')
                    show_message('Invalid Path to Thor', f'The directory: \'{thor_path}\' does not exist.\nYou can set the path to your external Thor build by going to:\nSettings - Thor - Path to external Thor build', [{'text': 'OK', 'fg': 'black'}], window_size=(500, 140))
                    return
                if sudo == False:
                    Thor = pexpect.spawn(f'{thor_directory}TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
                elif sudo == True:
                    Thor = pexpect.spawn(f'sudo {thor_directory}TheAirBlow.Thor.Shell', timeout=None, encoding='utf-8')
            if Thor == None:
                raise Exception('Thor GUI was unable to start Thor because Thor == None. Feel free to open an issue for this on GiHub. TIA.')
            output_thread = Thread(target=update_output)
            output_thread.daemon = True
            output_thread.start()
            currently_running = True
            Start_Button.configure(text='Stop Thor')
            tooltip_manager.change_tooltip(Start_Button, 'Stop Thor')
            print('Started Thor')
    except pexpect.exceptions.TIMEOUT:
        print('A Timeout occurred in start_thor')
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f'An Exception occurred in start_thor:\n{e}')
    except Exception as e:
        print(f'An exception occurred in start_thor:\n{e}')

# What most Thor commands go through
def send_command(command, case='normal'):
    global Thor, successful_commands, prompt_available, sudo_prompt_available
    if currently_running:
        try:
            if 'exit' in command or 'quit' in command:
                print('Sadly, stopping Thor independently is currently not supported by Thor GUI. To stop Thor, either click the: \'Stop Thor\' button (which will close the window), or close the window.')
                show_message('Unsupported command', 'Sadly, stopping Thor independently is currently not supported by Thor GUI.\nTo stop Thor, either click the: \'Stop Thor\' button (which will close the window), or close the window.', [{'text': 'OK', 'fg': 'black'}], window_size=(740, 117))
            else:
                if prompt_available == True:
                    if case == 'normal' or case == 'entry':
                        Thor.sendline(command)
                        Output_Text.see(tk.END)
                        successful_commands.append(command)
                        print(f'Sent command: \'{command}\'')
                elif sudo_prompt_available == True:
                    sudo_prompt_available = False
                    Thor.sendline(command)
                    Output_Text.see(tk.END)
                    successful_commands.append('{password}')
                    print('Sent command: \'{password}\'')
                    Command_Entry.delete(0, tk.END)
                    Command_Entry.configure(show='')
                elif clean_line.endswith('[y/n] (n):') and case == 'entry':
                    Thor.sendline(command)
                    Output_Text.see(tk.END)
                    successful_commands.append(command)
                    print(f'Sent command: \'{command}\'')
                else:
                    if case == 'entry':
                        print(f'Couldn\'t send the command: \'{command}\', as no prompt (\'shell>\', \'[y/n] (n):\') was available')
                    else:
                        print(f'Couldn\'t send the command: \'{command}\', as the \'shell>\' prompt wasn\'t available')
        except Exception as e:
            print(f'An exception occurred in send_command: {e}')

# Perhaps the most important part of the program, along with scan_output - Handles displaying the output from Thor, while scan_output calls other functions when it detects certain lines in the output
def update_output():
    global last_lines, tag, connection, clean_line
    last_lines = deque(maxlen=300)
    output_buffer = ''
    output_text_lines = []
    next_line = ''
    while True:
        try:
            chunk = Thor.read_nonblocking(4096, timeout=0)
            if chunk:
                chunk = output_buffer + chunk
                output_lines = chunk.splitlines()
                for line in output_lines:
                    mostly_clean_line = re.sub(r'\x1b\[[?0-9;]*[A-Za-z]', '', line)
                    clean_line = re.sub('\x1b=', '', mostly_clean_line).strip()

                    if clean_line.startswith(('AP', 'BL', 'CP', 'CSC', 'HOME_CSC', 'USERDATA')):
                        if clean_line.endswith(':'):
                            determine_tag(clean_line)
                            output_text_lines.append((clean_line, tag))
                            scan_output()
                            last_lines.append((clean_line, tag))
                            next_line = ''
                        else:
                            next_line = clean_line
                    elif next_line:
                        clean_line = next_line + clean_line
                        next_line = ''
                        determine_tag(clean_line)
                        output_text_lines.append((clean_line, tag))
                        scan_output()
                        last_lines.append((clean_line, tag))
                    else:
                        determine_tag(clean_line)
                        output_text_lines.append((clean_line, tag))
                        scan_output()
                        last_lines.append((clean_line, tag))

                    output_buffer = ''

        except pexpect.exceptions.TIMEOUT:
            pass
        except pexpect.exceptions.EOF:
            break
        except Exception as e:
            print(f'An exception occurred in update_output: \'{e}\'')

        # Update the Output_Text widget
        if output_text_lines:
            for line, tag in output_text_lines:
                Output_Text.configure(state='normal')
                Output_Text.insert(tk.END, line + '\n', tag)
                Output_Text.configure(state='disabled')
            Output_Text.see(tk.END)
            output_text_lines = []

        # Delay between each update
        sleep(0.1)

def scan_output():
    global graphical_flash, last_lines, clean_line, archive_name, odin_archives, prompt_available, sudo_prompt_available, first_prompt, TFlash_Option_var, EFSClear_Option_var, BootloaderUpdate_Option_var, ResetFlashCount_Option_var 
    try:
        prompt_available = False
        if 'shell>' in clean_line:
            set_thor('on')
            prompt_available = True
        elif '[sudo]' in clean_line:
            set_sudo()
            sudo_prompt_available = True
        elif 'Successfully began an Odin session!' in clean_line:
            set_odin('on')
        elif 'Successfully disconnected the device!' in clean_line:
            set_connect('off')
        elif 'Successfully connected to the device!' in clean_line:
            set_connect('on')
        elif 'Choose a device to connect to:' in clean_line and last_lines[-1][0] == 'Cancel operation':
            run_function(select_device)
        elif 'Successfully ended an Odin session!' in clean_line:
            set_odin('off')
        elif '> [ ]' in clean_line:
            if 'Choose what partitions to flash from' in last_lines[-3][0]:
                if '(Press <space> to select, <enter> to accept)' in last_lines[-4][0]:
                    found_index = None
                    for i in range(len(last_lines) - 1, -1, -1):
                        if last_lines[i][0].startswith('Choose what partitions to flash from'):
                            found_index = i
                            break
                    if found_index is not None:
                        archive_name_pre = last_lines[found_index + 1][0].rstrip(':')
                        last_flash_command = get_last_flash_tar_command()
                        archive_path = last_flash_command.split(' ')[1]
                        archive_name = os.path.basename(archive_name_pre.strip())
                        combined_file = os.path.join(archive_path, archive_name)
                        if graphical_flash == False:
                            run_function(select_partitions, archive_path, archive_name)
                            return False
                        else:
                            if combined_file in odin_archives:
                                run_function(select_partitions, archive_path, archive_name)
                                return False
                            else:
                                Thor.send('\n')
        elif 'Are you absolutely sure you want to flash those? [y/n] (n):' in clean_line:
            run_function(verify_flash)
            graphical_flash = False
        elif '\' is set to \'' in clean_line:
            if 'Option \'T-Flash\' is set to \'False\'' in clean_line:
                TFlash_Option_var = ttk.IntVar(value=False)
            if 'Option \'T-Flash\' is set to \'True\'' in clean_line:
                TFlash_Option_var = ttk.IntVar(value=True)
            if 'Option \'EFS Clear\' is set to \'False\'' in clean_line:
                EFSClear_Option_var = ttk.IntVar(value=False)
            if 'Option \'EFS Clear\' is set to \'True\'' in clean_line:
                EFSClear_Option_var = ttk.IntVar(value=True)
            if 'Option \'Bootloader Update\' is set to \'False\'' in clean_line:
                BootloaderUpdate_Option_var = ttk.IntVar(value=False)
            if 'Option \'Bootloader Update\' is set to \'True\'' in clean_line:
                BootloaderUpdate_Option_var = ttk.IntVar(value=True)
            if 'Option \'Reset Flash Count\' is set to \'False\'' in clean_line:
                ResetFlashCount_Option_var = ttk.IntVar(value=False)
            if 'Option \'Reset Flash Count\' is set to \'True\'' in clean_line:
                ResetFlashCount_Option_var = ttk.IntVar(value=True)
        elif 'Failed to open the device for RW: Permission denied (13)' in clean_line:
            run_function(show_message('Oops!', 'Thor just said:\n\'Failed to open the device for RW: Permission denied (13)\'.\n\nA possible fix is to:\n1. Go to the Settings Tab,\n2. Toggle on \'Run Thor with sudo\',\n3. Restart Thor GUI,\n4. Try connecting again.\n\nIf it still doesn\'t work, feel free to let me know!', [{'text': 'OK', 'fg': 'black'}], (460, 252)))
    except Exception as e:
        print(f'An exception occurred in scan_output: \'{e}\'')

# Handles coloring the output, as the original ANSI escape sequences are stripped out
def determine_tag(line):
    global tag
    green = [
        'Total commands: 11',
        'Choose a device to connect to:',
        'Choose what partitions to flash from',
        'Successfully connected to the device!',
        'Successfully disconnected the device!',
        'Successfully began an Odin session!',
        'Successfully ended an Odin session!',
        'Option \'',
        'Successfully set \'',
        'Total protocol commands: 11',
        'You chose to flash '
    ]
    yellow = [
        '~~~~~~~~ Platform specific notes ~~~~~~~~',
        '[required] {optional} - option list',
        'Are you absolutely sure you want to flash those? [y/n] (n):'
    ]
    blue = [
        'exit - Closes the shell, quit also works'
    ]
    orange = [
        'Cancel operation'
    ]
    dark_blue = [

    ]
    red = [
        '~~~~~~~^'
    ]
    green_italic = [
        'Note: beginning a protocol session unlocks new commands for you to use'
    ]
    if line.startswith('Welcome to Thor Shell v1.0.4!'):
        Output_Text.configure(state='normal')
        Output_Text.delete('1.0', 'end')
        Output_Text.configure(state='disabled')
        tag = 'green'
    elif line.startswith('shell>'):
        tag = 'default_tag'
    elif 'Phone [' in line:
        tag = 'dark_blue'
    elif line in green:
        tag = 'green'
    elif line in yellow:
        tag = 'yellow'
    elif line in blue:
        tag = 'blue'
    elif line in orange:
        tag = 'orange'
    elif line in dark_blue:
        tag = 'dark_blue'
    elif line in red:
        tag = 'red'
    elif line in green_italic:
        tag = 'green_italic'

# Figures out what the last 'flashTar' command run was
def get_last_flash_tar_command():
    global successful_commands
    for command in reversed(successful_commands):
        if command.startswith('flashTar'):
            return command
    return None

# Deals with enabling/disabling buttons - Mainly used by set_thor(), set_connect(), and set_odin()
def set_widget_state(*args, state='normal', text=None):
    for widget in args:
        widget.configure(state=state, text=text)
        if text is not None:
            widget.configure(text=text)
            
# Tells the program when the user is running Thor with sudo and needs to enter their password
def set_sudo():
    Command_Entry.configure(show='*')
    Command_Entry.focus_set()
    set_widget_state(Command_Entry)

# Tells the program whether Thor is running or not
def set_thor(value):
    if value == 'on':
        set_widget_state(Connect_Button, Command_Entry, Page_Up_Button, Page_Down_Button, Enter_Button, Space_Button)
    elif value == 'off':
        set_widget_state(Connect_Button, Command_Entry, Page_Up_Button, Page_Down_Button, Enter_Button, Space_Button, state='disabled')
        set_connect('off')

# Tells the program whether a device is connected or not
def set_connect(value):
    global connection
    if value == 'on':
        if connection == False:
            set_widget_state(Connect_Button, text='Disconnect')
            tooltip_manager.change_tooltip(Connect_Button, 'Disconnect a device in download mode')
            Begin_Button.configure(state='normal')
            connection = True
    elif value == 'off':
        if connection == True:
            set_odin('off')
            Connect_Button.configure(text='Connect device')
            tooltip_manager.change_tooltip(Connect_Button, 'Connect a device in download mode')
            Begin_Button.configure(state='disabled')
            connection = False

# Tells the program whether an Odin session is running or not
def set_odin(value):
    global odin_running
    if value == 'on':
        if odin_running == False:
            Begin_Button.configure(text='End Odin Protocol')
            tooltip_manager.change_tooltip(Begin_Button, 'Stop an Odin session')
            set_widget_state(Apply_Options_Button, Start_Flash_Button)
            odin_running = True
    elif value == 'off':
        if odin_running == True:
            Begin_Button.configure(text='Start Odin Protocol')
            tooltip_manager.change_tooltip(Begin_Button, 'Start an Odin session')
            set_widget_state(Apply_Options_Button, Start_Flash_Button, state='disabled')
            odin_running == False

# Handles connecting / disconnecting devices
def toggle_connection():
    global currently_running
    global connection
    try:
        if currently_running:
            if not connection:
                send_command('connect')
            elif connection:
                send_command('disconnect')
    except Exception as e:
        print(f'An exception occurred in toggle_connection: {e}')

# This starts and stops the Odin protocol
def toggle_odin():
    global currently_running
    global odin_running
    try:
        if currently_running:
            if not odin_running:
                send_command('begin odin')
            elif odin_running:
                send_command('end')
    except Exception as e:
        print(f'An exception occurred in toggle_odin: {e}')

# Sets the 'Options' back to default and resets the Odin archive Check-buttons/Entries
def reset():
    global currently_running
    try:
#        TFlash_Option_var.set(False)
        EFSClear_Option_var.set(False)
        BootloaderUpdate_Option_var.set(False)
        ResetFlashCount_Option_var.set(True)
        BL_Checkbutton_var.set(False)
        AP_Checkbutton_var.set(False)
        CP_Checkbutton_var.set(False)
        CSC_Checkbutton_var.set(False)
        USERDATA_Checkbutton_var.set(False)
        BL_Entry.delete(0, 'end')
        AP_Entry.delete(0, 'end')
        CP_Entry.delete(0, 'end')
        CSC_Entry.delete(0, 'end')
        USERDATA_Entry.delete(0, 'end')
    except Exception as e:
        print(f'An exception occurred in reset: {e}')

# Moves the correct frame to the top
def toggle_frame(name):
    frame_name = name + '_Frame'
    button_name = name + '_Button'
    frame = globals()[frame_name]
    button = globals()[button_name]
    frame.lift()
    buttons = [Log_Button, Options_Button, Pit_Button, Settings_Button, Help_Button, About_Button]
    for btn in buttons:
        if btn == button:
            btn.grid_configure(pady=0)
        else:
            btn.grid_configure(pady=5)

# Handles setting the options
# NOTE: The T Flash option is currently disabled
def apply_options():
#    tflash_status = TFlash_Option_var.get()
    efs_clear_status = EFSClear_Option_var.get()
    bootloader_update_status = BootloaderUpdate_Option_var.get()
    reset_flash_count_status = ResetFlashCount_Option_var.get()

#    if tflash_status == 1:

    if efs_clear_status == 1:
        Thor.sendline('options efsclear true')

    elif efs_clear_status == 0:
        Thor.sendline('options efsclear false')

    if bootloader_update_status == 1:
        Thor.sendline('options blupdate true')

    elif bootloader_update_status == 0:
        Thor.sendline('options blupdate false')

    if reset_flash_count_status == 1:
        Thor.sendline('options resetfc true')

    elif reset_flash_count_status == 0:
        Thor.sendline('options resetfc false')

# Runs functions in the main thread
def run_function(function, *args):
    window.after(0, function, *args)

# Runs the 'flashTar' command when the 'Start' button is clicked
def start_flash():
    global currently_running, odin_archives, graphical_flash
    try:
        checkboxes = [
            (BL_Checkbutton_var, BL_Entry, 'BL'),
            (AP_Checkbutton_var, AP_Entry, 'AP'),
            (CP_Checkbutton_var, CP_Entry, 'CP'),
            (CSC_Checkbutton_var, CSC_Entry, 'CSC'),
            (USERDATA_Checkbutton_var, USERDATA_Entry, 'USERDATA')
        ]
        odin_archives = []
        unique_directories = set()

        def validate_file(file_path, file_type):
            if os.path.exists(file_path):
                if file_path.endswith(('.tar', '.zip', '.md5')):
                    return True
                else:
                    print(f'Invalid {file_type} file selected - Files must be .tar, .zip, or .md5')
                    show_message('Invalid file', 'Files must be .tar, .zip, or .md5', [{'text': 'OK'}], window_size=(400, 100))
            else:
                print(f'Invalid {file_type} file selected - The file does not exist')
                show_message('Invalid file', f'The selected {file_type} file does not exist', [{'text': 'OK'}], window_size=(400, 100))
            return False

        for checkbox_var, entry, file_type in checkboxes:
            if checkbox_var.get():
                file_path = entry.get()
                if not validate_file(file_path, file_type):
                    return False
                odin_archives.append(file_path)
                unique_directories.add(os.path.dirname(file_path))

        if len(odin_archives) == 0:
            print('No files were selected - Please select at least one file')
            show_message('No files selected', 'Please select at least one file', [{'text': 'OK', 'fg': 'black'}], window_size=(400, 100))
            return False

        if len(unique_directories) > 1:
            print('Invalid files - All selected files must be in the same directory')
            show_message('Invalid files', 'All selected files must be in the same directory', [{'text': 'OK', 'fg': 'black'}], window_size=(400, 100))
            return False

        common_directory = unique_directories.pop()
        graphical_flash = True
        send_command(f'flashTar {common_directory}')

    except Exception as e:
        print(f'An exception occurred in start_flash: {e}')

    return True

# Opens message-boxes - Used by start_flash
def show_message(title, message, buttons, window_size=(300, 100)):
    global Message_Window

    Message_Window = tk.Toplevel(window)
    Message_Window.title(title)
    Message_Window.wm_transient(window)
    Message_Window.grab_set()
    Message_Window.update_idletasks()

    width, height = window_size
    x = window.winfo_rootx() + (window.winfo_width() - width) // 2
    y = window.winfo_rooty() + (window.winfo_height() - height) // 2
    Message_Window.geometry(f'{width}x{height}+{x}+{y}')
    Message_Window.grid_columnconfigure(0, weight=1)
#    Message_Window.grid_rowconfigure(0, weight=1)

    message_label = ttk.Label(Message_Window, text=message, anchor='center')
    message_label.grid(sticky='we', pady=20)

    row = 1
    for button in buttons:
        button_text = button.get('text', 'OK')
        button_fg = button.get('fg', 'black')
        button_command = button.get('command', Message_Window.destroy)
        Button_Widget = ttk.Button(Message_Window, text=button_text, command=button_command)
        Button_Widget.grid(row=row, pady=5)
        row = row + 1

# Opens the file picker when an Odin archive button is clicked
def open_file(type):
    global initial_directory
    try:
        def change_theme():
            sv_ttk.set_theme('dark')
        if theme == 'dark':
            sv_ttk.set_theme('light')
            t = Timer(0, change_theme)
            t.start()
        initialdir = Default_Directory_Entry.get()
        if initialdir == '~' or os.path.isdir(initialdir) == True:
            initial_directory = initialdir
            if type == 'AP':
                file_path = filedialog.askopenfilename(title=f'Select an {type} file', initialdir=initialdir, filetypes=[(f'{type} file', '.tar .zip .md5')])
            else:
                file_path = filedialog.askopenfilename(title=f'Select a {type} file', initialdir=initialdir, filetypes=[(f'{type} file', '.tar .zip .md5')])
            if file_path:
                if type == 'BL':
                    BL_Entry.delete(0, 'end')
                    BL_Entry.insert(0, file_path)
                elif type == 'AP':
                    AP_Entry.delete(0, 'end')
                    AP_Entry.insert(0, file_path)
                elif type == 'CP':
                    CP_Entry.delete(0, 'end')
                    CP_Entry.insert(0, file_path)
                elif type == 'CSC':
                    CSC_Entry.delete(0, 'end')
                    CSC_Entry.insert(0, file_path)
                elif type == 'USERDATA':
                    USERDATA_Entry.delete(0, 'end')
                    USERDATA_Entry.insert(0, file_path)
                print(f"Selected {type}: '{file_path}' with file picker")
        else:
            print(f"Invalid directory - The directory: '{initialdir}' does not exist. You can change your initial file picker directory by going to: Settings - Flashing - Initial file picker directory")
# This needs to be worked on...
#
#            show_message('Invalid directory', f"The directory: '{initialdir}' does not exist\nYou can change your initial file picker directory by going to:\nSettings - Flashing - Initial file picker directory", window_size=(480, 140))
#    except ttk.TclError:
#        print('Thor GUI was closed with the file picker still open - Don't do that. :)')
    except pexpect.exceptions.TIMEOUT:
        print('A Timeout occurred in start_thor')
#    except Exception as e:
#        print(f'An exception occurred in open_file: {e}')

# Handles asking the user if they'd like to connect to a device
def select_device():
    global last_lines
    devices = []
    start_index = None
    try:
        for i in range(len(last_lines)-1, -1, -1):
            if last_lines[i][0].startswith('Choose a device to connect to:'):
                start_index = i
                break

        if start_index is not None:
            for i in range(start_index+1, len(last_lines)):
                line = last_lines[i][0]
                if line.startswith('Cancel operation'):
                    break
                if line.strip() != '':
                    devices.append(line.strip('> '))

        if devices:
            title = 'Connect device'
            message = 'Choose a device to connect to:'
            selected_device = tk.StringVar(value=None)

            Connect_Device_Window = tk.Toplevel(window)
            Connect_Device_Window.title(title)
            Connect_Device_Window.wm_transient(window)
            Connect_Device_Window.grab_set()
            Connect_Device_Window.update_idletasks()

            window_size = (550, 200)
            width, height = window_size
            x = window.winfo_rootx() + (window.winfo_width() - width) // 2
            y = window.winfo_rooty() + (window.winfo_height() - height) // 2
            Connect_Device_Window.geometry(f'{width}x{height}+{x}+{y}')
            Connect_Device_Window.grid_columnconfigure(0, weight=1)
            Connect_Device_Window.grid_columnconfigure(1, weight=1)

            message_label = ttk.Label(Connect_Device_Window, text=message, anchor='center')
            message_label.grid(columnspan=2, sticky='ew')

            radio_buttons = []
            even = False
            row = 1
            for device in devices:
                var = tk.StringVar(value=device)
                radio_button = ttk.Radiobutton(Connect_Device_Window, text=device, variable=selected_device, value=device)
                radio_buttons.append((radio_button, var))
                if even == False:
                    radio_button.grid(pady=5, padx=5, columnspan=2, row=row)
                    even = True
                else:
                    radio_button.grid(padx=5, columnspan=2, row=row)
                    even = False
                row = row + 1

                def handle_connect():
                    KEY_DOWN = '\x1b[B'
                    selected = selected_device.get()
                    if selected == '':
                        print('No device was selected')
                    else:
                        for radio_button, var in radio_buttons:
                            if var.get() == selected:
                                Thor.send('\n')
                                Connect_Device_Window.destroy()
                                return False
                            else:
                                Thor.send(KEY_DOWN)

                def cancel_connect():
                    KEY_DOWN = '\x1b[B'
                    for radio_button, var in radio_buttons:
                        Thor.send(KEY_DOWN)
                    Thor.send('\n')
                    Connect_Device_Window.destroy()

            # Create the Connect button
            Connect_Button_2 = ttk.Button(Connect_Device_Window, text='Connect', command=handle_connect)
            Connect_Button_2.grid(pady=5, padx=5, column=1, row=row, sticky='we')

            # Create the Cancel button
            Cancel_Button = ttk.Button(Connect_Device_Window, text='Cancel', command=cancel_connect)
            Cancel_Button.grid(pady=5, padx=5, column=0, row=row, sticky='we')

            Connect_Device_Window.mainloop()
        else:
            print('No devices available.')
    except Exception as e:
        print(f'An exception occurred in select_device: {e}')

# Handles asking the user what partitions they'd like to flash
def select_partitions(path, name):
    try:
        selected_files = []
        selected_files.clear()
        combined_file = os.path.join(path, name)
        def get_files_from_tar(path, name):
            file_names = []
            with tarfile.open(os.path.join(path, name), 'r') as tar:
                for member in tar.getmembers():
                    file_names.append(member.name)
            return file_names

        def get_files_from_zip(path, name):
            file_names = []
            with zipfile.ZipFile(os.path.join(path, name), 'r') as zip:
                for file_info in zip.infolist():
                    file_names.append(file_info.filename)
            return file_names

        def select_all(checkboxes, select_all_var):
            select_all_value = select_all_var.get()
            for checkbox, var in checkboxes:
                var.set(select_all_value)

        def flash_selected_files(checkboxes, Select_Partitions_Window):
            for checkbox, var in checkboxes:
                if var.get() == 1:
                    selected_files.append(checkbox.cget('text'))
            if not selected_files:
                print(f'You chose not to select any partitions from {name}')
                Thor.send('\n')
                Select_Partitions_Window.destroy()
                return False

            for file_name in file_names:
                sleep(0.05)
                if file_name in selected_files:
                    Thor.send('\x20')
                Thor.send('\x1b[B')
            Thor.send('\n')
            Select_Partitions_Window.destroy()
            return False

        if name.endswith('.tar') or name.endswith('.md5'):
            file_names = get_files_from_tar(path, name)
        elif name.endswith('.zip'):
            file_names = get_files_from_zip(path, name)
        else:
            print('Invalid file format. Please provide a .tar, .zip, or .md5 file.')
            return

        Select_Partitions_Window = tk.Toplevel(window)
        Select_Partitions_Window.title('Select partitions')
        Select_Partitions_Window.wm_transient(window)
        Select_Partitions_Window.grab_set()
        Select_Partitions_Window.update_idletasks()

        window_height = 30
        checkboxes = []
        shortened_file = name[:34]

        Label = ttk.Label(Select_Partitions_Window, text=f'Select what partitions to flash from\n{shortened_file}...', font=('Monospace', 10))
        Label.pack(pady=5)
        window_height = window_height + 50

        select_all_var = tk.IntVar()
        select_all_button = ttk.Checkbutton(Select_Partitions_Window, text='Select all', variable=select_all_var, command=lambda: select_all(checkboxes, select_all_var))
        select_all_button.pack(pady=5)

        for file_name in file_names:
            var = tk.IntVar()
            checkbox = ttk.Checkbutton(Select_Partitions_Window, text=file_name, variable=var)
            checkbox.pack(anchor='w', pady=(0,5), padx=5)
            checkboxes.append((checkbox, var))
            window_height = window_height + 33

        Select_Partitions_Button = ttk.Button(Select_Partitions_Window, text='Select', command=lambda: flash_selected_files(checkboxes, Select_Partitions_Window))
        window_height = window_height + 38
        Select_Partitions_Button.pack()

        window_size=(330, window_height)
        width, height = window_size
        x = window.winfo_rootx() + (window.winfo_width() - width) // 2
        y = window.winfo_rooty() + (window.winfo_height() - height) // 2
        Select_Partitions_Window.geometry(f'{width}x{height}+{x}+{y}')

        Select_Partitions_Window.mainloop()

    except Exception as e:
        print(f'An exception occurred in select_partitions: {e}')

# Asks the user if they'd like to flash the selected partitions
def verify_flash():
    global last_lines
    try:
        Verify_Flash_Window = tk.Toplevel(window)
        Verify_Flash_Window.title('Verify Flash')
        Verify_Flash_Window.wm_transient(window)
        Verify_Flash_Window.grab_set()
        Verify_Flash_Window.update_idletasks()
        Verify_Flash_Window.columnconfigure(0, weight=1)
        Verify_Flash_Window.columnconfigure(1, weight=1)

        Label = ttk.Label(Verify_Flash_Window, text='Are you absolutely sure you want to flash the partitions you selected?', font=('Monospace', 11), anchor='center')
        Label.grid(row=0, column=0, columnspan=2, pady=9)

        def send_no():
            print('Sent \'n\'')
            Thor.sendline('n')
            Verify_Flash_Window.destroy()

        def send_yes():
            Thor.sendline('y')
            print('Sent \'y\'')
            Verify_Flash_Window.destroy()

        No_Button = ttk.Button(Verify_Flash_Window, text='No', command=send_no)
        No_Button.grid(row=1, column=0, sticky='we', pady=5, padx=(5,2.5))

        Yes_Button = ttk.Button(Verify_Flash_Window, text='Yes', command=send_yes)
        Yes_Button.grid(row=1, column=1, sticky='we', pady=5, padx=(2.5,5))

        width = 640
        height = 77
        x = window.winfo_rootx() + (window.winfo_width() - width) // 2
        y = window.winfo_rooty() + (window.winfo_height() - height) // 2
        Verify_Flash_Window.geometry(f'{width}x{height}+{x}+{y}')

        Verify_Flash_Window.mainloop()
    except Exception as e:
        print(f'An exception occurred in verify_flash: {e}')

# Opens websites
def open_link(link):
    webbrowser.open(link)

# Deals with showing links - From https://github.com/GregDMeyer/PWman/blob/master/tkHyperlinkManager.py, which itself is from http://effbot.org/zone/tkinter-text-hyperlink.htm, but that site no longer exists
class HyperlinkManager:

    def __init__(self, text):
        self.text = text
        self.text.tag_config('hyper', foreground='blue')
        self.text.tag_bind('hyper', '<Enter>', self._enter)
        self.text.tag_bind('hyper', '<Leave>', self._leave)
        self.text.tag_bind('hyper', '<ButtonRelease-1>', self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = 'hyper-%d' % len(self.links)
        self.links[tag] = action
        return 'hyper', tag

    def _enter(self, event):
        self.text.config(cursor='hand2')

    def _leave(self, event):
        self.text.config(cursor='')

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == 'hyper-':
                self.links[tag]()
                return

def bind_file_drop(widget):
    widget.drop_target_register(DND_FILES)
    widget.dnd_bind('<<Drop>>', lambda e: [widget.delete(0, 'end'), widget.insert(tk.END, e.data)])

# Changes variables
def change_variable(variable):
    global theme, tooltips, sudo, thor
    if variable == 'theme':
        if sv_ttk.get_theme() == 'dark':
            theme = 'light'
        elif sv_ttk.get_theme() == 'light':
            theme = 'dark'
        sv_ttk.set_theme(theme)
        if keep_dark_term == True and theme == 'light':
            Output_Text.configure(bg='#1c1c1c')
    elif variable == 'tooltips':
        tooltips = not tooltips
        if tooltips == True:
            tooltip_manager.create_tooltips()
        elif tooltips == False:
            tooltip_manager.hide_tooltips()
    elif variable == 'sudo':
        sudo = not sudo
    elif variable == 'thor':
        if thor == 'internal':
            thor = 'external'
            Thor_Entry.configure(state='normal')
        elif thor == 'external':
            thor = 'internal'
            Thor_Entry.configure(state='disabled')

# Creates the start-up window
def create_startup_window():
    try:
        if operating_system == 'Linux':
            compatibility_message = "It looks like you're using Linux, so you're good to go!"
        elif operating_system == 'Windows':
            compatibility_message = "It looks like you're using Windows, so sadly Thor GUI won't work for you."
        elif operating_system == 'Darwin':
            compatibility_message = "It looks like you're using macOS, so sadly Thor GUI won't work for you."
        Startup_Window = tk.Toplevel(window)
        Startup_Window.title('Thor GUI - A GUI for the Thor Flash Utility')
        Startup_Window.wm_transient(window)
        Startup_Window.grab_set()
        Startup_Window.update_idletasks()
        Startup_Window.columnconfigure(0, weight=1)
        Startup_Window.columnconfigure(1, weight=1)

        Label = ttk.Label(Startup_Window, text='Welcome to Thor GUI!', font=('Monospace', 11), anchor='center')
        Label.grid(row=0, column=0, columnspan=2, pady=9)

        Label2 = ttk.Label(Startup_Window, text="If you're not sure how to use Thor GUI, click the 'Help' tab.", font=('Monospace', 11), anchor='center')
        Label2.grid(row=2, column=0, columnspan=2, pady=9)

        Label3 = ttk.Label(Startup_Window, text="For info about Thor GUI, click the 'About' tab.", font=('Monospace', 11), anchor='center')
        Label3.grid(row=1, column=0, columnspan=2, pady=9)

        Label4 = ttk.Label(Startup_Window, text='Thor GUI currently only supports Linux.', font=('Monospace', 11), anchor='center')
        Label4.grid(row=3, column=0, columnspan=2, pady=9)

        Label5 = ttk.Label(Startup_Window, text=compatibility_message, font=('Monospace', 11), anchor='center')
        Label5.grid(row=4, column=0, columnspan=2, pady=9)

        Label6 = ttk.Label(Startup_Window, text="Click 'Close' to close this window, or 'Cancel' to close Thor GUI.", font=('Monospace', 11), anchor='center')
        Label6.grid(row=6, column=0, columnspan=2, pady=9)

        def send_cancel():
            Startup_Window.destroy()
            on_window_close()

        def send_close():
            global first_run
            first_run = False
            Startup_Window.destroy()

        Cancel_Button = ttk.Button(Startup_Window, text='Cancel', command=send_cancel)
        Cancel_Button.grid(row=7, column=0, sticky='we', pady=5, padx=(5,2.5))

        Close_Button = ttk.Button(Startup_Window, text='Close', command=send_close)
        Close_Button.grid(row=7, column=1, sticky='we', pady=5, padx=(2.5,5))

        width = 640
        height = 257
        x = window.winfo_rootx() + (window.winfo_width() - width) // 2
        y = window.winfo_rooty() + (window.winfo_height() - height) // 2
        Startup_Window.geometry(f'{width}x{height}+{x}+{y}')

        Startup_Window.mainloop()
    except Exception as e:
        print(f'An exception occurred in create_startup_window: {e}')

# Handles stopping everything when the window is closed, or the 'Stop Thor' button is clicked
def on_window_close():
    global Thor, currently_running, output_thread, prompt_available, Message_Window
    try:
        def force_stop():
            global currently_running
            currently_running = False
            window.after_cancel(start_flash)
            Thor.sendline('exit')
            Thor.terminate()
            Thor.wait()
            print('Stopped Thor (possibly forcibly)')
            output_thread.join(timeout=0.5)  # Wait for the output thread to finish with a timeout
            Force_Close_Window.destroy()
            print('Stopping Thor GUI...')
            f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
            pickle.dump(filed_version, f1)
            pickle.dump(theme, f1)
            pickle.dump(tooltips, f1)
            pickle.dump(sudo, f1)
            pickle.dump(initial_directory, f1)
            pickle.dump(first_run, f1)
            pickle.dump(thor, f1)
            pickle.dump(thor_directory, f1)
            pickle.dump(keep_dark_term, f1)
            f1.close()
            window.destroy()
        if currently_running:
            if prompt_available == True:
                currently_running = False
                window.after_cancel(start_flash)
                Thor.sendline('exit')
                Thor.terminate()
                Thor.wait()
                print('Stopped Thor')
                output_thread.join(timeout=0.5)  # Wait for the output thread to finish with a timeout
                print('Stopping Thor GUI...')
                f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
                pickle.dump(filed_version, f1)
                pickle.dump(theme, f1)
                pickle.dump(tooltips, f1)
                pickle.dump(sudo, f1)
                pickle.dump(initial_directory, f1)
                pickle.dump(first_run, f1)
                pickle.dump(thor, f1)
                pickle.dump(thor_directory, f1)
                pickle.dump(keep_dark_term, f1)
                f1.close()
                window.destroy()
            elif prompt_available == False:
                Force_Close_Window = tk.Toplevel(window)
                Force_Close_Window.title('Force Stop Thor')
                Force_Close_Window.wm_transient(window)
                Force_Close_Window.grab_set()
                Force_Close_Window.update_idletasks()
                Force_Close_Window.columnconfigure(0, weight=1)
                Force_Close_Window.columnconfigure(1, weight=1)
                width = 786
                height = 132
                x = window.winfo_rootx() + (window.winfo_width() - width) // 2
                y = window.winfo_rooty() + (window.winfo_height() - height) // 2
                Force_Close_Window.geometry(f'{width}x{height}+{x}+{y}')
                Force_Close_Label = ttk.Label(Force_Close_Window, text='The \'shell>\' prompt isn\'t available, so the \'exit\' command can\'t be sent.', font=('Monospace', 11), anchor='center')
                Force_Close_Label.grid(columnspan=2, column=0, row=0, sticky='we', pady=(5,2))
                Force_Close_Label_2 = ttk.Label(Force_Close_Window, text='Thor may be busy, or locked up.', font=('Monospace', 11), anchor='center')
                Force_Close_Label_2.grid(columnspan=2, column=0, row=1, sticky='we', pady=2)
                Force_Close_Label_3 = ttk.Label(Force_Close_Window, text='You may force stop Thor by clicking the \'Force Stop\' button.', font=('Monospace', 11), anchor='center')
                Force_Close_Label_3.grid(columnspan=2, column=0, row=2, sticky='we', pady=2)
                Force_Close_Label_4 = ttk.Label(Force_Close_Window, text='However, if Thor is in the middle of a flash or something, there will be consequences.', font=('Monospace', 11), anchor='center')
                Force_Close_Label_4.grid(columnspan=2, column=0, row=3, sticky='we', padx=5, pady=(0,5))
                Cancel_Force_Stop_Button = ttk.Button(Force_Close_Window, text='Cancel', command=Force_Close_Window.destroy)
                Cancel_Force_Stop_Button.grid(column=0, row=4, sticky='we', pady=5, padx=(5,2.5))
                Force_Stop_Button = ttk.Button(Force_Close_Window, text='Force Stop', command=force_stop)
                Force_Stop_Button.grid(column=1, row=4, sticky='we', pady=5, padx=(2.5,5))
                Force_Close_Window.mainloop()
        else:
            window.after_cancel(start_flash)
            print('Stopping Thor GUI...')
            f1 = open(f'{path_to_thor_gui}/thor-gui-settings.pkl', 'wb')
            pickle.dump(filed_version, f1)
            pickle.dump(theme, f1)
            pickle.dump(tooltips, f1)
            pickle.dump(sudo, f1)
            pickle.dump(initial_directory, f1)
            pickle.dump(first_run, f1)
            pickle.dump(thor, f1)
            pickle.dump(thor_directory, f1)
            pickle.dump(keep_dark_term, f1)
            f1.close()
            window.destroy()
    except Exception as e:
        print(f'An exception occurred in on_window_close: {e}')

# Creates and hides tooltips
class ToolTipManager:
    
    def __init__(self, tooltip_dict):
        self.tooltip_dict = tooltip_dict
        self.needed_tooltips = []
        self.tooltip_delay = 0.25

    def add_needed_tooltip(self, widget):
        widget_name = widget.name
        msg = self.tooltip_dict.get(widget_name)
        if msg:
            self.needed_tooltips.append(widget)

    def create_tooltips(self):
        for widget in self.needed_tooltips:
            msg = self.tooltip_dict.get(widget.name)
            ToolTip(widget, msg=msg, delay=self.tooltip_delay, width=len(msg) * 10)

    def hide_tooltips(self):
        for widget in self.needed_tooltips:
            msg='Tooltips will be disabled after a restart'
            if msg:
                ToolTip(widget, msg=msg, delay=self.tooltip_delay, width=len(msg) * 10)

    def change_tooltip(self, widget, msg):
        ToolTip(widget, msg=msg, delay=self.tooltip_delay, width=len(msg) * 10)    

# Creates buttons - My first-ever class :)
class Button():
    def __init__(self, name: str, master: ttk.Frame, text: str, command: typ.Callable,
        state: str = 'normal', 
        column: int = 0,
        row: int = 0,
        sticky: str = 'we',
        padx: int = 5,
        pady: int = 5, 
        columnspan: int = 1):
            
        self.name = name + '_Button'
        self.master = master
        self.text = text
        self.command = command
        self.state = state
        self.column = column
        self.row = row
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
        self.columnspan = columnspan
        self.tooltip_delay = 0.25
        self.tooltip_manager = tooltip_manager
        self.button = ttk.Button(self.master, text=self.text, command=self.command, state=self.state)
        self.button.grid(column=self.column, row=self.row, columnspan=self.columnspan, sticky=self.sticky, padx=self.padx, pady=self.pady)
        self.tooltip_manager.add_needed_tooltip(self)

    def __getattr__(self, attr):
        return getattr(self.button, attr)

# Creates entries
class Entry():
    def __init__(self, name: str, master: ttk.Frame,
        state: str = 'normal', 
        column: int = 0,
        row: int = 0,
        sticky: str = 'we',
        padx: int = 5,
        pady: int = 5, 
        columnspan: int = 1):
            
        self.name = name + '_Entry'
        self.master = master
        self.state = state
        self.column = column
        self.row = row
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
        self.columnspan = columnspan
        self.tooltip_delay = 0.25
        self.tooltip_manager = tooltip_manager
        self.entry = ttk.Entry(self.master, state=self.state)
        self.entry.grid(column=self.column, row=self.row, columnspan=self.columnspan, sticky=self.sticky, padx=self.padx, pady=self.pady)
        self.tooltip_manager.add_needed_tooltip(self)

    def __getattr__(self, attr):
        return getattr(self.entry, attr)

# Creates checkbuttons
class Checkbutton():
    def __init__(self, name: str, master: ttk.Frame, command, variable,
        text: str = None,
        style: str = None,
        state: str = 'normal', 
        column: int = 0,
        row: int = 0,
        sticky: str = 'we',
        padx: int = 5,
        pady: int = 5, 
        columnspan: int = 1):

        self.name = name + '_Checkbutton'
        self.master = master
        self.command = command
        self.variable = variable
        self.text = text
        self.style = style
        self.state = state
        self.column = column
        self.row = row
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
        self.columnspan = columnspan
        self.tooltip_delay = 0.25
        self.tooltip_manager = tooltip_manager
        self.checkbutton = ttk.Checkbutton(self.master, command=self.command, variable=self.variable, state=self.state)
        if self.text is not None and self.text[0] is not None:
            self.checkbutton.config(text=self.text)
        if self.style is not None and self.style[0] is not None:
            self.checkbutton.config(style=self.style)
        self.checkbutton.grid(column=self.column, row=self.row, columnspan=self.columnspan, sticky=self.sticky, padx=self.padx, pady=self.pady)
        self.tooltip_manager.add_needed_tooltip(self)

    def __getattr__(self, attr):
        return getattr(self.checkbutton, attr)

# Creates labels


# Creates labels, will be replaced with a class
def create_label(name, master, text, font=('Monospace', 11), sticky='we', padx=0, pady=0, anchor='center'):
    label = name + '_Label'
    label = ttk.Label(master, text=text, font=font, anchor=anchor)
    label.grid(sticky=sticky, padx=padx, pady=pady)

# Creates text, will be replaced with a class
def create_text(name, master, lines, font=('Monospace', 11)):
    text = name + '_Text'
    text = tk.Text(master, font=font, height=1, bd=0, highlightthickness=0, wrap='word')
    text.grid(sticky='ew')
    hyperlink = HyperlinkManager(text)
    text.tag_configure('center', justify='center')
    for line, link in lines:
        if link != None:
            text.insert(tk.END, line, hyperlink.add(partial(open_link, link)))
        else:
            text.insert(tk.END, line)
    text.tag_add('center', '1.0', 'end')
    text.config(state=tk.DISABLED)

# Creates the main window
window = TkinterDnD.Tk(className='Thor GUI')
window.title(f'Thor GUI - {version}')
window.geometry('985x600')

# Hide the window, and then show it as soon as possible - Without this, the window is grey while being initialised, something caused by tkinterdnd2
window.withdraw()
window.after(0,window.deiconify)

# Create a ToolTipManager instance
tooltip_manager = ToolTipManager(tooltip_dict)

# Sets the row and column widths
window.grid_rowconfigure(3, weight=1)
window.grid_rowconfigure(4, weight=1)
window.grid_rowconfigure(5, weight=1)
window.grid_rowconfigure(6, weight=1)
window.grid_rowconfigure(7, weight=1)
window.grid_columnconfigure(6, weight=1)

# Creates the main window widgets
Title_Label = ttk.Label(window, text='Thor Flash Utility v1.0.4', font=('Monospace', 20), anchor='center')
Title_Label.grid(row=0, column=0, columnspan=7, rowspan=2, sticky='nesw')

Start_Button = Button('Start', window, 'Start Thor', start_thor, 'normal', 8, 0, 'we', 5)
Begin_Button = Button('Begin', window, 'Start Odin Protocol', toggle_odin, 'disabled', 10, 0, 'we', 5, 5, 2)
Connect_Button = Button('Connect', window, 'Connect', toggle_connection, 'disabled', 9, 0, 'we', 0, 5)
Command_Entry = Entry('Command', window, 'disabled', 8, 1, 'nesw', 5, 0, 4)
Command_Entry.bind('<Return>', lambda event: send_command(Command_Entry.get(), 'entry'))
Enter_Button = Button('Enter', window, 'Enter', lambda: Thor.send('\n'), 'disabled', 8, 2, 'ew', 5)
Space_Button = Button('Space', window, 'Space', lambda: Thor.send('\x20'), 'disabled', 9, 2, 'ew', (0, 5))
Page_Up_Button = Button('Page_Up', window, 'PgUp', lambda: Thor.send('\x1b[A'), 'disabled', 10, 2, 'ew', 0)
Page_Down_Button = Button('Page_Down', window, 'PgDn', lambda: Thor.send('\x1b[B'), 'disabled', 11, 2, 'ew', 5)

Start_Flash_Button = Button('Start_Flash', window, 'Start', start_flash, 'disabled', 8, 8, 'ew', 0, 5, 2)
Reset_Button =Button('Reset', window, 'Reset', reset, 'normal', 10, 8, 'we', 5, 5, 2)

# Creates the Odin Archive Check-boxes
BL_Checkbutton_var = tk.IntVar()
AP_Checkbutton_var = tk.IntVar()
CP_Checkbutton_var = tk.IntVar()
CSC_Checkbutton_var = tk.IntVar()
USERDATA_Checkbutton_var = tk.IntVar()

BL_Checkbutton = Checkbutton('BL', window, None, BL_Checkbutton_var, state='normal', column=7, row=3)
AP_Checkbutton = Checkbutton('AP', window, None, AP_Checkbutton_var, state='normal', column=7, row=4)
CP_Checkbutton = Checkbutton('CP', window, None, CP_Checkbutton_var, state='normal', column=7, row=5)
CSC_Checkbutton = Checkbutton('CSC', window, None, CSC_Checkbutton_var, state='normal', column=7, row=6)
USERDATA_Checkbutton = Checkbutton('USERDATA', window, None, USERDATA_Checkbutton_var, state='normal', column=7, row=7)

# Creates the Odin archive Buttons
BL_Button = Button('BL', window, 'BL', lambda: open_file('BL'), 'normal', 8 , 3, 'we', 4)
AP_Button = Button('AP', window, 'AP', lambda: open_file('AP'), 'normal', 8, 4, 'we', 4)
CP_Button = Button('CP', window, 'CP', lambda: open_file('CP'), 'normal', 8, 5, 'we', 4)
CSC_Button = Button('CSC', window, 'CSC', lambda: open_file('CSC'), 'normal', 8 , 6, 'we', 4)
USERDATA_Button = Button('USERDATA', window, 'USERDATA', lambda: open_file('USERDATA'), 'normal', 8 , 7, 'we', 4)

# Creates the Odin archive Entries
BL_Entry = Entry('BL', window, 'normal', 9, 3, 'we', 5, 0, 3)
AP_Entry = Entry('AP', window, 'normal', 9, 4, 'we', 5, 0, 3)
CP_Entry = Entry('CP', window, 'normal', 9, 5, 'we', 5, 0, 3)
CSC_Entry = Entry('CSC', window, 'normal', 9, 6, 'we', 5, 0, 3)
USERDATA_Entry = Entry('USERDATA', window, 'normal', 9, 7, 'we', 5, 0, 3)

bind_file_drop(BL_Entry)
bind_file_drop(AP_Entry)
bind_file_drop(CP_Entry)
bind_file_drop(CSC_Entry)
bind_file_drop(USERDATA_Entry)

# Creates the five frame buttons
Log_Button = Button('Log', window, 'Log', lambda:toggle_frame('Log'), 'normal', 0, 2, 'wes', (5, 0), 0)
Options_Button = Button('Options', window, 'Options', lambda:toggle_frame('Options'), 'normal', 1, 2, 'wes', 0, (0, 5))
Pit_Button = Button('Pit', window, 'Pit', lambda:toggle_frame('Pit'), 'normal', 2, 2, 'wes', 0, 5)
Help_Button = Button('Help', window, 'Help', lambda:toggle_frame('Help'), 'normal', 4, 2, 'wes', 0, 5)
About_Button = Button('About', window, 'About', lambda:toggle_frame('About'), 'normal', 5, 2, 'wes', 0, 5)
Settings_Button = Button('Settings', window, 'Settings', lambda:toggle_frame('Settings'), 'normal', 3, 2, 'wes', 0, 5)

# Creates the Log Frame
Log_Frame = ttk.Frame(window)
Log_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
Log_Frame.grid_columnconfigure(0, weight=1)
Log_Frame.grid_rowconfigure(0, weight=1)

Output_Text = scrolledtext.ScrolledText(Log_Frame, state='disabled', highlightthickness=0, font=('Monospace', 9), borderwidth=0)
Output_Text.grid(row=0, column=0, rowspan=6, sticky='nesw')

# Creates the 'Options' frame and check-boxes
Options_Frame = ttk.Frame(window)
Options_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)

# Set the tooltip_manager for the Options frame
Options_Frame.tooltip_manager = tooltip_manager

NOTE_Label = ttk.Label(Options_Frame, text="NOTE: The 'T Flash' option is temporarily not supported by Thor GUI.")
NOTE_Label.grid(row=0, column=0, pady=10, padx=10, sticky='w')

TFlash_Option_var = tk.IntVar()
TFlash_Option = ttk.Checkbutton(Options_Frame, variable=TFlash_Option_var, text='T Flash', state='disabled')
TFlash_Option.grid(row=1, column=0, pady=10, padx=10, sticky='w')

TFlash_Label = ttk.Label(Options_Frame, text='Writes the bootloader of a working device onto the SD card', cursor='hand2')
TFlash_Label.grid(row=2, column=0, pady=10, padx=10, sticky='w')

TFlash_Label.bind('<ButtonRelease-1>', lambda e: open_link('https://android.stackexchange.com/questions/196304/what-does-odins-t-flash-option-do'))

EFSClear_Option_var = tk.IntVar()
EFSClear_Option = ttk.Checkbutton(Options_Frame, variable=EFSClear_Option_var, text='EFS Clear')
EFSClear_Option.grid(row=3, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label = ttk.Label(Options_Frame, text="Wipes the EFS partition (WARNING: You better know what you're doing!)", cursor='hand2')
EFSClear_Label.grid(row=4, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label.bind('<ButtonRelease-1>', lambda e: open_link('https://android.stackexchange.com/questions/185679/what-is-efs-and-msl-in-android'))

BootloaderUpdate_Option_var = tk.IntVar()
BootloaderUpdate_Option = ttk.Checkbutton(Options_Frame, variable=BootloaderUpdate_Option_var, text='Bootloader Update')
BootloaderUpdate_Option.grid(row=5, column=0, pady=10, padx=10, sticky='w')

BootloaderUpdate_Label = ttk.Label(Options_Frame, text='')
BootloaderUpdate_Label.grid(row=6, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Option_var = tk.IntVar(value=True)
ResetFlashCount_Option = ttk.Checkbutton(Options_Frame, variable=ResetFlashCount_Option_var, text='Reset Flash Count')
ResetFlashCount_Option.grid(row=7, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Label = ttk.Label(Options_Frame, text='')
ResetFlashCount_Label.grid(row=8, column=0, pady=10, padx=10, sticky='w')

Apply_Options_Button = Button('Apply_Options', Options_Frame, 'Apply', apply_options, 'disabled', 0, 9, 'w', 10, 10)

# Creates the 'Pit' frame
Pit_Frame = ttk.Frame(window)
Pit_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)

# Set the tooltip_manager for the Pit frame
Pit_Frame.tooltip_manager = tooltip_manager

Test_Label = ttk.Label(Pit_Frame, text='Just a test :)')
Test_Label.grid(row=0, column=0, pady=10, padx=10, sticky='w')
create_label('Test', Pit_Frame, 'Just a test :)', sticky='w', padx=10, pady=10)

Although_Label = ttk.Label(Pit_Frame, text='Pull requests are always welcome though!')
Although_Label.grid(row=1, column=0, pady=10, padx=10, sticky='w')

# Creates the 'Settings' frame
Settings_Frame = ttk.Frame(window)
Settings_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
Settings_Frame.grid_columnconfigure(0, weight=1)

create_label('Theme', Settings_Frame, 'Appearance', ('Monospace', 12), 'w')

if theme == 'light':
    other_theme = 'Dark'
elif theme == 'dark':
    other_theme = 'Light'

if tooltips == True:
    other_tooltip = 'off'
elif tooltips == False:
    other_tooltip = 'on'

if sudo == True:
    other_sudo = 'without'
elif sudo == False:
    other_sudo = 'with'
    
if thor == "internal":
    other_thor = "an external"
elif thor == "external":
    other_thor = "the internal"

Theme_Checkbutton = Checkbutton('Theme', Settings_Frame, lambda: change_variable('theme'), None, other_theme + ' theme', 'Switch.TCheckbutton', 'normal', 0, 1, 'w', 10)

Tooltip_Checkbutton = Checkbutton('Tooltip', Settings_Frame, lambda: change_variable('tooltips'), None, 'Tooltips ' + other_tooltip, 'Switch.TCheckbutton', 'normal', 0, 2, 'w', 10)

create_label('Tooltip', Settings_Frame, 'A restart is required to turn off tooltips\n', ('Monospace', 8), 'w', 15)

create_label('Thor', Settings_Frame, 'Thor', ('Monospace', 12), 'w')

Thor_Checkbutton = Checkbutton('Thor', Settings_Frame, lambda: change_variable('thor'), None, 'Use ' + other_thor + ' Thor build', 'Switch.TCheckbutton', 'normal', 0, 5, 'w', 10)

create_label('Thor_Directory', Settings_Frame, 'Path to external Thor build:', ('Monospace', 9), 'w', 15, 5)

Thor_Entry = Entry('Thor', Settings_Frame, 'normal', 0, 7, 'we', (15, 120))
Thor_Entry.insert(tk.END, thor_directory)
if thor == "internal":
    Thor_Entry.configure(state="disabled")

Sudo_Checkbutton = Checkbutton('Sudo', Settings_Frame, lambda: change_variable('sudo'), None, 'Run Thor ' + other_sudo + ' sudo', 'Switch.TCheckbutton', 'normal', 0, 8, 'w', 10)

create_label('Sudo', Settings_Frame, 'A restart is required if Thor is already running\n', ('Monospace', 8), 'w', 15)

create_label('Flashing', Settings_Frame, 'Flashing', ('Monospace', 12), 'w')

create_label('Default_Directory', Settings_Frame, 'Initial file picker directory:', ('Monospace', 9), 'w', 15, 5)

Default_Directory_Entry = Entry('Default_Directory', Settings_Frame, 'normal', 0, 12, 'we', (15, 120))
Default_Directory_Entry.insert(tk.END, initial_directory)

# Creates the 'Help' frame
Help_Frame = ttk.Frame(window)
Help_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
Help_Frame.grid_columnconfigure(0, weight=1)

create_label('Help', Help_Frame, '\nNot sure how to use Thor GUI?', ('Monospace', 13))

create_text('Usage_Help_Text', Help_Frame, [
    ('Check out ', None),
    ('the Usage Guide', 'https://github.com/ethical-haquer/Thor_GUI#usage'),
    ('.', None)
])

create_label('Help_2', Help_Frame, '\nNeed help?', ('Monospace', 13))

create_text('Get_Help', Help_Frame, [
    ('Let me know on ', None),
    ('XDA', 'https://xdaforums.com/t/thor-gui-a-gui-for-the-thor-flash-utility-samsung-flash-tool.4636402/'),
    (', or open an issue on ', None),
    ('GitHub', 'https://github.com/ethical-haquer/Thor_GUI'),
    ('.', None)
])

create_label('Help_3', Help_Frame, '\nFound an issue?', ('Monospace', 13))

create_text('Report', Help_Frame, [
    ("If it isn't listed ", None),
    ('here', 'https://github.com/ethical-haquer/Thor_GUI#known-bugs'),
    (', you can ', None),
    ('report it', 'https://github.com/ethical-haquer/Thor_GUI/issues/new/choose'),
    ('.', None)
])

# Creates the 'About' frame
About_Frame = ttk.Frame(window)
About_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
About_Frame.grid_columnconfigure(0, weight=1)

create_label('Thor_GUI', About_Frame, 'Thor GUI', ('Monospace', 13))

create_label('Thor_GUI_Version', About_Frame, f'{version}')

create_label('Thor_GUI_Description', About_Frame, "A GUI for the Thor Flash Utility")

create_text('Thor_GUI_Websites', About_Frame, [
    ('GitHub', 'https://github.com/ethical-haquer/Thor_GUI'),
    (', ', None),
    ('XDA', 'https://xdaforums.com/t/thor-gui-a-gui-for-the-thor-flash-utility-samsung-flash-tool.4636402/')
])

create_label('Built_Around', About_Frame, 'Built around the:')

create_label('Thor', About_Frame, '\nThor Flash Utility', ('Monospace', 13))

create_label('Thor_Version', About_Frame, 'v1.0.4')

create_label('Thor_Description', About_Frame, 'An alternative to Heimdall')

create_text('Thor_Websites', About_Frame, [
    ('GitHub', 'https://github.com/Samsung-Loki/Thor'),
    (', ', None),
    ('XDA', 'https://forum.xda-developers.com/t/dev-thor-flash-utility-the-new-samsung-flash-tool.4597355/')
])

create_label('Credits', About_Frame, '\nCredits:', ('Monospace', 13))

create_text('TheAirBlow', About_Frame, [
    ('TheAirBlow', 'https://github.com/TheAirBlow'),
    (' for the ', None),
    ('Thor Flash Utility', None)
])

create_text('rdbende', About_Frame, [
    ('rdbende', 'https://github.com/rdbende'),
    (' for the ', None),
    ('Sun Valley tkk theme', 'https://github.com/rdbende/Sun-Valley-ttk-theme')
])

create_text('ethical_haquer', About_Frame, [
    ('Myself, ', None),
    ('ethical_haquer', 'https://github.com/ethical-haquer'),
    (', for Thor GUI', None)
])

create_label('Disclaimer', About_Frame, '\nThor GUI comes with absolutely no warranty.', ('Monospace', 9))

create_label('Disclaimer_2', About_Frame, 'See the GNU General Public License, version 3 or later for details.', ('Monospace', 9))

create_label('Disclaimer_3', About_Frame, '\nThor Flash Utility comes with absolutely no warranty.', ('Monospace', 9))

create_label('Disclaimer_4', About_Frame, 'See the Mozilla Public License, version 2 or later for details.', ('Monospace', 9))

# Configures the tags for coloring the output text
Output_Text.tag_configure('green', foreground='#26A269')
Output_Text.tag_configure('yellow', foreground='#E9AD0C')
Output_Text.tag_configure('red', foreground='#F66151')
Output_Text.tag_configure('blue', foreground='#33C7DE')
Output_Text.tag_configure('green_italic', foreground='#26A269', font=('Monospace', 9, 'italic'))
Output_Text.tag_configure('orange', foreground='#E9AD0C')
Output_Text.tag_configure('dark_blue', foreground='#2A7BDE')

# Raises the 'Log' frame to top on start-up
toggle_frame('Log')

# Binds the on_window_close function to the window's close event
window.protocol('WM_DELETE_WINDOW', on_window_close)

# Sets what theme to use
sv_ttk.set_theme(theme)

# Creates tooltips for buttons and things
if tooltips == True:
    tooltip_manager.create_tooltips()

# Shows the setup window if first_run == True
if first_run == True:
    window.after(0,create_startup_window)

# Runs the Tkinter event loop
window.mainloop()
