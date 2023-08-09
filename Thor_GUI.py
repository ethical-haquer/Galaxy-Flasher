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
# Version: Alpha v0.1
# By: ethical_haquer
# Released: 8-9-23
# Known issues: Numerous :)

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import pexpect
from threading import Thread
import re
import webbrowser
from time import sleep

version = 'Alpha v0.1'

currently_running = False
odin_running = False
Thor = None
output_thread = None
stop_threads = False
connection = False
first_find = True
tag= 'default_tag'

print(f'Running Thor GUI - {version}...')

# This starts and stops the Thor
def start_thor():
    global Thor, output_thread, currently_running, stop_threads
    try:
        if currently_running:
            if 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend'):
                Thor.sendline('exit')
                stop_threads = True  # Set the flag to stop the threads
                Thor.terminate()
                Thor.wait()
                output_thread.join(timeout=1)  # Wait for the output thread to finish with a timeout
                print('Stopped Thor')
                window.destroy()
        elif not currently_running:
            Thor = pexpect.spawn('dotnet /PATH/TO/TheAirBlow.Thor.Shell.dll', timeout=None, encoding='utf-8')
            output_thread = Thread(target=update_output)
            output_thread.daemon = True
            output_thread.start()
            currently_running = True
            Start_Button.configure(text='Stop Thor (and program)', fg='#F66151', padx=10)
            print('Started Thor')
    except pexpect.exceptions.TIMEOUT:
            print('A Timeout Occurred in start_thor')
    except Exception as e:
        print(f"An exception occurred in toggle_odin: {e}")

# What most commands go through
def send_command(command):
    global Thor
    if currently_running:
        try:
            if 'exit' in command or 'quit' in command:
                print('Sadly, stopping Thor independently is currently not supported by this program. To stop Thor, either click the: \'Stop Thor (and program)\' button, or close the window.')
            else:   
                if 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend'):
                    Thor.sendline(command)
                    Output_Text.see(tk.END)
                    print(f'Sent command: \'{command}\'')
                else:
                    print(f'The \'shell>\' prompt is currently not available, couldn\'t send the command: \'{command}\'')
        except Exception as e:
            print(f"An exception occurred in send_command: {e}")

# Deals with enabling/disabling buttons - Mainly used by set_thor(), set_connect(), and set_odin()
def set_widget_state(*args, state="normal", text=None, color=None):
    for widget in args:
        widget.configure(state=state, text=text)
        if color is not None:
            widget.configure(fg=color)
        if text is not None:
            widget.configure(text=text)

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
        
# Perhaps the most important part of the program, along with scan_output - Handles displaying the output from Thor, while scan_output calls other functions when it detects a certain line in the output
def update_output():
    global tag
    global connection
    global cleaned_line2
    while True:
        try:
            chunk = Thor.read_nonblocking(4096, timeout=0)
            if chunk:
                output_lines = chunk.splitlines()
                for line in output_lines:
                    cleaned_line = re.sub(r'\x1b\[[?0-9;]*[A-Za-z]', '', line).strip()
                    cleaned_line2 = re.sub('\x1b=', '', cleaned_line).strip()
                    determine_tag(cleaned_line2)
                    Output_Text.configure(state='normal')
                    Output_Text.insert(tk.END, cleaned_line2 + '\n', tag)
                    Output_Text.configure(state='disabled')
                    Output_Text.see(tk.END)
                    scan_output()
        except pexpect.exceptions.TIMEOUT as e:
            pass
        except Exception as e:
            print(f"An exception occurred in update_output: '{e}'")
        # Delay between each update
        sleep(0.1)

