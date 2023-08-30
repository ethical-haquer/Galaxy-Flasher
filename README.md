# NOTICE: This is not the main branch, and is under construction

# Thor GUI

A GUI for the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).
![Thor_GUI_Alpha_v0 2 0](https://github.com/ethical-haquer/Thor_GUI/assets/141518185/a938faf7-5fc9-48e4-9981-178e78e6cd6d)

## Intro

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Thor's CLI, I decided to try and make a GUI for it. If you aren't comfortable with the command line, or just prefer a GUI, then this could be helpful for you. On the other hand, if you are comfortable using the command line, then you may just want to use Thor in the terminal. And yes, this is my first GitHub project, so please let me know if you have any suggestions. :slightly_smiling_face:

## Disclaimer

Currently, Thor GUI is in an Alpha stage. Not all of Thor's features have been implemented in the GUI, and there are known (and probably unknown) bugs. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs

Functional:
+ Setting the option "T Flash" to "True" locks-up Thor itself, at least in my case. I didn't have a micro-SD in, but still. Causes Ctrl+C to be necessary to stop Thor GUI.
+ Many interactive Thor commands that require user input, such as "flashTar", cannot be used. Currently the only one of these commands that works (mostly, see below issue) is "connect". This doesn't affect non-interactive Thor commands that don't require input, such as "help", "begin odin", etc.
+ While running "connect" (ethier with the connect button, or manually) works, you will only be able to connect to the first device listed; and if there are multiple devices connected, clicking "No" will connect to the second device listed instead of canceling.

Aesthetic:
+ Sometimes the first line of output shown in "Log" is a blank line.
+ Odin archive button rims change color when hovered-over, even when they are disabled. They should remain greyed-out completely.
+ The output from interactive commands (ones that require user input, such as flashTar, connect, etc.) is echoed. So if Thor outputs interactive text, it will be displayed two times. Also, when Thor GUI sends Thor keypresses to select things and such, Thor will send the new output, also echoed. Like when a "[]" changes to a "[X]", the whole section of output will be displayed again.

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

## Planned improvements

+ Built in installer and setup for .NET and Thor.
+ Different themes: dark, light, etc. (With the current look as a "Windows" theme)

## Prerequisites

### Thor

+ Install the .NET 7 Runtime. Instructions to do so can be found [here](https://learn.microsoft.com/en-us/dotnet/core/install/) (under the "Linux" section).
> [!NOTE]
> The .NET Framework is propreitary, but Thor depends on it.
+ Install Thor. Go [here](https://github.com/Samsung-Loki/Thor/releases) and download the latest "Linux.zip".
+ Next, unzip the "Linux.zip" file somewhere, and run:

  ```
  PATH/TO/TheAirBlow.Thor.Shell
  ```
+ If Thor runs, you're ready to move on!


Instructions to install the .NET Runtime can be found [here](https://learn.microsoft.com/en-us/dotnet/core/install/) (under the "Linux" section).

### Pexpect

```
pip3 install pexpect
```

## Install Instructions

+ Download the latest Thor GUI release from [here](https://github.com/ethical-haquer/Thor_GUI/releases).
+ Once it's downloaded, extract it, and open the Thor_GUI.py file with a text editor.
+ You need to edit line 62 of the file.
+ Replace "PATH/TO/TheAirBlow.Thor.Shell.dll" with the correct path to the .dll file (The one from the "Linux.zip").
+ Save your changes to the file, and run:

  ```
  python3 PATH/TO/Thor_GUI.py
  ```
+ If a sweet-looking GUI shows up, then you've finished installing Thor GUI!

> [!NOTE]
> If you encounter any issues, or have any questions, just let me know and I'll be glad to help. 🙂

## Usage

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
  <b>Starting an Odin protocol</b> 
</details>

## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Find bugs. If you find an issue that isn't listed above in "Known Bugs", please let me know!
+ Improve the code. Pull requests are always welcome!

## Credits

[TheAirBlow](https://github.com/theairblow) for Thor Flash Utility

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Thor GUI

## This program is licenced under

[GNU General Public License v3.0](https://github.com/ethical-haquer/Thor_GUI/blob/main/LICENSE)

