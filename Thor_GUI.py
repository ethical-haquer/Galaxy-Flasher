"""
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
"""

# Name: Thor GUI
# Version: Alpha v0.2.0
# By: ethical_haquer
# Released: N/A
# Known issues: Numerous :) - See https://github.com/ethical-haquer/Thor_GUI#known-bugs for more info

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import pexpect
from threading import Thread
import re
import webbrowser
from time import sleep
import tarfile
import os
from functools import partial
import time
import traceback

path_to_thor = '/PATH/TO/TheAirBlow.Thor.Shell.dll'

version = 'Alpha v0.2.0'

currently_running = False
odin_running = False
Thor = None
connection = False
first_find = True
first_flash = True
tag = 'green'
graphical_flash = False
prompt_available = False

successful_commands = []

file_paths = []

print(f'Running Thor GUI - {version}...')

# This starts and stops Thor
def start_thor():
    global Thor, output_thread, currently_running, prompt_available
    try:
        if currently_running:
            on_window_close()
        elif not currently_running:
            Thor = pexpect.spawn(f'dotnet {path_to_thor}', timeout=None, encoding='utf-8')
            output_thread = Thread(target=update_output)
            output_thread.daemon = True
            output_thread.start()
            currently_running = True
            Start_Button.configure(text='Stop Thor', fg='#F66151', padx=10)
            print('Started Thor')
    except pexpect.exceptions.TIMEOUT:
            print('A Timeout Occurred in start_thor')
    except Exception as e:
        print(f"An exception occurred in start_thor: {e}")
    
# What most commands go through
def send_command(command):
    global Thor, successful_commands, prompt_available
    if currently_running:
        try:
            if 'exit' in command or 'quit' in command:
                print('Sadly, stopping Thor independently is currently not supported by Thor GUI. To stop Thor, either click the: \'Stop Thor\' button (which will close the window), or close the window.')
            else:   
                if prompt_available == True:
                    Thor.sendline(command)
                    Output_Text.see(tk.END)
                    successful_commands.append(command)
                    print(f'Sent command: \'{command}\'')
                else:  
                    print(f'Couldn\'t send the command: \'{command}\', as the \'shell>\' prompt wasn\'t available')
        except Exception as e:
            print(f"An exception occurred in send_command: {e}")

# Perhaps the most important part of the program, along with scan_output - Handles displaying the output from Thor, while scan_output calls other functions when it detects certain lines in the output
def update_output():
    global last_lines
    global tag
    global connection
    global clean_line
    
    last_lines = [''] * 100
    output_buffer = ''
    
    while True:
        try:
            chunk = Thor.read_nonblocking(4096, timeout=0)
            if chunk:
                chunk = output_buffer + chunk
                output_lines = chunk.splitlines()
                
                for line in output_lines:
                    mostly_clean_line = re.sub(r'\x1b\[[?0-9;]*[A-Za-z]', '', line).strip()
                    clean_line = re.sub('\x1b=', '', mostly_clean_line).strip()
                    
                    if clean_line.startswith(("AP", "BL", "CP", "CSC", "HOME_CSC", "USERDATA")):
                        if clean_line.endswith(":"):
                            determine_tag(clean_line)
                            Output_Text.configure(state='normal')
                            Output_Text.insert(tk.END, clean_line + '\n', tag)
                            Output_Text.configure(state='disabled')
                            Output_Text.see(tk.END)
                            scan_output()
                            last_lines.pop(0)
                            last_lines.append(clean_line)
                        else:
                            output_buffer = clean_line
                    else:
                        if output_buffer.startswith("AP"):
                            clean_line = output_buffer + " " + clean_line
                            output_buffer = ''
                        
                        determine_tag(clean_line)
                        Output_Text.configure(state='normal')
                        Output_Text.insert(tk.END, clean_line + '\n', tag)
                        Output_Text.configure(state='disabled')
                        Output_Text.see(tk.END)
                        scan_output()
                        last_lines.pop(0)
                        last_lines.append(clean_line)
        except pexpect.exceptions.TIMEOUT:
            pass
        except pexpect.exceptions.EOF:
            break        
        except Exception as e:
            print(f"An exception occurred in update_output: '{e}'")
        
        # Delay between each update
        sleep(0.2)

