# Name: Thor Flash Utility GUI
# Version: pre-alpha 2.0
# By: ethical_haquer @ XDA
# Released: 8-1-23
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

version = 'pre-alpha 2.0'

currently_running = False
odin_running = False
Thor = None
output_thread = None
stop_threads = False
connect = False

print(f'Running Thor Flash Utility GUI - Version {version}...')

def start_thor():
    global Thor, output_thread, currently_running, stop_threads
    try:
        if currently_running:
            Thor.expect('shell>')
            Thor.sendline('exit')
            stop_threads = True  # Set the flag to stop the threads
            Thor.terminate()
            Thor.wait()
            output_thread.join(timeout=1)  # Wait for the output thread to finish with a timeout
            print('Stopped Thor')
            window.destroy()
        elif not currently_running:
            Thor = pexpect.spawn('dotnet /home/nah/Thor/TheAirBlow.Thor.Shell.dll', timeout=None, encoding='utf-8')
            output_thread = Thread(target=update_output)
            output_thread.daemon = True
            output_thread.start()
            currently_running = True
            Start_Button.configure(text='Stop Thor (and program)', fg='#F66151', padx=10)
            print('Started Thor')
    except pexpect.exceptions.TIMEOUT:
            # Handle timeout here
            print('A Timeout Occurred in start_thor')

def begin_odin():
    global odin_running
    global currently_running
    if odin_running:
        send_command('end')
        odin_running = False
        Begin_Button.configure(text='End Odin Protocol', fg='#F66151')
    elif not odin_running:
        send_command('begin odin')
        odin_running = True
        Begin_Button.configure(text='Begin Odin Protocol', fg='#26A269')

def send_command(command):
    global Thor
    if currently_running:
        try:
            if command == 'exit' or command == 'quit':
                print('Sadly, stopping Thor independently is not supported by this program. To stop Thor, either click the \'Stop Thor (and program)\' button, or close the window.')
            else:   
#                Thor.expect(['shell>'], timeout=0.5)
                if 'shell>' in Output_Text.get("1.0", tk.END):
                    Thor.sendline(command)
                    Output_Text.see(tk.END)
                    print(f'Sent command: \'{command}\'')
        except pexpect.exceptions.TIMEOUT:
            # Handle timeout here
            print('A Timeout Occurred in send_command')

def set_widget_state(*args, state="normal", text=None, color=None):
    print('set_widget_state is running...')
    for widget in args:
        widget.configure(state=state, text=text)
        if color is not None:
            widget.configure(fg=color)
        if text is not None:
            widget.configure(text=text)

def determine_tag(line):
    if line.startswith('Welcome'):
        return 'green'
    elif line.startswith('Successfully loaded "usb.ids" from cache.'):
        return 'green'
    elif line.startswith('Please be patient, loading device name database...'):
        return 'green'
    elif line.startswith('Type "help" for list of commands.'):
        return 'green'
    elif line.startswith('To start off, type "connect" to initiate a connection.'):
        return 'green'
    elif line.startswith('~~~~~~~~ Platform specific notes ~~~~~~~~'):
        return 'yellow'
    elif line.startswith('You have to run Thor as root or edit udev rules as follows:'):
        return 'yellow'
    elif line.startswith('1) create and open /etc/udev/rules.d/51-android.rules in an editor'):
        return 'yellow'
    elif line.startswith('2) enter SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666",'):
        return 'yellow'
    elif line.startswith('GROUP="YourUserGroupHere"'):
        return 'yellow'
    elif line.startswith('Additionally, you may have to disable the cdc_acm kernel module:'):
        return 'yellow'
    elif line.startswith('1) To temporarily unload, run "sudo modprobe -r cdc_acm"'):
        return 'yellow'
    elif line.startswith('2) To disable it, run "echo \'blacklist cdc_acm\' | sudo tee -a'):
        return 'yellow'
    elif line.startswith('/etc/modprobe.d/cdc_acm-blacklist.conf"'):
        return 'yellow'
    elif line.startswith('~~~~~~~^'):
        return 'red'
    elif line.startswith('No Samsung devices were found!'):
        return 'red'
    elif line.startswith('Not connected_to_device to a device!'):
        return 'red'
    else:
        return 'default_tag'

