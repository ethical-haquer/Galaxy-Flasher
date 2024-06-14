
# Galaxy Flasher

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Github Releases](https://img.shields.io/github/downloads/ethical-haquer/Galaxy-Flasher/total.svg?style=flat)](https://github.com/ethical-haquer/Galaxy-Flasher/releases)

A GUI for Samsung Flash Tools.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/9402d060-bf1c-4b0b-b901-558006272952">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/9402d060-bf1c-4b0b-b901-558006272952">
  <img alt="Screenshot of Thor GUI">
</picture>
<details>
  <summary><b>Screenshots</b></summary>
  <br>
  <b>NOTE:</b> These screenshots may not be up-to-date. I really need to automate creating them...
  <br>
  <br>
  Options Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/621b8ecf-c748-499d-8f4c-a8f612f293a2">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/dad26804-0c18-41e5-86a9-2dacd107f18f">
    <img alt="Options Tab">
  </picture>
  <br>
  Pit Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/50cda73e-fa59-41f1-a205-3c49f93289dd">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/4f5bdf5e-7ecd-43dc-af92-126d442820d0">
    <img alt="Pit Tab">
  </picture>
  <br>
  Settings Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/d574eb2b-c592-4d74-951b-d3effcd9e345">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/8a1a3712-394f-4d9c-b84e-b2eaa151a5f7">
    <img alt="Settings Tab">
  </picture>
  <br>
  About Dialog:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/6b479807-9206-41aa-b15a-874867a51825">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/d16c0e4d-65a7-46f8-b976-b34b7c57a116">
    <img alt="About Tab">
  </picture>
  <br>
  "Select Partitions" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/620d05e8-872e-44d7-946e-fca7bf80e311">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/83a61e3c-09d7-41a5-8178-124abc6fc623">
    <img alt="Select Partitions Window">
  </picture>
  <br>
  "Verify Flash" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/7d3d6e6c-af3c-48eb-bd31-263741b3f5b7">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Thor_GUI/assets/141518185/48a7da84-1474-4d09-9b9d-ae2a74d02100">
    <img alt="Verify Flash Window">
  </picture>
</details>

## Intro

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Odin4's CLI, I decided to try and make a GUI for the Thor Flash Utility. If you aren't comfortable with the command line, or just prefer a GUI, then this could be helpful for you. On the other hand, if you are comfortable using the command line, then you may just want to use Thor in the terminal. And yes, this is my first GitHub project, so please let me know if you have any suggestions. :slightly_smiling_face:

## Disclaimer

Currently, Galaxy Flasher is in an Alpha stage. Not all of Thor's features have been implemented in the GUI, and there are known (and possibly unknown) bugs. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs

In addition to [Thor's own issues](https://github.com/Samsung-Loki/Thor/issues), here are Galaxy Flasher's:


## Supported platforms

- [x] Linux (x64 and arm64)
- [ ] Windows
- [ ] macOS

## Prerequisites

### Python

If you're on Linux, you probably already have Python installed. Look [here](https://wiki.python.org/moin/BeginnersGuide/Download) if you don't.

### Tkinter

You probably already have Tkinter installed, but if you get "ModuleNotFoundError: No module named 'tkinter'", do this:

Debian-based distros:

```
sudo apt-get install python3-tk
```

Fedora:

```
sudo dnf install python3-tkinter
```

### These Python packages:

- pexpect
- sv-ttk
- tkinter-tooltip
- tkinterdnd2-universal
- zenipy

#### To install all of them:

```
pip install pexpect sv-ttk tkinter-tooltip tkinterdnd2-universal zenipy
```

## Installation

+ First, make sure you have the [above prerequisites](https://github.com/ethical-haquer/Thor_GUI?tab=readme-ov-file#prerequisites).
+ Download the latest "thor-gui_os_version.zip" file from [here](https://github.com/ethical-haquer/Thor_GUI/releases).
+ Once it's downloaded, extract it.
+ Then run:

  ```
  python3 PATH/TO/thor-gui.py
  ```
+ If a sweet-looking GUI shows up, then you've finished installing Thor GUI!

> [!NOTE]
> If you encounter any issues, or have any questions, just let me know and I'll be glad to help. 🙂

## Usage

**NOTE:** This screen-recording is not up-to-date. I really need to automate creating it...

https://github.com/ethical-haquer/Thor_GUI/assets/141518185/5df866bb-74d1-40ba-b5b0-571ed88d68a3

<details>
  <summary><b>Guide</b></summary>
  <br>
  <b>Starting Thor (0:00):</b>
  <br>
  To start Thor, click the "Start Thor" button. This is usually the first thing you'd do after running Thor GUI.
  <br>
  <br>
  <b>Connecting to a device (0:09):</b> 
  <br>
  To connect to a device, click the "Connect" button. A pop-up window will appear, asking you what device you'd like to connect to. Choose a device, and then click "Select".
  <br>
  <br>
  <b>Starting an Odin protocol (0:17):</b>
  <br>
  To start an Odin protocol, which is needed to flash a device, click the "Start Odin protocol" button. 
  <br>
  <b>Fun fact:</b> The top three buttons in Thor GUI are placed in the order they should be used, from left to right.
  <br>
  <br>
  <b>Flashing Odin archives (0:19)</b> 
  <br>
  To flash Odin archives, first select what files to flash. You may either select the files with a file picker, by clicking one of the file buttons (For example, to select a BL file, click the "BL" button), or type the file path into the corresponding entry. Only files which are selected with the check-boxes will be flashed. 
  <br>
  <br>
  To flash the selected files, hit the "Start" button. There are a few requirements that must be met for it to start the flash: 
  <br>
  At least one file must be selected (with the check-boxes), 
  <br>
  All selected files must exist, 
  <br>
  All selected files must be a .tar, .md5, or .zip, 
  <br>
  All selected files must be in the same directory. 
  <br>
  <br>
  If any of these above conditions is not met, Thor GUI will simply let you know, so don't worry.
  <br>
  <br>
  After a flash has been started, you will be presented with a "Select Partitions" Window. You may click "Select All" to select all of the listed partitions, or choose certain partitions to flash. Once you have finished selecting the partitions you want to flash, hit the "Select" button. There will be a "Select Partitions" Window for <b>every file</b> you selected with the check-boxes.
  <br>
  <br>
  After you have finished selecting partitions to flash you will see a "Verify Flash" window. This is your chance to cancel the flash if needed, by clicking the "No" button. Otherwise, click the "Yes" button and the flash will start.
  <br>
  <br>
  <b>Running a <a href="https://github.com/Samsung-Loki/Thor#current-list-of-commands">Thor command</a> (1:12):</b> 
  <br>
  To send Thor a command, enter it into the Command Entry (upper-right corner of Thor GUI, under the "Start Thor" button) and hit Enter. (the key on the keyboard, not the button on Thor GUI)
</details>

## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Find and report bugs. If you find an issue that isn't listed above in "Known Bugs", please let me know!
+ Help translate Thor GUI into your language. Refer to [this readme](https://github.com/ethical-haquer/Thor_GUI/blob/main/locales/README.md) for more info.
+ Improve the code. Pull requests are always welcome!
+ Suggest an improvement by opening up a [feature request](https://github.com/ethical-haquer/Thor_GUI/issues/new/choose)!

## Credits

[TheAirBlow](https://github.com/theairblow) for the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor)

[rdbende](https://github.com/rdbende) for the [Sun Valley tkk theme](https://github.com/rdbende/Sun-Valley-ttk-theme)

[Not_Rich@XDA](https://xdaforums.com/m/not_rich.8463826/) for continuing to test out new versions and suggest improvements.

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Thor GUI

## License

Thor GUI is licensed under GPLv3. Please see [`LICENSE`](./LICENSE) for the full license text.