def scan_output():
    global graphical_flash, last_lines, clean_line, archive_name, file_paths, prompt_available
    try:
        prompt_available = False
        if 'shell>' in clean_line:
            set_thor('on')
            prompt_available = True
        elif 'Successfully began an Odin session!' in clean_line:
            set_odin('on')
        elif 'Successfully disconnected the device!' in clean_line:
            set_connect('off')
        elif 'Successfully connected to the device!' in clean_line:
            set_connect('on')
        elif 'Cancel operation' in clean_line and "> " in last_lines[-1]:
            print('check 1')
            connect_index = None
            for i in range(len(last_lines)):
                print('check 2')
                if last_lines[i] == "connect":
                    print('check 3')
                    connect_index = i
                    break
            
            if connect_index is not None:
                print('check 4')
                cancel_operation_count = 0
                if clean_line == "Cancel operation":
                    cancel_operation_count += 1
                for line in last_lines[connect_index:]:
                    print('check 5')
                    if line == "Cancel operation":
                        print('check 6')
                        cancel_operation_count += 1
                        if cancel_operation_count == 2:
                            select_device()
                            break
                    elif line == "shell>":
                        break
        elif 'Successfully ended an Odin session!' in clean_line:
            set_odin('off')
        elif 'Choose what partitions to flash from' in clean_line and last_lines[-1] == "(Press <space> to select, <enter> to accept)":
            print('test 1')
            found_index = None
            print('test 2')
            for i in range(len(last_lines) - 1, -1, -1):
                print('test 3')
                if last_lines[i].startswith('Choose what partitions to flash from'):
                    print('test 4')
                    found_index = i
                    print('test 5')
                    break

            if found_index is not None:
                print('test 6')
                archive_name_pre = last_lines[found_index + 1].rstrip(':')
                print('test 7')
                last_flash_command = get_last_flash_tar_command()
                print('test 8')
                archive_path = last_flash_command.split(' ')[1]
                print('test 9')
                archive_name = os.path.basename(archive_name_pre.strip())
                print(f'Archive name is: {archive_name}')
                print(f'Archive path is: {archive_path}')

                # Check for "X"s in the archive list
                has_x = False
                for line in last_lines[found_index + 2:]:
                    if '[X]' in line:
                        has_x = True
                        break

                if not has_x:
                    if graphical_flash == False:
                        print('test 10')
                        select_partitions(archive_path, archive_name)
                        print('test 11')
                    else:
                        print('test 12')
                        combined_file = os.path.join(archive_path, archive_name)
                        print('test 13')
                        print(f'The combined file is: \'{combined_file}\'')
                        print(file_paths)
                        if combined_file in file_paths:
                            print('test 14')
                            select_partitions(archive_path, archive_name)
                        else:
                            Thor.send('\n')

        elif 'You chose to flash' and 'partitions in total:' in clean_line and last_lines[-1] == "(Are you absolutely sure you want to flash those? [y/n] (n):)":
            verify_flash()
            graphical_flash = False

        elif '" is set to "' in clean_line:
            if 'Option "T-Flash" is set to "False"' in clean_line:
                TFlash_Option_var = tk.IntVar(value=False)
            if 'Option "T-Flash" is set to "True"' in clean_line:
                TFlash_Option_var = tk.IntVar(value=True)
            if 'Option "EFS Clear" is set to "False"' in clean_line:
                EFSClear_Option_var = tk.IntVar(value=False)
            if 'Option "EFS Clear" is set to "True"' in clean_line:
                EFSClear_Option_var = tk.IntVar(value=True)
            if 'Option "Bootloader Update" is set to "False"' in clean_line:
                BootloaderUpdate_Option_var = tk.IntVar(value=False)
            if 'Option "Bootloader Update" is set to "True"' in clean_line:
                BootloaderUpdate_Option_var = tk.IntVar(value=True)
            if 'Option "Reset Flash Count" is set to "False"' in clean_line:
                ResetFlashCount_Option_var = tk.IntVar(value=False)
            if 'Option "Reset Flash Count" is set to "True"' in clean_line:
                ResetFlashCount_Option_var = tk.IntVar(value=True)  
    except Exception as e:
        print(f"An exception occurred in scan_output: '{e}'")

# Handles coloring the output, as the original ANSI escape sequences are stripped out
def determine_tag(line):
    global tag
    if line.startswith('Welcome to Thor Shell v1.0.4!'):
        tag = 'green'
    elif line.startswith('~~~~~~~~ Platform specific notes ~~~~~~~~'):
        tag = 'yellow'
    elif line.startswith('shell>'):
        tag = 'default_tag'
    elif line.startswith('~~~~~~~^'):
        tag = 'red'
    elif line.startswith('Note: beginning a protocol session unlocks new commands for you to use'):
        tag = 'green_italic'
    elif line.startswith('[required] {optional} - option list'):
        tag = 'yellow'
    elif line.startswith('Total commands: 11'):
        tag = 'green'
    elif line.startswith('exit - Closes the shell, quit also works'):
        tag = 'blue'
    elif line.startswith('Cancel operation'):
        tag = 'orange'
    elif line.startswith('Choose a device to connect to:'):
        tag = 'green'
    elif line.startswith('Successfully connected to the device!'):
        tag = 'green'
    elif line.startswith('Successfully disconnected the device!'):
        tag = 'green'
    elif 'Phone [' in line:
        tag = 'dark_blue'
    elif line.startswith('Successfully began an Odin session!'):
        tag = 'green'
    elif line.startswith('Successfully ended an Odin session!'):
        tag = 'green'
    elif line.startswith('Option "'):
        tag = 'green'
    elif line.startswith('Total protocol commands: 11'):
        tag = 'green'
    elif line.startswith('Successfully set "'):
        tag = 'green'
    elif line.startswith('Choose what partitions to flash from'):
        tag = 'green'
    elif line.startswith('You chose to flash '):
        tag = 'green'
    elif line.startswith('Are you absolutely sure you want to flash those? [y/n] (n):'):
        tag = 'yellow'

# Figures out what the last "flashTar" command run was
def get_last_flash_tar_command():
    global successful_commands
    for command in reversed(successful_commands):
        if command.startswith("flashTar"):
            return command
    return None

# Asks the user if they'd like to flash the selected partitions
def verify_flash():
    global last_lines
    start_index = -1
    num_partitions = -1
    
    for i, clean_line in enumerate(last_lines):
        if clean_line.startswith("You chose to flash"):
            start_index = i
            num_partitions = int(clean_line.split()[4])
    
    if start_index == -1:
        return
    
    chosen_partitions = last_lines[start_index+1:]
    end_index = -1
    
    for i, command in enumerate(chosen_partitions):
        if command.startswith("Are you absolutely sure you want to flash those?"):
            end_index = i
            break
    
    if end_index == -1:
        return
    
    message = "You chose to flash {} partitions in total:\n".format(num_partitions)
    message += "\n".join(chosen_partitions[:end_index]) + "\n"
    message += "\nAre you absolutely sure you want to flash those?"
    
    root = tk.Tk()
    root.title("Verify Flash")
    
    label = tk.Label(root, text=message)
    label.pack()
    
    def send_no():
        Thor.sendline('n')
        root.destroy()
    
    def send_yes():
        Thor.sendline('y')
        root.destroy()
    
    no_button = tk.Button(root, text="No", command=send_no)
    no_button.pack(side='left')
    
    yes_button = tk.Button(root, text="Yes", command=send_yes)
    yes_button.pack(side='right')

