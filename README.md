# Thor GUI
A GUI for the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).
![Thor_GUI](https://github.com/ethical-haquer/Thor_GUI/assets/141518185/bf4e2fb2-ada4-45f1-a192-109e6deb1b92)


## Intro
After witnessing a new Linux user, who had just switched over from Windows, struggle with using Thor's CLI, I decided to try and make a GUI for it. If you aren't comfortable with the command line, or just prefer a GUI, then this could be helpful for you. On the other hand, if you are comfortable using the command line, then you may just want to use Thor in the terminal. And yes, this is my first GitHub project, so please let me know if you have any suggestions. :slightly_smiling_face:

## Disclaimer
Currently, Thor GUI is in an Alpha stage. Not all of Thor's features have been implemented in the GUI, and there are some known (and probably unknown) bugs. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs
+ Some lines of output text are not colored. For example 'Successfully began an Odin session!'.
+ The 'Begin Odin protocol' button does not change after a session is running. Should read: 'End Odin protocol' and send command "end", when session is already running.
+ Setting the option "T Flash" to true locks-up Thor itself, at least in my case. I didn't have a micro-SD in, but still. Causes Ctrl+C to be necessary to stop Thor GUI.
+ Sometimes the first line of output is a blank line.

## Implemented Thor features
- [x] Connecting/Disconnecting devices
- [x] Starting/Stopping an Odin session
- [x] Setting options
- [x] Typing and sending Thor a command
- [ ] Flashing Odin archives
- [ ] Flashing a single partition
- [ ] Printing a description of a device's partition table
- [ ] Dumping a device's partition table into a PIT file
- [ ] Printing a description of any PIT file

## Install Instructions
First, Thor has to be installed (If it isn't already). Here is how:
+ Install the .NET 7 Runtime. Instructions to do so can be found [here](https://learn.microsoft.com/en-us/dotnet/core/install/) (under the "Linux" section).
+ Install Thor. Go [here](https://github.com/Samsung-Loki/Thor/releases) and download the latest "Linux.zip".
+ Next, unzip the "Linux.zip" file somewhere, and run:
  ```
  PATH/TO/TheAirBlow.Thor.Shell
  ```
+ If Thor runs, you're ready to move on!

Now we can install Thor GUI:
+ First run:
  ```
  pip3 install pexpect
  ```
+ This will install pexpect, which Thor GUI uses.
+ Then download the latest Thor GUI release from [here](https://github.com/ethical-haquer/Thor_GUI/releases).
+ Once it's downloaded, extract it, and open the Thor_GUI.py file with a text editor.
+ You need to edit line 43 of the file.
+ Replace "PATH/TO/TheAirBlow.Thor.Shell.dll" with the correct path to the .dll file (The one from "Linux.zip").
+ Save your changes to the file, and run:
  ```
  python3 PATH/TO/Thor_GUI.py
  ```
+ If a sweet-looking GUI shows up, then you've finished installing Thor GUI!

**NOTE:** If you encounter any issues, or have any questions, just let me know and I'll be glad to help. 🙂

## Usage
This program was designed to be as similiar to Odin as possible. The first thing you should do is click the "Start Thor" button. This will start Thor, and begin displaying Thor's output in the "Log" tab. Notice how this enables more buttons to be used. You can enter a [valid Thor command](https://github.com/Samsung-Loki/Thor#current-list-of-commands), perhaps "help", in the entry next to the "Send Command" button. Then click "Send Command". You should see the output from "help" displayed. To connect your device, have it plugged in, while in download mode, and click "Connect". A pop-up window should appear, asking you if you'd like to connect to the device. Clicking "yes" will connect your device and enable more buttons. Closing the window will handle shutting everthing down.

## How you can help
Here are some ways you can help me improve/finish Thor GUI:
+ Send me Thor's output after flashing an Odin archive(s). This is actually _very_ helpful, because in order to implement Odin archive flashing in Thor GUI, I need to know what Thor's expected output is. Since I only have one Samsung device, and don't need to flash it at the moment, I can't do this myself.
+ Find bugs. If you find an issue that isn't listed above in "Known Bugs", please let me know!
+ Improve the code. Pull-requests are always welcome!

## Credits
[TheAirBlow](https://github.com/theairblow) for Thor Flash Utility

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Thor GUI

## This program is licenced under
[GNU General Public License v3.0](https://github.com/ethical-haquer/Thor_GUI/blob/main/LICENSE)

