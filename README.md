# Thor GUI
A GUI for the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).
![A screenshot of Thor GUI](https://github.com/ethical-haquer/Thor_GUI/assets/141518185/cfc1490e-91be-40b2-bb17-5b767a41dacc)

## Intro
After witnessing a new Linux user, who had just switched over from Windows, struggle with using Thor's CLI, I decided to try and make a GUI for it. If you aren't comfortable with the command line, or just prefer a GUI, then this could be helpful for you. On the other hand, if you are comfortable using the command line, then you may just want to use Thor in the terminal.

## Disclaimer
Currently, the latest release of Thor GUI is in an Alpha stage. Not all of Thor's features have been implemented in the GUI, and there are some known (and probably unknown) bugs. A list of missing features and know bugs can be found below.

## Known Bugs (In latest release)


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
+ Then download the latest ".py" file from [here]().
+ Once it's downloaded, open it with a text editor.
+ You need to edit line NUMBER of the file.
+ Replace "PATH/TO/TheAirBlow.Thor.Shell.dll" with the correct path to the .dll file (The one from "Linux.zip").
+ Save your changes to the file, and run:
  ```
  python3 PATH/TO/Thor_GUI_Alpha.py
  ```
+ If you see a sweet GUI pop up, then you've finished installing Thor GUI!

## Usage
This program was designed to be as similiar to Odin as possible. The first thing you should do is click the "Start Thor" button. This will start Thor, and begin displaying Thor's output in the "Log" tab. Notice how this enables more buttons to be used. You can enter a [valid Thor command](https://github.com/Samsung-Loki/Thor#current-list-of-commands), perhaps "help", in the entry next to the "Send Command" button. Then click "Send Command". You should see "help" displayed under the "shell>" prompt, and the output from "help" should be displayed. To connect your device, have it plugged in, while in download mode, and click "Connect". A pop-up window should appear, asking you if you'd like to connect to the device. Clicking "yes" will connect your device and enable more buttons.

## How you can help
Here are some ways you can help me improve Thor GUI:
+ Send me Thor's output after flashing an Odin archive(s). This is actually very helpful, because in order to implement Odin archive flashing in Thor GUI, I need to know what Thor's expected output is. Since I only have one Samsung device, and don't need to flash it at the moment, I can't do this myself.
+ If you find an issue that isn't listed above in "Known Bugs", please let me know!
+ Improve the code. Pull-requests are always welcome!

## Credits
[TheAirBlow](https://github.com/theairblow) for Thor Flash Utility

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Thor GUI