# Deals with enabling/disabling buttons - Mainly used by set_thor(), set_connect(), and set_odin()
def set_widget_state(*args, state="normal", text=None, color=None):
    for widget in args:
        widget.configure(state=state, text=text)
        if color is not None:
            widget.configure(fg=color)
        if text is not None:
            widget.configure(text=text)

# Tells the program whether Thor is running or not
def set_thor(value):
    global first_find
    if value == 'on':
        set_widget_state(Connect_Button, Send_Button, Command_Entry)
        first_find = False
    elif value == 'off':
        set_widget_state(Connect_Button, Send_Button, Command_Entry, state='disabled')
        set_connect('off')

# Tells the program whether a device is connected or not
def set_connect(value):
    global connection
    if value == 'on':
        if connection == False:
            set_widget_state(Connect_Button, text='Disconnect device', color='#F66151')
            Begin_Button.configure(state='normal')
            connection = True
    elif value == 'off':
        if connection == True:
            set_odin('off')
            Connect_Button.configure(text='Connect device', fg='#26A269')
            Begin_Button.configure(state='disabled')
            connection = False
        
# Tells the program whether an Odin session is running or not
def set_odin(value):
    global odin_running
    if value == 'on':
        if odin_running == False:
            Begin_Button.configure(text='End Odin Protocol', fg='#F66151')
            set_widget_state(Apply_Options_Button, Start_Flash_Button)
            odin_running = True
    elif value == 'off':
        if odin_running == True:
            Begin_Button.configure(text='Start Odin Protocol', fg='#26A269')
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
        print(f"An exception occurred in toggle_connection: {e}")

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
        print(f"An exception occurred in toggle_odin: {e}")

def start_flash():
    global currently_running
    try:
        invalid_file = False
        if currently_running == True:
            checkboxes = [
                (BL_Checkbox_var, BL_Entry, "BL"),
                (AP_Checkbox_var, AP_Entry, "AP"),
                (CP_Checkbox_var, CP_Entry, "CP"),
                (CSC_Checkbox_var, CSC_Entry, "CSC"),
                (USERDATA_Checkbox_var, USERDATA_Entry, "USERDATA")
            ]
            
            selected_files = []
            unique_directories = set()

            def validate_file(file_path, file_type):
                if os.path.exists(file_path):
                    if (file_path.endswith('.tar') or file_path.endswith('.zip') or file_path.endswith('.md5')):
                        return True
                    else:
                        print(f"Invalid {file_type} file selected - Files must be .tar, .zip, or .md5")
                        show_message("Invalid file", f"Files must be .tar, .zip, or .md5", [{'text': 'OK', 'fg': 'black'}], window_size=(400, 200))
                else:
                    print(f"Invalid {file_type} file selected")
                    show_message("Invalid file", f"The chosen {file_type} file does not exist", [{'text': 'OK', 'fg': 'black'}], window_size=(400, 200))
                return False
            
            for checkbox_var, entry, file_type in checkboxes:
                if currently_running:
                    if checkbox_var.get():
                        file_path = entry.get()
                        if validate_file(file_path, file_type):
                            selected_files.append(file_path)
                            unique_directories.add(os.path.dirname(file_path))

            if currently_running:
                if invalid_file == False:
                    if len(selected_files) > 0:
                        if len(unique_directories) == 1:
                            common_directory = unique_directories.pop()
                            graphical_flash = True
                            send_command(f"flashTar {common_directory}")
                        else:
                            print("Invalid files - All selected files must be in the same directory")
                            show_message("Invalid files", "All selected files must be in the same directory", [{'text': 'OK', 'fg': 'black'}], window_size=(400, 200))
                    else:
                        print("No files were selected")
                        show_message("No files selected", "Please select at least one file", [{'text': 'OK', 'fg': 'black'}], window_size=(400, 200))
    except Exception as e:
        print(f"An exception occurred in start_flash: {e}")
    
# Sets the "Options" back to default and resets the Odin archive Check-buttons/Entries
def reset():
    global currently_running
    try:
        TFlash_Option_var.set(False)
        EFSClear_Option_var.set(False)
        BootloaderUpdate_Option_var.set(False)
        ResetFlashCount_Option_var.set(True)
        BL_Checkbox_var.set(False)
        AP_Checkbox_var.set(False)
        CP_Checkbox_var.set(False)
        CSC_Checkbox_var.set(False)
        USERDATA_Checkbox_var.set(False)
        BL_Entry.delete(0, 'end')
        AP_Entry.delete(0, 'end')
        CP_Entry.delete(0, 'end')
        CSC_Entry.delete(0, 'end')
        USERDATA_Entry.delete(0, 'end')
    except Exception as e:
        print(f"An exception occurred in reset: {e}")

# Moves the correct frame to the top
def toggle_frame(name):
    frame_name = name + "_Frame"
    button_name = name + "_Button"
    frame = globals()[frame_name]
    button = globals()[button_name]
    
    frame.lift()
    buttons = [Options_Button, Pit_Button, Log_Button, Help_Button, About_Button]
    
    for btn in buttons:
        if btn == button:
            btn.configure(bg='white')
            btn.grid_configure(pady=0)
        else:
            btn.configure(bg='#E1E1E1')
            btn.grid_configure(pady=5)

def sendline_with_timeout(Thor, command, prompt, timeout):
    global clean_line
    start_time = time.time()
    while time.time() - start_time < timeout:
        if prompt in clean_line:
            Thor.sendline(command)
            return True
        time.sleep(0.3)
    return False