def scan_output():
    global cleaned_line2
    try:
        if 'shell>' in cleaned_line2:
            set_thor('on')
        if 'Successfully began an Odin session!' in cleaned_line2:
            set_odin('on')
        if 'Successfully disconnected the device!' in cleaned_line2:
            set_connect('off')
        if 'Successfully connected to the device!' in cleaned_line2:
            set_connect('on')
        if 'Cancel operation' in Output_Text.get('end-6l linestart', 'end-6l lineend') and 'Choose a device to connect to:' in Output_Text.get('end-5l linestart', 'end-5l lineend'):
            device()
        if 'Successfully ended an Odin session!' in cleaned_line2:
            set_odin('off')
        if '" is set to "' in cleaned_line2:
            if 'Option "T-Flash" is set to "False"' in cleaned_line2:
                TFlash_Option_var = tk.IntVar(value=False)
            if 'Option "T-Flash" is set to "True"' in cleaned_line2:
                TFlash_Option_var = tk.IntVar(value=True)
            if 'Option "EFS Clear" is set to "False"' in cleaned_line2:
                EFSClear_Option_var = tk.IntVar(value=False)
            if 'Option "EFS Clear" is set to "True"' in cleaned_line2:
                EFSClear_Option_var = tk.IntVar(value=True)
            if 'Option "Bootloader Update" is set to "False"' in cleaned_line2:
                BootloaderUpdate_Option_var = tk.IntVar(value=False)
            if 'Option "Bootloader Update" is set to "True"' in cleaned_line2:
                BootloaderUpdate_Option_var = tk.IntVar(value=True)
            if 'Option "Reset Flash Count" is set to "False"' in cleaned_line2:
                ResetFlashCount_Option_var = tk.IntVar(value=False)
            if 'Option "Reset Flash Count" is set to "True"' in cleaned_line2:
                ResetFlashCount_Option_var = tk.IntVar(value=True)
    except Exception as e:
            print(f"An exception occurred in scan_output: '{e}'")

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

# Moves the correct frame to the top
def toggle_options():
    Options_Frame.lift()
    Options_Button.configure(bg='white')
    Options_Button.grid_configure(pady=0)
    Pit_Button.configure(bg='#E1E1E1')
    Pit_Button.grid_configure(pady=5)
    Log_Button.configure(bg='#E1E1E1')
    Log_Button.grid_configure(pady=5)

def toggle_pit():
    Pit_Frame.lift()
    Pit_Button.configure(bg='white')
    Pit_Button.grid_configure(pady=0)
    Options_Button.configure(bg='#E1E1E1')
    Options_Button.grid_configure(pady=5)
    Log_Button.configure(bg='#E1E1E1')
    Log_Button.grid_configure(pady=5)

def toggle_log():
    Log_Frame.lift()
    Log_Button.configure(bg='white')
    Log_Button.grid_configure(pady=0)
    Options_Button.configure(bg='#E1E1E1')
    Options_Button.grid_configure(pady=5)
    Pit_Button.configure(bg='#E1E1E1')
    Pit_Button.grid_configure(pady=5)

# Handles setting the options
def apply_options():
    tflash_status = TFlash_Option_var.get()
    efs_clear_status = EFSClear_Option_var.get()
    bootloader_update_status = BootloaderUpdate_Option_var.get()
    reset_flash_count_status = ResetFlashCount_Option_var.get()
    print('pass: 1')
    if tflash_status == 1:
        print('pass: 2')
        send_command('options tflash true')
        print('pass: 3')
    if efs_clear_status == 1:
        print('Would have set the option "EFSClear" to true, but it is currently disabled due to how destructive it is.')
#        send_command('options efsclear true')
    elif efs_clear_status == 0:
        send_command('options efsclear false')
    if bootloader_update_status == 1:
        send_command('options blupdate true')
    elif bootloader_update_status == 0:
        send_command('options blupdate false')
    if reset_flash_count_status == 1:
        send_command('options resetfc true')
    elif reset_flash_count_status == 0:
        send_command('options resetfc false')

# Tells the program whether Thor is running or not
def set_thor(value):
    global first_find
    if value == 'on':
