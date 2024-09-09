<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/images/galaxy-flasher-dark-light.png">
    <source media="(prefers-color-scheme: light)" srcset="/images/galaxy-flasher-light-dark.png">
    <img src="images/galaxy-flasher-dark-light.png" alt="Screenshot of Galaxy Flasher" width="500">
  </picture>
</div>
<div align="center">

Have any ideas for the icon? Let me know on [Codeberg](https://codeberg.org/ethical_haquer/Galaxy-Flasher/issues/21), [GitHub](https://github.com/ethical-haquer/Galaxy-Flasher/issues/21), or [XDA](https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/page-4#post-89701721).

</div>
<h1 align="center">Galaxy Flasher</h1>
<div align="center">

A GUI for Samsung flash-tools.

[Codeberg](https://codeberg.org/ethical_haquer/Galaxy-Flasher) | [GitHub](https://github.com/ethical-haquer/Galaxy-Flasher) | [XDA](https://xdaforums.com/t/linux-galaxy-flasher-a-gui-for-samsung-flash-tools.4636402/)

</div>
<details>
  <summary><b>Screenshots</b></summary>
  <br>
  Options Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/images/galaxy-flasher-options-tab-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="/images/galaxy-flasher-options-tab-light.png">
    <img src="images/galaxy-flasher-options-tab-dark.png" alt="Screenshot of the Options Tab">
  </picture>
  <br>
  Pit Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/d10aecd0-633f-4c20-a738-d56dad080772">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/ab4ffcf2-1198-43dd-9b2d-a20841821eaf">
    <img alt="Pit Tab">
  </picture>
  <br>
  Settings Tab:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/d3f424ad-25c5-4e40-ba74-75ed5713e2ab">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/6340bddb-ad4d-4567-bc97-8f028bbb7865">
    <img alt="Settings Tab">
  </picture>
  <br>
  About Dialog:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/5e6b5625-4cde-43a4-a459-44d943cfbe74">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/788a7330-69dd-43ea-9cfa-3be68f1c058b">
    <img alt="About Tab">
  </picture>
  <br>
  "Select Partitions" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/91c6b476-3917-42c4-9d9a-1ac3f3bf931a">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/c1b972a5-a9e1-4e02-81e4-cce970cea5c4">
    <img alt="Select Partitions Window">
  </picture>
  <br>
  "Verify Flash" Window:
  <br>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/ef054041-001a-483e-a438-073b6a49276d">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/90cd9c3a-dc40-4538-837e-571e7c22b8e2">
    <img alt="Verify Flash Window">
  </picture>
</details>

## Background

After witnessing a new Linux user, who had just switched over from Windows, struggle with using Odin4's CLI, I decided to make a GUI for Thor: Thor GUI. With the release of v0.5.0, Thor GUI was renamed Galaxy Flasher, and it now supports Thor and Odin4.

## Disclaimer

Currently, Galaxy Flasher is in an Alpha stage. There are known (and probably unknown) bugs. A list of missing features and know bugs in the **latest release** can be found below.

## Known Bugs

- Setting options through the Options Tab is buggy.

## TODO

- Improve the Options Tab for Thor
- Display the partitions to be flashed in the Verify Flash Window
- Use an Adw.Dialog for the Select Partitions Window
- Hide Thor-specific settings if the current flash-tool is not Thor
- Publish Galaxy Flasher on FlatHub

## Supported platforms

- [x] Linux x64
- [ ] Linux arm64 (WIP, only Thor can be used, untested)
- [ ] Windows
- [ ] macOS

## Supported flash-tools

- Thor
- Odin4
- PyThor (in development)

## Installation and Usage

For how to install and use Galaxy Flasher, refer to the [Galaxy Flasher documentation](https://galaxy-flasher-docs.readthedocs.io/en/latest/).

## How you can help

Here are some ways you can help me improve/finish Thor GUI:
+ Galaxy Flasher needs a logo! If you would be interested in making one, please open a new issue.
+ Find and report bugs. If you find an issue that isn't listed as a [known bug](https://github.com/ethical-haquer/Galaxy-Flasher?tab=readme-ov-file#tabs), and isn't listed [here](https://github.com/ethical-haquer/Galaxy-Flasher/issues), please let me know!
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
