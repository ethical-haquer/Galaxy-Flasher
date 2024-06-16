
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

## Usage (text coming soon)

Galaxy Flasher's layout is similiar to Odin. In the upper-right there are four buttons: "Log", "Options", "Pit", and "Settings". Clicking these buttons will change what tab you are viewing. The Log Tab displays the output from the flash tool. The Options Tab lets you set flash tool specific options. The Pit Tab is currently a place-holder, there is nothing there. The Settings Tab is where you can change Galaxy Flasher's settings. In the bottom-right area, you will see five nearly identical rows consisting of a button and an entry. That is where you select files to flash.

### Tabs

<details>
  <summary><b>Log Tab</b></summary>
  The Log Tab displays the output from the Flash Tool.
  <br>
  You are also able to enter commands into the Log Tab, just as you would in the terminal.
</details>

<details>
  <summary><b>Options Tab<b></summary>
    The Options Tab is where you can set Flash Tool specific options.
    <br>
    For Thor, the options are:
    <ul>
      <li>T Flash - </li>
      <li>EFS Clear</li>
      <li>Bootloader Update</li>
      <li>Reset Flash Count</li>
    </ul>
</details>

[Galaxy-Flasher-Thor-Screencast-Dark.webm](https://github.com/ethical-haquer/Galaxy-Flasher/assets/141518185/bc8c07d5-17ea-447a-b4b2-98aa295cc3e6)

## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Galaxy Flasher needs a logo! If you would be interested in making one, please open a new issue.
+ Find and report bugs. If you find an issue that isn't listed above in "Known Bugs" or [here](https://github.com/ethical-haquer/Galaxy-Flasher/issues), please let me know!
+ ~Help translate Thor GUI into your language. Refer to [this readme](https://github.com/ethical-haquer/Thor_GUI/blob/main/locales/README.md) for more info~. NOTE: Currently, the en.json file is in dire need of updating after the re-write, so please don't add other translations until it is updated. Thanks!
+ Improve the code. Pull requests are always welcome!
+ Suggest an improvement by opening up a [feature request](https://github.com/ethical-haquer/Thor_GUI/issues/new/choose)!

## Credits

[TheAirBlow](https://github.com/theairblow) for posting [Odin4](https://xdaforums.com/t/official-samsung-odin-v4-1-2-1-dc05e3ea-for-linux.4453423/) to XDA, and for creating the [Thor Flash Utility](https://github.com/Samsung-Loki/Thor).

[justaCasualCoder](https://github.com/justaCasualCoder) for his contributions, and for starting the port to GTK4 on his own.

[Not_Rich@XDA](https://xdaforums.com/m/not_rich.8463826/) for continuing to test out new versions and suggest improvements.

Myself, [ethical_haquer](https://github.com/ethical-haquer), for Galaxy Flasher.

## License

Thor GUI is licensed under GPLv3. Please see [`LICENSE`](./LICENSE) for the full license text.