#       This check is here because otherwise the output is full of "set_widget_state is running...", in this case unnecessarily
        if first_find == True:
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
            set_widget_state(BL_Checkbox, AP_Checkbox, CP_Checkbox, CSC_Checkbox, USERDATA_Checkbox, BL_Button, AP_Button, CP_Button, CSC_Button, USERDATA_Button, BL_Entry, AP_Entry, CP_Entry, CSC_Entry, USERDATA_Entry, TFlash_Option, EFSClear_Option, BootloaderUpdate_Option, ResetFlashCount_Option, Apply_Options_Button)
            odin_running = True
    elif value == 'off':
        if odin_running == True:
            Begin_Button.configure(text='Start Odin Protocol', fg='#26A269')
            set_widget_state(BL_Checkbox, AP_Checkbox, CP_Checkbox, CSC_Checkbox, USERDATA_Checkbox, BL_Button, AP_Button, CP_Button, CSC_Button, USERDATA_Button, BL_Entry, AP_Entry, CP_Entry, CSC_Entry, USERDATA_Entry, TFlash_Option, EFSClear_Option, BootloaderUpdate_Option, ResetFlashCount_Option, Apply_Options_Button, state='disabled')
            odin_running == False

# Handles asking the user if they'd like to connect to the device
def device():
    KEY_DOWN = '\x1b[B'
    device = Output_Text.get('end-3l linestart', 'end-3l lineend')
    Connect_Device_Box = tk.messagebox.askquestion("Question", f"Do you want to connect to the device:\n'{device}'?", icon='question') 
    try:
        if Connect_Device_Box == 'yes':
            Thor.send('\n')
            if 'Now run "begin" with the protocol you need.' in Output_Text.get('end-1l linestart', 'end-1l lineend'):
                set_widget_state(Connect_Button, text='Disconnect device', color='#F66151')
                set_connect('on')
        else:
            Thor.send(KEY_DOWN)
            Thor.send('\n')
            if 'Cancelled by user' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
                set_connect('off')
            else:
                print('An error occurred in device')       
    except Exception as e:
        print(f"An exception occurred in device: {e}")

# Opens file picker when Odin archive button is clicked
def open_file(type):
    file_path = filedialog.askopenfilename()
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

# Opens website when option description is clicked
def open_link(link):
    webbrowser.open(link)

# Handles stopping everthing when the window is closed
def on_window_close():
    global Thor, output_thread, stop_threads
    if currently_running:
        if 'shell>' in Output_Text.get("1.0", tk.END):
            Thor.sendline('exit')
            stop_threads = True  # Set the flag to stop the threads
            Thor.terminate()
            Thor.wait()
            output_thread.join(timeout=0.5)  # Wait for the output thread to finish with a timeout
    window.destroy()

# Changes buttons' rim color when hovered over
def on_button_hover(event, button):
    button.config(relief="flat", borderwidth=0, highlightbackground="#0479D7")

def on_button_leave(event, button):
    button.config(relief='flat', borderwidth=0, highlightbackground="#ACACAC")

def bind_button_events(button):
    button.bind("<Enter>", lambda event: on_button_hover(event, button))
    button.bind("<Leave>", lambda event: on_button_leave(event, button))

# Creates the Tkinter window
window = tk.Tk()
window.title("Thor GUI - Alpha v0.1")

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
window.grid_columnconfigure(3, weight=1)

# Creates the Title Label
Title_Label = tk.Label(window, text="Thor Flash Utility v1.0.4", font=("Monospace", 20), bg='#F0F0F0')
Title_Label.grid(row=0, column=0, columnspan=7, rowspan=2, sticky="nesw")

# Creates the "Start Thor" Button
Start_Button = tk.Button(window, text="Start Thor", command=start_thor, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0, padx=57.5)
Start_Button.grid(row=0, column=8, sticky='we', pady=5, padx=5)