def update_output():
    while True:
        try:
            chunk = Thor.read_nonblocking(4096, timeout=0)
            if chunk:
                output_lines = chunk.splitlines()
                for line in output_lines:
                    cleaned_line = re.sub(r'\x1b\[[?0-9;]*[A-Za-z]', '', line).strip()
                    tag = determine_tag(cleaned_line)
                    Output_Text.configure(state='normal')
                    Output_Text.insert(tk.END, cleaned_line + '\n', tag)
                    Output_Text.configure(state='disabled')
                    Output_Text.see(tk.END)
                    if '/etc/modprobe.d/cdc_acm-blacklist.conf"' in cleaned_line:
                        running()
                    if 'Successfully connected to the device!' in cleaned_line:
                        connected_to_device('on')
                    if 'Successfully began an Odin session!' in cleaned_line:
                        odin_session_started()
        except pexpect.exceptions.TIMEOUT:
            pass
        except pexpect.EOF:
            pass

        # Delay between each update
        sleep(0.1)

def toggle_connection():
    global connect
    if currently_running:
        try:
            if connect == False:
                send_command('connect')
                sleep(0.5)
                print(Output_Text.get('end-2l linestart', 'end-2l lineend'))
                print(Output_Text.get('end-3l linestart', 'end-3l lineend'))
                if 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend') and 'Choose a device to connect to:' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
                    device()
                    set_widget_state(Connect_Button, text='Disconnect device', color='#F66151')
                    connect = True
                elif 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend') and 'No Samsung devices were found!' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
                    print('Couldn\'t find a Samsung device!')
            elif connect == True:
                send_command('disconnect')
                print('This works: 1')
                if Thor.expect(['Successfully disconnected the device!'], timeout=0.5) == 0:
                    print('This works: 2')
                    connected_to_device('off')
                    print('This works: 3')
                    Connect_Button.configure(text='Connect device', fg='#26A269')
                    print('This works: 4')
                    connect = False
                elif Thor.expect(['Not connected to a device!'], timeout=0.5) == 0:
                    print('Something needs worked on...')
        
        
        except pexpect.exceptions.TIMEOUT:
            # Handle timeout here
            print('A Timeout Occurred in toggle_connection')


def toggle_connection():
    global connect
    if currently_running:
        if connect == False:
            send_command('connect')
            window.after(200, check_connection)
        elif connect == True:
            send_command('disconnect')
            window.after(200, check_disconnection)

def check_connection():
    try:
        if 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend') and 'Choose a device to connect to:' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
            device()
            set_widget_state(Connect_Button, text='Disconnect device', color='#F66151')
            connect = True
        elif 'shell>' in Output_Text.get('end-2l linestart', 'end-2l lineend') and 'No Samsung devices were found!' in Output_Text.get('end-3l linestart', 'end-3l lineend'):
            print('Couldn\'t find a Samsung device!')
    except Exception as e:
        print(f"Error reading output: {e}")

def check_disconnection():
    try:
        if Thor.expect(['Successfully disconnected the device!'], timeout=0.5) == 0:
            connected_to_device('off')
            Connect_Button.configure(text='Connect device', fg='#26A269')
            connect = False
        elif Thor.expect(['Not connected to a device!'], timeout=0.5) == 0:
            print('Something needs worked on...')
    except Exception as e:
        print(f"Error reading output: {e}")


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
        print('Would have set the option "EFSClear" to true, but it is currently disabled')
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

def running():
    set_widget_state(Connect_Button, Send_Button, Command_Entry)

def connected_to_device(which_one):
    if which_one == 'on':
        Begin_Button.configure(state='normal')
    elif which_one == 'off':
        Begin_Button.configure(state='disabled')

def odin_session_started():
    set_widget_state(BL_Checkbox, AP_Checkbox, CP_Checkbox, CSC_Checkbox, USERDATA_Checkbox, BL_Button, AP_Button, CP_Button, CSC_Button, USERDATA_Button, BL_Entry, AP_Entry, CP_Entry, CSC_Entry, USERDATA_Entry, TFlash_Option, EFSClear_Option, BootloaderUpdate_Option, ResetFlashCount_Option, Apply_Options_Button)

def device():
    KEY_DOWN = '\x1b[B'
    Connect_Device_Box = tk.messagebox.askquestion("Question", "Do you want to connect to this device?", icon='question')
    try:
        if Connect_Device_Box == 'yes':
            Thor.expect('Cancel operation', timeout=0.5)
            Thor.send('\n')
        else:
            print('yes: 1')
            Thor.expect('Cancel operation', timeout=0.5)
            print('yes: 2')
            Thor.send(KEY_DOWN)
            Thor.send('\n')
            print('yes: 3')
            Thor.expect(['Cancelled by user'], timeout=0.5)
            
    except pexpect.exceptions.TIMEOUT:
            # Handle timeout here
            print('A Timeout Occured in device')

