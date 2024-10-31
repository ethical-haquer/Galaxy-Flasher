# Locales
This folder contains all the locale files to support different languages. The language that is used by Thor GUI is dependent on your system language. If your language is not yet supported by Thor GUI, it will fallback to English.

If you want to translate Thor GUI to a language which is not yet supported, use the [`en.json`](https://github.com/ethical-haquer/Thor_GUI/blob/main/locales/en.json) file as a base for the translation.
Make sure that the json file is named using the same format (for example, Japanese = `ja.json`).

If you want to check what display language is being reported to Thor GUI, you can run these commands in the Python shell:

```
import locale
locale.setlocale(locale.LC_ALL, "")
locale = locale.getlocale(locale.LC_MESSAGES)[0]
seperator = '_'
locale.split(seperator, 1)[0]
```

During translation, it's a good idea to run Thor GUI with the translated language and see the end result. Just follow the [installation instructions](https://github.com/ethical-haquer/Thor_GUI?tab=readme-ov-file#installation) and run `thor_gui.py`. As long as the translated file is properly named and placed in the locales folder, Thor GUI should automatically display in the new language.

You can use the newline character `\n` to split long strings onto multiple lines. Text enclosed in `{}` brackets, such as `{file}`, are variables which should be left the way they are and not be translated.

If you have any questions, just let me know. Thanks for helping!

NOTE: This readme was copied from [WSA-Sideloader](https://github.com/infinitepower18/WSA-Sideloader/blob/main/locales/README.md), which inspired me to add translation support to Thor GUI.
