
# Thor GUI

A GUI for the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).
![Thor_GUI](https://github.com/ethical-haquer/Thor_GUI/assets/141518185/4fa0e2e6-da03-49fe-be44-af1bba96344f)
<details>
  <summary>Screenshots</summary>
  <br>
  <b>NOTE:</b> This section is a work-in-progress
  <br>
  <br>
  "Options" Tab:
  <br>
  <img src="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/8d2625f9-780a-4f83-b9e5-db90d691295e" alt="Options Tab">
  <br>
  Command Entry:
  <br>
  <img src="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/6292ec8e-7ffc-4036-a000-2ec178e9314b" alt="Command Entry">
  <br>
  "Select Partitions" Window:
  <br>
  <img src="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/57fe8e2e-6ebf-44b6-b223-9eb4e221a35f" alt="Select Partitions Window">
  <br>
  "Verify Flash" Window:
  <br>
  <img src="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/1b6bb3a9-38d8-4f47-aedf-310f7a88ca34" alt="Verify Flash Window">
</details>

## Intro

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Thor's CLI, I decided to try and make a GUI for it. If you aren't comfortable with the command line, or just prefer a GUI, then this could be helpful for you. On the other hand, if you are comfortable using the command line, then you may just want to use Thor in the terminal. And yes, this is my first GitHub project, so please let me know if you have any suggestions. :slightly_smiling_face:

## Disclaimer

Currently, Thor GUI is in an Alpha stage. Not all of Thor's features have been implemented in the GUI, and there are known (and probably unknown) bugs. A list of missing features and know bugs in the _latest release_ can be found below.

## Known Bugs

In addition to [Thor's own issues](https://github.com/Samsung-Loki/Thor/issues), here are Thor GUI's:

Functional:
+ Currently, the only interactive Thor commands (the ones that require user input, such as "flashFile") that can be used are "connect" and "flashTar". This doesn't affect non-interactive Thor commands that don't require input, such as "help", "begin odin", etc.

Aesthetic:
+ The output from interactive commands (ones that require user input, such as flashTar, connect, etc.) is echoed. So if Thor outputs interactive text, it will be displayed two times. Also, when Thor GUI sends Thor keypresses to select things and such, Thor will send the new output, also echoed. Like when a "[ ]" changes to a "[X]", that whole section of output will be displayed again.

## Implemented Thor features

- [x] Connecting/Disconnecting devices
- [x] Starting/Stopping an Odin session
- [x] Setting options
- [x] Typing and sending Thor a command
- [x] Flashing Odin archives
- [ ] Flashing a single partition
- [ ] Printing a description of a device's partition table
- [ ] Dumping a device's partition table into a PIT file
- [ ] Printing a description of any PIT file

## Planned improvements

+ Built in installer and setup for .NET and Thor.
+ Different themes: dark, light, etc. (With the current look as a "Windows" theme)

## Prerequisites

### Thor

+ Install the .NET 7 Runtime. Instructions to do so can be found [here](https://learn.microsoft.com/en-us/dotnet/core/install/) (under the "Linux" section).
> [!NOTE]
> The .NET Framework is propreitary.
+ Install Thor. Download the "Linux.zip" file from [here](https://github.com/Samsung-Loki/Thor/releases/tag/1.0.4).
+ Next, unzip the "Linux.zip" file somewhere, and run:

  ```
  PATH/TO/TheAirBlow.Thor.Shell
  ```
+ If Thor runs, you're ready to move on!

### Pexpect

```
pip3 install pexpect
```

## Install Instructions

+ Download the latest Thor GUI release from [here](https://github.com/ethical-haquer/Thor_GUI/releases).
+ Once it's downloaded, extract it, and open the Thor_GUI.py file with a text editor.
+ You need to edit line 39 of the file.
+ Replace "PATH/TO/TheAirBlow.Thor.Shell.dll" with the correct path to the .dll file (The one from the "Linux.zip").
+ Save your changes to the file, and run:

  ```
  python3 PATH/TO/Thor_GUI.py
  ```
+ If a sweet-looking GUI shows up, then you've finished installing Thor GUI!

> [!NOTE]
> If you encounter any issues, or have any questions, just let me know and I'll be glad to help. 🙂

## Usage
**NOTE:** This section is a work-in-progress
<details>
  <summary>Guide</summary>
  <br>
  <b>Starting Thor:</b>
  <br>
  To start Thor, click the "Start Thor" button. This is usually the first thing you'd do after running Thor GUI.
  <br>
  <br>
  <b>Connecting to a device:</b> 
  <br>
  To connect to a device, click the "Connect" button. A pop-up window will appear, asking you what device you'd like to connect to. Choose a device, and then click "Select".
  <br>
  <br>
  <b>Running a <a href="https://github.com/Samsung-Loki/Thor#current-list-of-commands">Thor command</a>:</b> 
  <br>
  To send Thor a command, enter it into the Command Entry (upper-right corner of Thor GUI, under the "Start Thor" button) and hit Enter.
  <br>
  <br>
  <b>Starting an Odin protocol</b> 
  <br>
  To start an Odin protocol, click the "Begin Odin Protocol" button.
  <br>
  <br>
  <b>Flashing Odin archives</b> 
  <br>
  To flash Odin archives, first select what files to flash. You may either select the files with a file picker, by clicking one of the file buttons (For example, to select a BL file, click the "BL" button), or type the file path into the corresponding entry. Only files which are selected with the check-boxes will be flashed. To flash the selected files, hit the "Start" button. There are a few requirements that must be met for it to start the flash: At least one file must be selected (with the check-boxes), All selected files must exist, All selected files must be a .tar, .md5, or .zip, and All selected files must be in the same directory. If any of these conditions is not met, Thor GUI will simply let you know, so don't worry.
  
</details>

## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Find and report bugs. If you find an issue that isn't listed above in "Known Bugs", please let me know!
+ Improve the code. Pull requests are always welcome!

## Credits

[TheAirBlow](https://github.com/theairblow) for Thor Flash Utility

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Thor GUI

## This program is licenced under

[GNU General Public License v3.0](https://github.com/ethical-haquer/Thor_GUI/blob/main/LICENSE)