def open_file(type):
    # Open the file dialog and get the selected file
    file_path = filedialog.askopenfilename()
    # Check if a file was selected
    if file_path:
        # Update the entry widget with the file path
        if type == "BL":
            BL_Entry.delete(0, 'end')
            BL_Entry.insert(0, file_path)
            BL_Entry.icursor(tk.END)  # Move focus to the end of the line
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

def open_link(link):
    webbrowser.open(link)

def on_window_close():
    global Thor, output_thread, stop_threads
    if currently_running:
        if 'shell>' in Output_Text.get("1.0", tk.END):
            Thor.sendline('exit')
            stop_threads = True  # Set the flag to stop the threads
            Thor.terminate()
            Thor.wait()
            output_thread.join(timeout=1)  # Wait for the output thread to finish with a timeout
    window.destroy()

def on_button_hover(event, button):
    button.config(relief="flat", borderwidth=0, highlightbackground="#0479D7")

def on_button_leave(event, button):
    button.config(relief='flat', borderwidth=0, highlightbackground="#ACACAC")

def bind_button_events(button):
    button.bind("<Enter>", lambda event: on_button_hover(event, button))
    button.bind("<Leave>", lambda event: on_button_leave(event, button))

# Create the Tkinter window
window = tk.Tk()
window.title("Thor Flash Utility GUI - Version pre-alpha 1.0")

# Set the window size
window.geometry("985x600")

# Set the window color
window.configure(bg='#F0F0F0')

# Set the row and column widths
window.grid_rowconfigure(3, weight=1)
window.grid_rowconfigure(4, weight=1)
window.grid_rowconfigure(5, weight=1)
window.grid_rowconfigure(6, weight=1)
window.grid_rowconfigure(7, weight=1)
window.grid_columnconfigure(3, weight=1)

# Create and place the title label
Title_Label = tk.Label(window, text="Thor Flash Utility v1.0.4", font=("Monospace", 20), bg='#F0F0F0')
Title_Label.grid(row=0, column=0, columnspan=7, rowspan=2, sticky="nesw")

# Create the "Start Thor" button
Start_Button = tk.Button(window, text="Start Thor", command=start_thor, fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0, padx=57.5)
Start_Button.grid(row=0, column=8, sticky='we', pady=5, padx=5)

