
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

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Odin4's CLI, I decided to make a GUI for Thor: Thor GUI. With the release of v0.5.0, Thor GUI was renamed Galaxy Flasher, and it now supports Thor and Odin4.

## Disclaimer

Currently, Galaxy Flasher is in an Alpha stage. There are known (and probably unknown) bugs. Also, it was just completely re-written, so the readme is still in the process of getting updated. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs

Thinking of any...

## Supported platforms

- [x] Linux x64
- [ ] Linux arm64 (WIP, only Thor can be used, untested)
- [ ] Windows
- [ ] macOS

## Supported flash-tools

- Thor
- Odin4
- PyThor (in development)

## Installing

There are currently two ways to install/use Galaxy Flasher:

- As a Flatpak.
- As a .py file.

The [first way](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#as-a-flatpak) is recommended because it supports a wider range of distros. The [second way](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#as-a-py-file-currently-not-complete) is really only better if you plan on contributing to the code. Below are the steps for each method.

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

#### Prerequisites

- python3-gi
- libvte-2.91-gtk4-0 >= 0.72
- gir1.2-vte-3.91 >= 0.72

#### Installation

1. First of all, make sure you have the [above prerequisites](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#prerequisites). You may notice, they __are incomplete__, so expect to have to install other stuff. __Please let me know__ what else you had to install, if you had to install other stuff. Thanks!
2. Download the latest "galaxy-flasher-version-os.zip" file from [the Releases page](https://github.com/ethical-haquer/Galaxy-Flasher/releases). It is a good idea to make a new directory and save the file there, to keep it more contained.
3. Once the file is downloaded, extract it.
4. Move into the newly extracted directory. It should be named the same as the file, minus the ".zip" part.
5. Run `python3 galaxy-flasher.py`.
6. If Galaxy Flasher starts up, then you're done. Congratulations! If you instead get errors, __please let me know__ so I can update the guide. Thanks!

## Usage

Galaxy Flasher's layout is similar to Odin. In the upper-right there are four buttons: "Log", "Options", "Pit", and "Settings". Clicking these buttons will change what "tab" you are viewing. All four tabs are described [here](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#tabs). On the right side you will see five rows that each have a button and an entry. That is where you can [select files](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#selecting-files). For how to flash files, [look here](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#flashing-files).

### Tabs

  <p>
  <details>
  <summary><b>Log Tab</b></summary>
  The Log Tab displays the output from the flash-tool.
  <br>
  You are also able to enter flash-tool commands into the Log Tab, just as you would in the terminal.
  </details>
  </p>
  
  <p>
  <details>
  <summary><b>Options Tab</b></summary>
  The Options Tab is where you can set flash-tool specific options.

  For Thor, the options are:
  
  - T Flash - Writes the bootloader of a working device to the SD card.
  - EFS Clear - Wipes phone/network-related stuff from your device. It should NOT be used by normal users. (currently disabled until a safety is implemented)
  - Bootloader Update - I honestly have no idea what this does. Let me know if you do!
  - Reset Flash Count - I beleive this does what it sounds like it does, but I don't know when you'd ever use it. Please correct me if I'm wrong!

  For Odin4, there are currently no options.
  The "-V", "Validate home binary with pit file" option might be added if someone can tell me what it does.
  
  </details>
  </p>
  
  <p>
  <details>
  <summary><b>Pit Tab</b></summary>
  The Pit Tab is just a placeholder currently.
  </details>
  </p>
  
  <p>
  <details>
  <summary><b>Settings Tab</b></summary>
  The Settings Tab is where you can change Galaxy Flasher's settings.
  Here is a list of them:

  - Flash Tool - The flash-tool you would like Galaxy Flasher to use. The options are:
    - Thor - An open-source flash-tool. The last update was almost a year ago, sadly.
    - Odin4 - A proprietary, official Samsung flash-tool that was leaked.
    - PyThor - An open-source flash-tool that is still in development. The only real reason to use it is if you plan on contributing to it.

  - Theme - The theme you would like Galaxy Flasher to use. The options are:
    - System - Galaxy Flasher will attempt to use the system theme.
    - Light - Light theme.
    - Dark - Dark theme.

  - Run Thor with sudo - This allows you to choose whether or not you want to run Thor with sudo. By default it is turned off; Turning it on may fix errors in some cases. This only applies to Thor.
    
  - [Thor] Automatically select all partitions - This automatically selects all of the partitions from the files you select, instead of asking you what ones you would like to select. This only applies to Thor.

  </details>
  </p>

### Selecting Files

To select files to flash, you can:

- Click the corresponding file button, which will open a file picker.
- Drag and drop a file into it's corresponding file entry.
- Copy/Paste (or type!) a file-path into the correct file entry.

Corresponding or correct as in if you want to select a CP file, click the CP file button, if you have a BL file-path copied, paste it into the BL file entry, etc.

### Flashing Files

Flashing files with Galaxy Flasher is easy. Here's how to do it:

  <p>
  <details>
  <summary><b>Thor</b></summary>

  - Click the "Connect" button. If there is more than one device connected, you will be prompted to select a device. You will know you have connected when the "Connect" button changes to "Disconnect".
  - Once you're connected to a device, click the "Start Odin Protocol" button. If the button changes to "End Odin Protocol", you're good.
  - Click the "Flash!" button. (after you've selected at least one file to flash)
  - If the "[Thor] Automatically select all partitions" setting is off, you will be asked to select what partitions to flash from each file you selected. If that setting is on, Galaxy Flasher will automatically select all of the partitions for each file you selected.
  - Once you (or the computer) have selected the partitions to flash from each file you selected, a "Verify Flash" window will appear. This is when you can abort if you didn't mean to flash what you selected. Click "No" to cancel, or "OK" to begin flashing the device.
  </details>
  </p>

  <p>
  <details>
  <summary><b>Odin4</b></summary>

  Please note that unlike Thor, Odin4 does not have a "Verify Flash" window. If you accidentally started flashing your device, you can disconnect it from your computer when Odin4 is verifying the files. (verifying the files is the first thing it does, followed by flashing them) If Odin4 has already started flashing the files to your device, disconnecting your device may cause even more issues.

  - Click the "Flash!" button. (after you've selected at least one file to flash)
  - If there is more than one device connected, you will be prompted to select a device.
  - That's it!

  </details>
  </p>




## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Galaxy Flasher needs a logo! If you would be interested in making one, please open a new issue.
+ Find and report bugs. If you find an issue that isn't listed above in "Known Bugs" or [here](https://github.com/ethical-haquer/Galaxy-Flasher/issues), please let me know!
+ ~Help translate Galaxy Flasher into your language. Refer to [this readme](https://github.com/ethical-haquer/Galaxy-Flasher/blob/main/locales/README.md) for more info~. NOTE: Currently, the en.json file is in dire need of updating after the re-write, so please don't add other translations until it is updated. Thanks!
+ Improve the code. Pull requests are always welcome!
+ Suggest an improvement by opening up a [feature request](https://github.com/ethical-haquer/Galaxy-Flasher/issues/new/choose)!

## Credits

[TheAirBlow](https://github.com/theairblow) for posting [Odin4](https://xdaforums.com/t/official-samsung-odin-v4-1-2-1-dc05e3ea-for-linux.4453423/) to XDA, and for creating the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).

[justaCasualCoder](https://github.com/justaCasualCoder) for his contributions, and for starting the port to GTK4 on his own.

[Not_Rich@XDA](https://xdaforums.com/m/not_rich.8463826/) for continuing to test out new versions and suggest improvements.

[ethical_haquer](https://github.com/ethical-haquer) for Galaxy Flasher.

## License

Galaxy Flasher is licensed under GPLv3. Please see [`LICENSE`](./LICENSE) for the full license text.