# Handles setting the options
def apply_options():
    tflash_status = TFlash_Option_var.get()
    efs_clear_status = EFSClear_Option_var.get()
    bootloader_update_status = BootloaderUpdate_Option_var.get()
    reset_flash_count_status = ResetFlashCount_Option_var.get()
    
    if tflash_status == 1:
        tflash_thread = Thread(target=sendline_with_timeout, args=(Thor, 'options tflash true', 'shell>', 30))
        tflash_thread.start()
        tflash_thread.join(timeout)
    if tflash_thread.is_alive():
        print("Couldn't set the option 'T-Flash' to true because it timed out")
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
    tflash_thread.join()

# Handles asking the user if they'd like to connect to a device
def select_device():
    print('yay!')
    KEY_DOWN = '\x1b[B'
    device = Output_Text.get('end-3l linestart', 'end-3l lineend')
    Connect_Device_Window = tk.messagebox.askquestion("Question", f"Do you want to connect to the device:\n'{device}'?", icon='question') 
    try:
        if Connect_Device_Window == 'yes':
            Thor.send('\n')
            if 'Now run "begin" with the protocol you need.' in Output_Text.get('end-1l linestart', 'end-1l lineend'):
                set_widget_state(Connect_Button, text='Disconnect device', color='#F66151')
                set_connect('on')
        else:
            Thor.send(KEY_DOWN)
            Thor.send('\n')
            print(Output_Text.get('end-3l linestart', 'end-3l lineend'))
            print(Output_Text.get('end-2l linestart', 'end-2l lineend'))
            if 'Cancelled by user' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
                set_connect('off')
            else:
                print('An error occurred in select_device')       
    except Exception as e:
        print(f"An exception occurred in select_device: {e}")