# Create the "Begin Odin" button
Begin_Button = tk.Button(window, text="Begin Odin Protocol", command=begin_odin, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Begin_Button.grid(row=0, column=10, sticky='we', pady=5, padx=5)

# Create the command entry
Command_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
Command_Entry.grid(row=1, column=8, columnspan=2, sticky='nesw', pady=5, padx=5)

# Create the "Send Command" button
Send_Button = tk.Button(window, text="Send Command to Thor", command=lambda: send_command(Command_Entry.get()), state='disabled', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Send_Button.grid(row=1, column=10, sticky='we', pady=5, padx=5)

# Create the "Connect" button
Connect_Button = tk.Button(window, text="Connect", command=toggle_connection, state='disabled', fg='#26A269', bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Connect_Button.grid(row=0,column=9, pady=5)

# Create the "BL" check-box
BL_Checkbox_var = tk.IntVar()
BL_Checkbox = tk.Checkbutton(window, variable=BL_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
BL_Checkbox.grid(row=3, column=7)

# Create the "AP" check-box
AP_Checkbox_var = tk.IntVar()
AP_Checkbox = tk.Checkbutton(window, variable=AP_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0')
AP_Checkbox.grid(row=4, column=7)

# Create the "CP" check-box
CP_Ckeckbox_var = tk.IntVar()
CP_Checkbox = tk.Checkbutton(window, variable=CP_Ckeckbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0')
CP_Checkbox.grid(row=5, column=7)

# Create the "CSC" check-box
CSC_Checkbox_var = tk.IntVar()
CSC_Checkbox = tk.Checkbutton(window, variable=CSC_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
CSC_Checkbox.grid(row=6, column=7)

# Create the "USERDATA" check-box
USERDATA_Checkbox_var = tk.IntVar()
USERDATA_Checkbox = tk.Checkbutton(window, variable=USERDATA_Checkbox_var, state='disabled', bg='#F0F0F0', highlightbackground='#F0F0F0', relief='flat')
USERDATA_Checkbox.grid(row=7, column=7)

# Create the "BL" button
BL_Button = tk.Button(window, text="Bl", pady="5", state='disabled', command=lambda: open_file('BL'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
BL_Button.grid(row=3, column=8, sticky='ew', padx='4')
bind_button_events(BL_Button)

# Create the "AP" button
AP_Button = tk.Button(window, text="AP", pady="5", state='disabled', command=lambda: open_file('AP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
AP_Button.grid(row=4, column=8, sticky='ew', padx='4')
bind_button_events(AP_Button)

# Create the "CP" button
CP_Button = tk.Button(window, text="CP", pady="5", state='disabled', command=lambda: open_file('CP'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CP_Button.grid(row=5, column=8, sticky='ew', padx='4')
bind_button_events(CP_Button)

# Create the "CSC" button
CSC_Button = tk.Button(window, text="CSC", pady="5", state='disabled', command=lambda: open_file('CSC'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
CSC_Button.grid(row=6, column=8, sticky='ew', padx='4')
bind_button_events(CSC_Button)

# Create the "USERDATA" button
USERDATA_Button = tk.Button(window, text="USERDATA", pady=5, state='disabled', command=lambda: open_file('USERDATA'), bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
USERDATA_Button.grid(row=7, column=8, sticky='ew', padx='4')
bind_button_events(USERDATA_Button)

# Create the "BL" entry
BL_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
BL_Entry.grid(row=3, column=9, columnspan=2, sticky='we', padx=5)

# Create the "AP" entry
AP_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
AP_Entry.grid(row=4, column=9, columnspan=2, sticky='we', padx=5)

# Create the "CP" entry
CP_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
CP_Entry.grid(row=5, column=9, columnspan=2, sticky='we', padx=5)

# Create the "CSC" entry
CSC_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
CSC_Entry.grid(row=6, column=9, columnspan=2, sticky='we', padx=5)

# Create the "USERDATA" entry
USERDATA_Entry = tk.Entry(window, state='disabled', bg='#F0F0F0', relief='flat', highlightbackground='#7A7A7A')
USERDATA_Entry.grid(row=7, column=9, columnspan=2, sticky='we', padx=5)

# Create the "Log" button
Log_Button = tk.Button(window, text='Log', command=toggle_log, bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Log_Button.grid(row=2, column=0, sticky='wes', pady=5, padx=5)

# Create the "Options" button
Options_Button = tk.Button(window, text='Options', command=toggle_options, bg='#E1E1E1', highlightbackground='#ACACAC', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Options_Button.grid(row=2, column=1, sticky='wes', pady=5)

# Create the "Pit" button
Pit_Button = tk.Button(window, text='Pit', command=toggle_pit, bg='#E1E1E1', highlightbackground='#ACACAC', highlightcolor='#E4F1FB', activebackground='#E4F1FB', relief='flat', borderwidth=0)
Pit_Button.grid(row=2, column=2, sticky='wes', pady=5, padx=5)

# Create the "Options" frame and check-boxes
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

# Create the "Pit" frame
Pit_Frame = tk.Frame(window, bg='white')
Pit_Frame.grid(row=3, rowspan=5, column=0, columnspan=7, sticky='nesw', padx=5)

Test_Label = tk.Label(Pit_Frame, text='Just a test :)')
Test_Label.grid(row=0, column=0, padx=10, pady=5)

# Create the "Log" frame
Log_Frame = tk.Frame(window, bg='white')
Log_Frame.grid(row=3, rowspan=5, column=0, columnspan=7, sticky='nesw', padx=5)
Log_Frame.grid_columnconfigure(0, weight=1)
Log_Frame.grid_rowconfigure(0, weight=1)

Output_Text = scrolledtext.ScrolledText(Log_Frame, state="disabled", highlightthickness=0, font=("Monospace", 9))
Output_Text.grid(row=0, column=0, rowspan=6, sticky='nesw')

# Configure the tags for coloring the text
Output_Text.tag_configure('green', foreground='#26A269')
Output_Text.tag_configure('yellow', foreground='#E9AD0C')
Output_Text.tag_configure('red', foreground='#F66151')

# Raise the "Log" frame to top on start-up
toggle_log()

# TESTING
#odin_session_started()

# Bind the on_window_close function to the window's close event
window.protocol("WM_DELETE_WINDOW", on_window_close)

# Run the Tkinter event loop
window.mainloop()