# Creates the "Begin Odin" Button
Begin_Button = tk.Button(window, text="Begin Odin Protocol", command=toggle_odin, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Begin_Button.grid(row=0, column=10, sticky='we', pady=5, padx=5)

# Creates the Command Entry
Command_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
Command_Entry.grid(row=1, column=8, columnspan=2, sticky='nesw', pady=5, padx=5)

# Creates the "Send Command" Button
Send_Button = tk.Button(window, text="Send Command to Thor", command=lambda: send_command(Command_Entry.get()), state='disabled', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Send_Button.grid(row=1, column=10, sticky='we', pady=5, padx=5)

# Creates the "Connect" Button
Connect_Button = tk.Button(window, text="Connect", command=toggle_connection, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Connect_Button.grid(row=0,column=9, pady=5)

# Creates the Odin archive Check-boxes
BL_Checkbox_var = tk.IntVar()
BL_Checkbox = tk.Checkbutton(window, variable=BL_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
BL_Checkbox.grid(row=3, column=7)

AP_Checkbox_var = tk.IntVar()
AP_Checkbox = tk.Checkbutton(window, variable=AP_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0')
AP_Checkbox.grid(row=4, column=7)

CP_Ckeckbox_var = tk.IntVar()
CP_Checkbox = tk.Checkbutton(window, variable=CP_Ckeckbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0')
CP_Checkbox.grid(row=5, column=7)

CSC_Checkbox_var = tk.IntVar()
CSC_Checkbox = tk.Checkbutton(window, variable=CSC_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
CSC_Checkbox.grid(row=6, column=7)

USERDATA_Checkbox_var = tk.IntVar()
USERDATA_Checkbox = tk.Checkbutton(window, variable=USERDATA_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
USERDATA_Checkbox.grid(row=7, column=7)

# Creates the Odin archive Buttons
BL_Button = tk.Button(window, text="Bl", pady="5", state='disabled', command=lambda: open_file('BL'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
BL_Button.grid(row=3, column=8, sticky='ew', padx='4')
bind_button_events(BL_Button)

AP_Button = tk.Button(window, text="AP", pady="5", state='disabled', command=lambda: open_file('AP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
AP_Button.grid(row=4, column=8, sticky='ew', padx='4')
bind_button_events(AP_Button)

CP_Button = tk.Button(window, text="CP", pady="5", state='disabled', command=lambda: open_file('CP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CP_Button.grid(row=5, column=8, sticky='ew', padx='4')
bind_button_events(CP_Button)

CSC_Button = tk.Button(window, text="CSC", pady="5", state='disabled', command=lambda: open_file('CSC'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CSC_Button.grid(row=6, column=8, sticky='ew', padx='4')
bind_button_events(CSC_Button)

USERDATA_Button = tk.Button(window, text="USERDATA", pady=5, state='disabled', command=lambda: open_file('USERDATA'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
USERDATA_Button.grid(row=7, column=8, sticky='ew', padx='4')
bind_button_events(USERDATA_Button)

# Creates the Odin archive Entries
BL_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
BL_Entry.grid(row=3, column=9, columnspan=2, sticky='we', padx=5)

AP_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
AP_Entry.grid(row=4, column=9, columnspan=2, sticky='we', padx=5)

CP_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
CP_Entry.grid(row=5, column=9, columnspan=2, sticky='we', padx=5)

CSC_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
CSC_Entry.grid(row=6, column=9, columnspan=2, sticky='we', padx=5)

USERDATA_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
USERDATA_Entry.grid(row=7, column=9, columnspan=2, sticky='we', padx=5)

# Creates the three Frame Buttons
Log_Button = tk.Button(window, text='Log', command=toggle_log, bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Log_Button.grid(row=2, column=0, sticky='wes', pady=5, padx=5)

Options_Button = tk.Button(window, text='Options', command=toggle_options, bg='#E1E1E1', highlightbackground='#ACACAC', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Options_Button.grid(row=2, column=1, sticky='wes', pady=5)

Pit_Button = tk.Button(window, text='Pit', command=toggle_pit, bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Pit_Button.grid(row=2, column=2, sticky='wes', pady=5, padx=5)

# Creates the "Options" frame and check-boxes
Options_Frame = tk.Frame(window, bg='white')
Options_Frame.grid(row=3, rowspan=5, column=0, columnspan=7, sticky='nesw', padx=5)

TFlash_Option_var = tk.IntVar()
TFlash_Option = tk.Checkbutton(Options_Frame, variable=TFlash_Option_var, text='T Flash', state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
TFlash_Option.grid(row=0, column=0, pady=10, padx=10, sticky='w')

TFlash_Label = tk.Label(Options_Frame, text='Writes the bootloader of a working device onto the SD card', bg='white', cursor='hand2')
TFlash_Label.grid(row=1, column=0, pady=10, padx=10, sticky='w')

TFlash_Label.bind("<Button-1>", lambda e: open_link('https://android.stackexchange.com/questions/196304/what-does-odins-t-flash-option-do'))

EFSClear_Option_var = tk.IntVar()
EFSClear_Option = tk.Checkbutton(Options_Frame, variable=EFSClear_Option_var, text='EFS Clear', state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
EFSClear_Option.grid(row=2, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label = tk.Label(Options_Frame, text='Wipes the EFS partition (WARNING: You better know what you\'re doing!)', bg='white', cursor='hand2')
EFSClear_Label.grid(row=3, column=0, pady=10, padx=10, sticky='w')

EFSClear_Label.bind("<Button-1>", lambda e: open_link('https://android.stackexchange.com/questions/185679/what-is-efs-and-msl-in-android'))

BootloaderUpdate_Option_var = tk.IntVar()
BootloaderUpdate_Option = tk.Checkbutton(Options_Frame, variable=BootloaderUpdate_Option_var, text='Bootloader Update', state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
BootloaderUpdate_Option.grid(row=4, column=0, pady=10, padx=10, sticky='w')

BootloaderUpdate_Label = tk.Label(Options_Frame, text='', bg='white')
BootloaderUpdate_Label.grid(row=5, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Option_var = tk.IntVar(value=True)
ResetFlashCount_Option = tk.Checkbutton(Options_Frame, variable=ResetFlashCount_Option_var, text='Reset Flash Count', state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', highlightcolor='#F0F0F0', activebackground='#F0F0F0', relief='flat')
ResetFlashCount_Option.grid(row=6, column=0, pady=10, padx=10, sticky='w')

ResetFlashCount_Label = tk.Label(Options_Frame, text='', bg='white')
ResetFlashCount_Label.grid(row=7, column=0, pady=10, padx=10, sticky='w')

Apply_Options_Button = tk.Button(Options_Frame, text='Apply', command=apply_options, state='disabled', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Apply_Options_Button.grid(row=8, column=0, pady=10, padx=10, sticky='w')
bind_button_events(Apply_Options_Button)

# Creates the "Pit" frame
Pit_Frame = tk.Frame(window, bg='white')
Pit_Frame.grid(row=3, rowspan=5, column=0, columnspan=7, sticky='nesw', padx=5)

Test_Label = tk.Label(Pit_Frame, text='Just a test :)', bg='#F0F0F0')
Test_Label.grid(row=0, column=0, pady=10, padx=10, sticky='w')

Although_Label = tk.Label(Pit_Frame, text='Pull requests are always welcome though!', bg='#F0F0F0')
Although_Label.grid(row=1, column=0, pady=10, padx=10, sticky='w')

# Creates the "Log" frame
Log_Frame = tk.Frame(window, bg='white')
Log_Frame.grid(row=3, rowspan=5, column=0, columnspan=7, sticky='nesw', padx=5)
Log_Frame.grid_columnconfigure(0, weight=1)
Log_Frame.grid_rowconfigure(0, weight=1)

Output_Text = scrolledtext.ScrolledText(Log_Frame, state="disabled", highlightthickness=0, font=("Monospace", 9))
Output_Text.grid(row=0, column=0, rowspan=6, sticky='nesw')

# Configures the tags for coloring the output text
Output_Text.tag_configure('green', foreground='#26A269')
Output_Text.tag_configure('yellow', foreground='#E9AD0C')
Output_Text.tag_configure('red', foreground='#F66151')
Output_Text.tag_configure('blue', foreground='#33C7DE')
Output_Text.tag_configure('green_italic', foreground='#26A269', font=('Monospace', 9, 'italic'))
Output_Text.tag_configure('orange', foreground='#E9AD0C')
Output_Text.tag_configure('dark_blue', foreground='#2A7BDE')

# Raises the "Log" frame to top on start-up
toggle_log()

# Binds the on_window_close function to the window's close event
window.protocol("WM_DELETE_WINDOW", on_window_close)

# Runs the Tkinter event loop
window.mainloop()