# Handles asking the user what partitions they'd like to flash
def select_partitions(path, name):
    global BL
    global AP
    global CP
    global CSC
    global USERDATA
    try:
        KEY_DOWN = '\x1b[B'
        SPACE_KEY = '\x20'
        tar_path = os.path.join(path, name)
        print(f'The tar_path is {tar_path}')
        tar = tarfile.open(tar_path, 'r')
        file_names = tar.getnames()
        tar.close()

        selected_partitions = []

        Choose_Partitions_Window = tk.Toplevel(window)
        Choose_Partitions_Window.title("Select partitions")
        window.configure(bg='#F0F0F0')
        
        def toggle_file(name, selected_partitions):
            if name in selected_partitions:
                selected_partitions.remove(name)
            else:
                selected_partitions.append(name)
        def select_all():
            for checkbox in Choose_Partitions_Window.winfo_children():
                if isinstance(checkbox, tk.Checkbutton):
                    checkbox.select()
                    selected_partitions.append(checkbox.cget('text'))
        def flash_selected_files():
            for file_name in selected_partitions:
                Thor.send(SPACE_KEY)
                Thor.send(KEY_DOWN)
            Thor.send('\n')
            Choose_Partitions_Window.destroy()

        Choose_Partitions_Label = tk.Label(Choose_Partitions_Window, text=f"Select what partitions to flash from:\n'{name}'.")
        Choose_Partitions_Label.grid(row=0, column=0)

        Choose_Partitions_Button = tk.Button(Choose_Partitions_Window, text="Select All", command=select_all, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
        Choose_Partitions_Button.grid(row=2, column=0)
        bind_button_events(Choose_Partitions_Button)
        
        row = 3
        
        for file_name in file_names:
            checkbox = tk.Checkbutton(Choose_Partitions_Window, text=file_name, command=lambda name=file_name: toggle_file(name, selected_partitions), bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
            checkbox.grid(row=row, column=0, sticky='w')
            row = row + 1

        Flash_Selected_Files_Button = tk.Button(Choose_Partitions_Window, text="Flash Selected Files", command=flash_selected_files, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
        Flash_Selected_Files_Button.grid()
        bind_button_events(Flash_Selected_Files_Button)
    except Exception as e:
        print(f"An exception occurred in select_partitions: {e}")

# Opens file picker when Odin archive button is clicked
def open_file(type):
    file_path = filedialog.askopenfilename(title=f"Select the {type} file")
    if file_path:
        if type == "BL":
            BL_Entry.delete(0, 'end')
            BL_Entry.insert(0, file_path)
        elif type == "AP":
            AP_Entry.delete(0, 'end')
            AP_Entry.insert(0, file_path)
        elif type == "CP":
            CP_Entry.delete(0, 'end')
            CP_Entry.insert(0, file_path)
        elif type == "CSC":
            CSC_Entry.delete(0, 'end')
            CSC_Entry.insert(0, file_path)
        elif type == "USERDATA":
            USERDATA_Entry.delete(0, 'end')
            USERDATA_Entry.insert(0, file_path)
        print("Selected file", file_path, f"as {type}")

def show_message(title, message, buttons, window_size=(300, 200)):
    Message_Window = tk.Toplevel()
    Message_Window.title(title)
    
    width, height = window_size
    screen_width = Message_Window.winfo_screenwidth()
    screen_height = Message_Window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    Message_Window.geometry(f"{width}x{height}+{x}+{y}")
    
    message_label = tk.Label(Message_Window, text=message)
    message_label.pack(padx=20, pady=20)
    
    for button in buttons:
        button_text = button.get('text', 'OK')
        button_fg = button.get('fg', 'black')
        button_command = button.get('command', Message_Window.destroy)
        
        button_widget = tk.Button(Message_Window, text=button_text, fg=button_fg, command=button_command)
        button_widget.pack(pady=10)
    
    Message_Window.mainloop()

# Opens websites
def open_link(link):
    webbrowser.open(link)

# Deals with showing links - From https://github.com/GregDMeyer/PWman/blob/master/tkHyperlinkManager.py, which itself is from http://effbot.org/zone/tkinter-text-hyperlink.htm, but that site no longer exists
class HyperlinkManager:

    def __init__(self, text):

        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<ButtonRelease-1>", self._click)

        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

# Handles stopping everthing when the window is closed, or the 'Stop Thor' button is clicked
def on_window_close():
    global Thor, currently_running, output_thread, prompt_available
    try:   
        if currently_running:
            if prompt_available == True:
                currently_running = False
                Thor.sendline('exit')
                Thor.terminate()
                Thor.wait()
                print('Stopped Thor')
                output_thread.join(timeout=0.5)  # Wait for the output thread to finish with a timeout
                print('Stopping Thor GUI...')
                window.destroy()
            elif prompt_available == False:
                Force_Close_Window = tk.Toplevel(master=window, bg="#F0F0F0")
                Force_Close_Window.title("Force Stop Thor")
                Force_Close_Window.wm_transient(window)
                Force_Close_Window.grab_set()
                Force_Close_Window.update_idletasks()
                
                def cancel_force_close():
                    Force_Close_Window.destroy()
                
                def force_close():
                    currently_running = False
                    Thor.sendline('exit')
                    Thor.terminate()
                    Thor.wait()
                    print('Stopped Thor (possibly forcibly)')
                    output_thread.join(timeout=0.5)  # Wait for the output thread to finish with a timeout
                    Force_Close_Window.destroy()
                    print('Stopping Thor GUI...')
                    window.destroy()

                Force_Close_Label = tk.Label(Force_Close_Window, text="The 'shell>' prompt isn't avalable, so the 'exit' command can't be sent.\nThor may be busy, or locked-up.\nYou may force stop Thor if you want, by clicking the 'Force Stop' button.\nHowever, if Thor is in the middle of a flash or something, there will be consequences.", font=("Monospace", 11), bg='#F0F0F0')
                Force_Close_Label.grid(row=0, column=0, columnspan=2, sticky='nesw')
                Cancel_Button = tk.Button(Force_Close_Window, text='Cancel', command=cancel_force_close, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
                Cancel_Button.grid(row=1, column=0)
                bind_button_events(Cancel_Button)
                Force_Close_Button = tk.Button(Force_Close_Window, text='Force Stop', command=force_close, fg='#F66151', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
                Force_Close_Button.grid(row=1, column=1)
                bind_button_events(Force_Close_Button)
        else:
            print('Stopping Thor GUI...')
            window.destroy()
    except Exception as e:
        print(f"An exception occurred in on_window_close: {e}")

# Changes buttons' rim color when hovered over
def on_button_hover(event, button):
    if button["state"] != "disabled":
        button.config(relief="flat", borderwidth=0, highlightbackground="#0479D7")

def on_button_leave(event, button):
    if button["state"] != "disabled":
        button.config(relief='flat', borderwidth=0, highlightbackground="#ACACAC")

def bind_button_events(button):
    button.bind("<Enter>", lambda event: on_button_hover(event, button))
    button.bind("<Leave>", lambda event: on_button_leave(event, button))

# Creates the Tkinter window
window = tk.Tk()
window.title(f"Thor GUI - {version}")

# Sets the window size
window.geometry("985x600")

# Sets the window color
window.configure(bg='#F0F0F0')

# Sets the row and column widths
window.grid_rowconfigure(3, weight=1)
window.grid_rowconfigure(4, weight=1)
window.grid_rowconfigure(5, weight=1)
window.grid_rowconfigure(6, weight=1)
window.grid_rowconfigure(7, weight=1)
window.grid_columnconfigure(5, weight=1)

# Creates the Title Label
Title_Label = tk.Label(window, text="Thor Flash Utility v1.0.4", font=("Monospace", 20), bg='#F0F0F0')
Title_Label.grid(row=0, column=0, columnspan=7, rowspan=2, sticky="nesw")

# Creates the "Start Thor" Button
Start_Button = tk.Button(window, text="Start Thor", command=start_thor, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Start_Button.grid(row=0, column=8, padx=5, sticky='ew')
bind_button_events(Start_Button)

# Creates the "Begin Odin" Button
Begin_Button = tk.Button(window, text="Begin Odin Protocol", command=toggle_odin, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Begin_Button.grid(row=0, column=10, sticky='we', pady=5, padx=5)
bind_button_events(Begin_Button)

# Creates the Command Entry
Command_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A', highlightcolor='#0078D7')
Command_Entry.grid(row=1, column=8, columnspan=2, pady=5, padx=5, sticky='nesw')

# Creates the "Send Command" Button
Send_Button = tk.Button(window, text="Send Command to Thor", command=lambda: send_command(Command_Entry.get()), state='disabled', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Send_Button.grid(row=1, column=10, sticky='we', pady=5, padx=5)
bind_button_events(Send_Button)

# Creates the "Connect" Button
Connect_Button = tk.Button(window, text="Connect", command=toggle_connection, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Connect_Button.grid(row=0,column=9, sticky='we', pady=5)
bind_button_events(Connect_Button)

# Creates the "Start" Button
Start_Flash_Button = tk.Button(window, text="Start", command=start_flash, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0, state='disabled')
Start_Flash_Button.grid(row=8, column=8, columnspan=2, sticky='ew', pady=5)
bind_button_events(Start_Flash_Button)

# Creates the "Reset" Button
Reset_Button = tk.Button(window, text="Reset", command=reset, fg='#F66151', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Reset_Button.grid(row=8, column=10, sticky='we', pady=5, padx=5)
bind_button_events(Reset_Button)

# Creates the Odin Archive Check-boxes
BL_Checkbox_var = tk.IntVar()
BL_Checkbox = tk.Checkbutton(window, variable=BL_Checkbox_var, bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
BL_Checkbox.grid(row=3, column=7)

AP_Checkbox_var = tk.IntVar()
AP_Checkbox = tk.Checkbutton(window, variable=AP_Checkbox_var, bg='#F0F0F0', highlightbackground='#F0F0F0')
AP_Checkbox.grid(row=4, column=7)

CP_Checkbox_var = tk.IntVar()
CP_Checkbox = tk.Checkbutton(window, variable=CP_Checkbox_var, bg='#F0F0F0', highlightbackground='#F0F0F0')
CP_Checkbox.grid(row=5, column=7)

CSC_Checkbox_var = tk.IntVar()
CSC_Checkbox = tk.Checkbutton(window, variable=CSC_Checkbox_var, bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
CSC_Checkbox.grid(row=6, column=7)

USERDATA_Checkbox_var = tk.IntVar()
USERDATA_Checkbox = tk.Checkbutton(window, variable=USERDATA_Checkbox_var, bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
USERDATA_Checkbox.grid(row=7, column=7)

# Creates the Odin archive Buttons
BL_Button = tk.Button(window, text="Bl", pady="5", command=lambda: open_file('BL'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
BL_Button.grid(row=3, column=8, padx='4', sticky='ew')
bind_button_events(BL_Button)

AP_Button = tk.Button(window, text="AP", pady="5", command=lambda: open_file('AP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
AP_Button.grid(row=4, column=8, padx='4', sticky='ew')
bind_button_events(AP_Button)

CP_Button = tk.Button(window, text="CP", pady="5", command=lambda: open_file('CP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CP_Button.grid(row=5, column=8, padx='4', sticky='ew')
bind_button_events(CP_Button)

CSC_Button = tk.Button(window, text="CSC", pady="5", command=lambda: open_file('CSC'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CSC_Button.grid(row=6, column=8, padx='4', sticky='ew')
bind_button_events(CSC_Button)

USERDATA_Button = tk.Button(window, text="USERDATA", pady=5, command=lambda: open_file('USERDATA'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
USERDATA_Button.grid(row=7, column=8, padx='4', sticky='ew')
bind_button_events(USERDATA_Button)

# Creates the Odin archive Entries
BL_Entry = tk.Entry(window, bg='#F0F0F0', highlightcolor='#0078D7', relief='flat', highlightbackground='#7A7A7A')
BL_Entry.grid(row=3, column=9, columnspan=2, sticky='we', padx=5)

AP_Entry = tk.Entry(window, bg='#F0F0F0', highlightcolor='#0078D7', relief='flat', highlightbackground='#7A7A7A')
AP_Entry.grid(row=4, column=9, columnspan=2, sticky='we', padx=5)

CP_Entry = tk.Entry(window, bg='#F0F0F0', highlightcolor='#0078D7', relief='flat', highlightbackground='#7A7A7A')
CP_Entry.grid(row=5, column=9, columnspan=2, sticky='we', padx=5)

CSC_Entry = tk.Entry(window, bg='#F0F0F0', highlightcolor='#0078D7', relief='flat', highlightbackground='#7A7A7A')
CSC_Entry.grid(row=6, column=9, columnspan=2, sticky='we', padx=5)

USERDATA_Entry = tk.Entry(window, bg='#F0F0F0', highlightcolor='#0078D7', relief='flat', highlightbackground='#7A7A7A')
USERDATA_Entry.grid(row=7, column=9, columnspan=2, sticky='we', padx=5)

# Creates the five Frame Buttons
Log_Button = tk.Button(window, text='Log', command=lambda:toggle_frame('Log'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Log_Button.grid(row=2, column=0, sticky='wes', pady=5, padx=5)

Options_Button = tk.Button(window, text='Options', command=lambda:toggle_frame('Options'), bg='#E1E1E1', highlightbackground='#ACACAC', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Options_Button.grid(row=2, column=1, sticky='wes', pady=5)

Pit_Button = tk.Button(window, text='Pit', command=lambda:toggle_frame('Pit'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Pit_Button.grid(row=2, column=2, sticky='wes', pady=5, padx=5)

Help_Button = tk.Button(window, text='Help', command=lambda:toggle_frame('Help'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Help_Button.grid(row=2, column=3, sticky='wes', pady=5)

About_Button = tk.Button(window, text='About', command=lambda:toggle_frame('About'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
About_Button.grid(row=2, column=4, sticky='wes', pady=5, padx=5)

# Creates the "Log" frame
Log_Frame = tk.Frame(window, bg='white')
Log_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
Log_Frame.grid_columnconfigure(0, weight=1)
Log_Frame.grid_rowconfigure(0, weight=1)

Output_Text = scrolledtext.ScrolledText(Log_Frame, state="disabled", highlightthickness=0, font=("Monospace", 9))
Output_Text.grid(row=0, column=0, rowspan=6, sticky='nesw')

# Creates the "Options" frame and check-boxes
Options_Frame = tk.Frame(window, bg='white')
Options_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)

TFlash_Option_var = tk.IntVar()
TFlash_Option = tk.Checkbutton(Options_Frame, variable=TFlash_Option_var, text='T Flash', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
TFlash_Option.grid(row=0, column=0, pady=10, padx=10, sticky='w')

TFlash_Label = tk.Label(Options_Frame, text='Writes the bootloader of a working device onto the SD card', bg='white', cursor='hand2')
TFlash_Label.grid(row=1, column=0, pady=10, padx=10, sticky='w')

TFlash_Label.bind("<ButtonRelease-1>", lambda e: open_link('https://android.stackexchange.com/questions/196304/what-does-odins-t-flash-option-do'))

EFSClear_Option_var = tk.IntVar()
EFSClear_Option = tk.Checkbutton(Options_Frame, variable=EFSClear_Option_var, text='EFS Clear', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
EFSClear_Option.grid(row=2, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label = tk.Label(Options_Frame, text='Wipes the EFS partition (WARNING: You better know what you\'re doing!)', bg='white', cursor='hand2')
EFSClear_Label.grid(row=3, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label.bind("<ButtonRelease-1>", lambda e: open_link('https://android.stackexchange.com/questions/185679/what-is-efs-and-msl-in-android'))

BootloaderUpdate_Option_var = tk.IntVar()
BootloaderUpdate_Option = tk.Checkbutton(Options_Frame, variable=BootloaderUpdate_Option_var, text='Bootloader Update', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
BootloaderUpdate_Option.grid(row=4, column=0, pady=10, padx=10, sticky='w')

BootloaderUpdate_Label = tk.Label(Options_Frame, text='', bg='white')
BootloaderUpdate_Label.grid(row=5, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Option_var = tk.IntVar(value=True)
ResetFlashCount_Option = tk.Checkbutton(Options_Frame, variable=ResetFlashCount_Option_var, text='Reset Flash Count', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
ResetFlashCount_Option.grid(row=6, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Label = tk.Label(Options_Frame, text='', bg='white')
ResetFlashCount_Label.grid(row=7, column=0, pady=10, padx=10, sticky='w')

Apply_Options_Button = tk.Button(Options_Frame, text='Apply', command=apply_options, state='disabled', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Apply_Options_Button.grid(row=8, column=0, pady=10, padx=10, sticky='w')
bind_button_events(Apply_Options_Button)

# Creates the "Pit" frame
Pit_Frame = tk.Frame(window, bg='white')
Pit_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)

Test_Label = tk.Label(Pit_Frame, text='Just a test :)', bg='#F0F0F0')
Test_Label.grid(row=0, column=0, pady=10, padx=10, sticky='w')

Although_Label = tk.Label(Pit_Frame, text='Pull requests are always welcome though!', bg='#F0F0F0')
Although_Label.grid(row=1, column=0, pady=10, padx=10, sticky='w')

# Creates the "Help" frame
Help_Frame = tk.Frame(window, bg='white')
Help_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
Help_Frame.grid_columnconfigure(0, weight=1)

Help_Label = tk.Label(Help_Frame, text='Need help?', bg='white', font=("Monospace", 13))
Help_Label.grid(row=0, column=0, sticky='ew')

Get_Help_Text = tk.Text(Help_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
Get_Help_Text.grid(row=2, column=0, sticky='ew')
hyperlink = HyperlinkManager(Get_Help_Text)
Get_Help_Text.tag_configure("center", justify='center')
Get_Help_Text.insert(tk.END, "Let me know on ")
Get_Help_Text.insert(tk.END, "XDA", hyperlink.add(partial(open_link, 'https://forum.xda-developers.com/t/poll-would-a-gui-for-linux-odin4-and-or-thor-be-helpful.4604333/')))
Get_Help_Text.insert(tk.END, ", or open an issue on ")
Get_Help_Text.insert(tk.END, "GitHub", hyperlink.add(partial(open_link, 'https://github.com/ethical-haquer/Thor_GUI')))
Get_Help_Text.insert(tk.END, ".")
Get_Help_Text.tag_add("center", "1.0", "end")
Get_Help_Text.config(state=tk.DISABLED) 

Help_Label_2 = tk.Label(Help_Frame, text='', bg='white')
Help_Label_2.grid(row=3, column=0, sticky='ew')

Help_Label_3 = tk.Label(Help_Frame, text='Found an issue?', bg='white', font=("Monospace", 13))
Help_Label_3.grid(row=4, column=0, sticky='ew')

Report_Text = tk.Text(Help_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
Report_Text.grid(row=5, column=0, sticky='ew')
hyperlink = HyperlinkManager(Report_Text)
Report_Text.tag_configure("center", justify='center')
Report_Text.insert(tk.END, "If it isn't listed ")
Report_Text.insert(tk.END, "here", hyperlink.add(partial(open_link, 'https://github.com/ethical-haquer/Thor_GUI#known-bugs')))
Report_Text.insert(tk.END, ", you can ")
Report_Text.insert(tk.END, "report it", hyperlink.add(partial(open_link, 'https://github.com/ethical-haquer/Thor_GUI/issues/new?assignees=&labels=&projects=&template=bug_report.md&title=')))
Report_Text.insert(tk.END, ".")
Report_Text.tag_add("center", "1.0", "end")
Report_Text.config(state=tk.DISABLED) 

# Creates the "About" frame
About_Frame = tk.Frame(window, bg='white')
About_Frame.grid(row=3, rowspan=6, column=0, columnspan=7, sticky='nesw', padx=5)
About_Frame.grid_columnconfigure(0, weight=1)

Thor_GUI_Label = tk.Label(About_Frame, text='Thor GUI', bg='white', font=("Monospace", 13))
Thor_GUI_Label.grid(sticky='ew')

Thor_GUI_Label_2 = tk.Label(About_Frame, text=f'{version}', bg='white', font=('Monospace', 11))
Thor_GUI_Label_2.grid(sticky='ew')

Thor_GUI_Label_3 = tk.Label(About_Frame, text='A GUI for the Thor Flash Utility', bg='white', font=('Monospace', 11))
Thor_GUI_Label_3.grid(sticky='ew')

Thor_GUI_Websites_Text = tk.Text(About_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
Thor_GUI_Websites_Text.grid(sticky='ew')
hyperlink = HyperlinkManager(Thor_GUI_Websites_Text)
Thor_GUI_Websites_Text.tag_configure("center", justify='center')
Thor_GUI_Websites_Text.insert(tk.END, "GitHub", hyperlink.add(partial(open_link, 'https://github.com/ethical-haquer/Thor_GUI')))
Thor_GUI_Websites_Text.insert(tk.END, ", ")
Thor_GUI_Websites_Text.insert(tk.END, "XDA", hyperlink.add(partial(open_link, 'https://forum.xda-developers.com/t/poll-would-a-gui-for-linux-odin4-and-or-thor-be-helpful.4604333/')))
Thor_GUI_Websites_Text.tag_add("center", "1.0", "end")
Thor_GUI_Websites_Text.config(state=tk.DISABLED)

Thor_GUI_Label_8 = tk.Label(About_Frame, text='Built around the:', bg='white', font=('Monospace', 11))
Thor_GUI_Label_8.grid(sticky='ew')

Thor_GUI_Label_18 = tk.Label(About_Frame, text='', bg='white')
Thor_GUI_Label_18.grid(sticky='ew')

Thor_GUI_Label_9 = tk.Label(About_Frame, text='Thor Flash Utility', bg='white', font=("Monospace", 13))
Thor_GUI_Label_9.grid(sticky='ew')

Thor_GUI_Label_10 = tk.Label(About_Frame, text='v1.0.4', bg='white', font=('Monospace', 11))
Thor_GUI_Label_10.grid(sticky='ew')

Thor_GUI_Label_11 = tk.Label(About_Frame, text='An alternative to Heimdall', bg='white', font=('Monospace', 11))
Thor_GUI_Label_11.grid(sticky='ew')

Thor_Websites_Text = tk.Text(About_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
Thor_Websites_Text.grid(sticky='ew')
hyperlink = HyperlinkManager(Thor_Websites_Text)
Thor_Websites_Text.tag_configure("center", justify='center')
Thor_Websites_Text.insert(tk.END, "GitHub", hyperlink.add(partial(open_link, 'https://github.com/Samsung-Loki/Thor')))
Thor_Websites_Text.insert(tk.END, ", ")
Thor_Websites_Text.insert(tk.END, "XDA", hyperlink.add(partial(open_link, 'https://forum.xda-developers.com/t/dev-thor-flash-utility-the-new-samsung-flash-tool.4597355/')))
Thor_Websites_Text.tag_add("center", "1.0", "end")
Thor_Websites_Text.config(state=tk.DISABLED)

Thor_GUI_Label_20 = tk.Label(About_Frame, text='', bg='white')
Thor_GUI_Label_20.grid(sticky='ew')

Thor_GUI_Label_21 = tk.Label(About_Frame, text='Credits:', bg='white', font=('Monospace', 13))
Thor_GUI_Label_21.grid(sticky='ew')

TheAirBlow_Text = tk.Text(About_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
TheAirBlow_Text.grid(sticky='ew')
hyperlink = HyperlinkManager(TheAirBlow_Text)
TheAirBlow_Text.tag_configure("center", justify='center')
TheAirBlow_Text.insert(tk.END, "TheAirBlow", hyperlink.add(partial(open_link, 'https://github.com/TheAirBlow')))
TheAirBlow_Text.insert(tk.END, " for Thor Flash Utility")
TheAirBlow_Text.tag_add("center", "1.0", "end")
TheAirBlow_Text.config(state=tk.DISABLED)

ethical_haquer_Text = tk.Text(About_Frame, bg='white', font=("Monospace", 11), height=1, bd=0, highlightthickness=0, wrap="word")
ethical_haquer_Text.grid(sticky='ew')
hyperlink = HyperlinkManager(ethical_haquer_Text)
ethical_haquer_Text.tag_configure("center", justify='center')
ethical_haquer_Text.insert(tk.END, "Myself, ")
ethical_haquer_Text.insert(tk.END, "ethical_haquer", hyperlink.add(partial(open_link, 'https://github.com/ethical-haquer')))
ethical_haquer_Text.insert(tk.END, ", for Thor GUI")
ethical_haquer_Text.tag_add("center", "1.0", "end")
ethical_haquer_Text.config(state=tk.DISABLED)

Thor_GUI_Label_17 = tk.Label(About_Frame, text='', bg='white')
Thor_GUI_Label_17.grid(sticky='ew')

Thor_GUI_Label_6 = tk.Label(About_Frame, text='This program comes with absolutely no warranty.', bg='white', font=("Monospace", 9))
Thor_GUI_Label_6.grid(sticky='ew')

Thor_GUI_Label_7 = tk.Label(About_Frame, text='See the GNU General Public License, version 3 or later for details.', bg='white', font=("Monospace", 9))
Thor_GUI_Label_7.grid(sticky='ew')

Thor_GUI_Label_16 = tk.Label(About_Frame, text='', bg='white')
Thor_GUI_Label_16.grid(sticky='ew')

Thor_GUI_Label_14 = tk.Label(About_Frame, text='Thor Flash Utility comes with absolutely no warranty.', bg='white', font=("Monospace", 9))
Thor_GUI_Label_14.grid(sticky='ew')

Thor_GUI_Label_15 = tk.Label(About_Frame, text='See the Mozilla Public License, version 2 or later for details.', bg='white', font=("Monospace", 9))
Thor_GUI_Label_15.grid(sticky='ew')

# Configures the tags for coloring the output text
Output_Text.tag_configure('green', foreground='#26A269')
Output_Text.tag_configure('yellow', foreground='#E9AD0C')
Output_Text.tag_configure('red', foreground='#F66151')
Output_Text.tag_configure('blue', foreground='#33C7DE')
Output_Text.tag_configure('green_italic', foreground='#26A269', font=('Monospace', 9, 'italic'))
Output_Text.tag_configure('orange', foreground='#E9AD0C')
Output_Text.tag_configure('dark_blue', foreground='#2A7BDE')

# Raises the "Log" frame to top on start-up
toggle_frame('Log')

# Binds the on_window_close function to the window's close event
window.protocol("WM_DELETE_WINDOW", on_window_close)

# Runs the Tkinter event loop
window.mainloop()
