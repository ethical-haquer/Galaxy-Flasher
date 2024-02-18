# Locales
This folder contains all the locale files to support multiple languages. The language that is used by Thor GUI is dependent on your system language. If your language isn't yet supported by Thor GUI, it will fallback to English.

If you want to translate Thor GUI to a language which is not yet supported, use the `en.json` file as a base for the translation.
Make sure that the json file is named with the same format e.g. Japanese `ja.json`.

If you have Python installed on your system, and want to check what display language is being reported to Thor GUI, you can run these commands using the Python shell:

```
import locale
locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = '_'
locale.split(seperator, 1)[0]
```

During translation, it is a good idea to run Thor GUI with the translated language to see the end result. Just make sure you have Git and Python installed, clone this repo, install the dependencies and run `thor_gui.py`. As long as the translated file is properly named and placed in the locales folder, it should automatically display in that language.

You can use the newline character `\n` to put the text after it to the next line on the screen. Text enclosed in `{}` brackets, such as `{file}` are variables which should be left the way they are and not be translated.

NOTE: This readme was copied from [WSA-Sideloader](https://github.com/infinitepower18/WSA-Sideloader/blob/main/locales/README.md), which inspired me to add translation support to Thor GUI.
