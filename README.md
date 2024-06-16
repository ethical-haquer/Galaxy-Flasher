
# Galaxy Flasher

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Github Releases](https://img.shields.io/github/downloads/ethical-haquer/Galaxy-Flasher/total.svg?style=flat)](https://github.com/ethical-haquer/Galaxy-Flasher/releases)

A GUI for Samsung Flash Tools.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/cdfc298d-fb85-4c01-924c-5971a6e380cb">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/f157cbad-d09c-40ae-a68d-91512d52211a">
  <img alt="Screenshot of Thor GUI">
</picture>
<details>
  <summary><b>Screenshots</b></summary>
  <br>
  Options Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/621b8ecf-c748-499d-8f4c-a8f612f293a2">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/dc08a6bf-2e10-47b0-b7c5-d0ae7a11d695">
    <img alt="Options Tab">
  </picture>
  <br>
  Pit Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/50cda73e-fa59-41f1-a205-3c49f93289dd">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/88fee46a-ed65-4c38-87ba-6695b6e5ae34">
    <img alt="Pit Tab">
  </picture>
  <br>
  Settings Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/d574eb2b-c592-4d74-951b-d3effcd9e345">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/58f92b1a-0390-4620-995b-06104a7eda71">
    <img alt="Settings Tab">
  </picture>
  <br>
  About Dialog:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/6b479807-9206-41aa-b15a-874867a51825">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/3bfe072f-6cfc-4e5e-8512-0e1561b2834a">
    <img alt="About Tab">
  </picture>
  <br>
  "Select Partitions" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/dc7cea25-1819-4ccd-b119-dd45ca7fab61">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/a46b1f00-34da-4e26-a16d-bc7c8223cea1">
    <img alt="Select Partitions Window">
  </picture>
  <br>
  "Verify Flash" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/ead15566-0efa-4e95-a834-01d3ab01c2dd">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/1486223e-254f-4ffd-a3bf-9bfdb7d8a74e">
    <img alt="Verify Flash Window">
  </picture>
</details>

## Background

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Odin4's CLI, I decided to make a GUI for Thor: Thor GUI. With the release of v0.5.0, Thor GUI was renamed Galaxy Flasher, and it supports Thor and Odin4.

## Disclaimer

Currently, Galaxy Flasher is in an Alpha stage. There are known (and possibly unknown) bugs. Also, it was just completely re-written, so the readme is still in the process of getting updated. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs

## Supported platforms

- [x] Linux x64
- [ ] Linux arm64 (WIP, only Thor can be used, untested)
- [ ] Windows
- [ ] macOS

## Installing

There are currently two ways to install/use Galaxy FLasher:

- As a Flatpak.
- As a .py file.

The [first way](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#as-a-flatpak) is recomended because it supports a wider range of distros. The [second way](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#as-a-py-file-currently-not-complete) is really only better if you plan on contributing to the code. Below are the steps for each method.

> [!NOTE]
> If you encounter _any_ issues, or have _any_ questions, just let me know and I'll be glad to help. 🙂

> [!NOTE]
> These guides are still not fully tested. If you find any issues, __please let me know__! Thanks.

### As a Flatpak

#### Flatpak Prerequisites

- flatpak - Go [here](https://www.flatpak.org/setup/), select your distro, and follow the directions to install flatpak.
- flatpak-builder - "...[flatpak-builder] is usually available from the same repository as the flatpak package (e.g. use apt or dnf). You can also install it as a flatpak with `flatpak install flathub org.flatpak.Builder`". (quote from [here](https://docs.flatpak.org/en/latest/first-build.html))

#### Flatpak Installation

1. First of all, make sure you have the [above prerequisites](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#flatpak-prerequisites).
2. Download the latest "galaxy-flasher-version-os.zip" file from [the Releases page](https://github.com/ethical-haquer/Galaxy-Flasher/releases). It is a good idea to make a new directory and save the file there, to keep it more contained.
3. Once the file is downloaded, extract it.
4. Move into the newly extracted directory. It should be named the same as the file, minus the ".zip" part.
5. Move into the "flatpak" directory.
6. Run the command `./build.sh` in the terminal. You must be located in the same "flatpak" directory in the terminal when you run it. If you don't know how to change directories in the terminal, look at [this guide](https://itsfoss.com/change-directories/).
7. If the command finishes with a lot of output, and you get no errors, then go to step 13. If you instead get "Failed to init: Unable to find sdk org.gnome.Sdk version 46", then continue following the steps below.
8. Run "flatpak install org.gnome.Sdk" in the terminal. You should get a list of different versions to choose from.
9. Select version 46.
10. If what you see looks correct, type "y" and hit enter. Once it says "Changes complete.", continue.
11. Run the `./build.sh` command again, from the "flatpak" directory.
12. Once again, if the command finishes with a lot of output, and you get no errors, then go to step 13. If you instead get errors, __please let me know__ so I can update this guide. Thanks!
13. You've finished installing Galaxy Flasher, congratulations!

### As a .py file (currently not complete)

#### Prerequisites (currently not complete)

- python3-gi
- libvte-2.91-gtk4-0 >= 0.72
- gir1.2-vte-3.91 >= 0.72

#### Installation

1. First of all, make sure you have the [above prerequisites](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#prerequisites-currently-not-complete). You may notice, they are incomplete,
2. Download the latest "galaxy-flasher-version-os.zip" file from [the Releases page](https://github.com/ethical-haquer/Galaxy-Flasher/releases). It is a good idea to make a new directory and save the file there, to keep it more contained.
3. Once the file is downloaded, extract it.
4. Move into the newly extracted directory. It should be named the same as the file, minus the ".zip" part.
5. Run `python3 galaxy-flasher.py`.
6. If Galaxy Flasher starts up, then you're done. Congratulations! If you instead get errors, __please let me know__ so I can update the guide. Thanks!

## Usage

[Galaxy-Flasher-Thor-Screencast-Dark.webm](https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/bc8c07d5-17ea-447a-b4b2-98aa295cc3e6)

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
