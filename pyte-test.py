import threading as thrd
import tkinter as tk
from tkinter import Frame, Scrollbar, Text, font
import re

import pexpect
import pyte
import pyte.graphics
from pyte.screens import HistoryScreen

COLOR_MAPPINGS = {
    "black": "black",
    "red": "#ff0000",
    "green": "#00ff00",
    "yellow": "#ffff00",
    "blue": "#0000ff",
    "magenta": "#ff00ff",
    "cyan": "#00ffff",
    "white": "white",
}

class Terminal(Frame):
    def __init__(
        self, master=None, log_file=None, font_size=8, color=False, *args, **kwargs
    ):
        super().__init__(master)

        self.color = color
        self.fg = kwargs.pop("fg", "white")  # Fallback to white if not specified
        self.bg = kwargs.pop("bg", "black")  # Fallback to black if not specified

        self.key_pressed = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.rows = 0
        self.cols = 0
        # Configure the font
        self.custom_font = font.Font(family="Monospace", size=font_size)
        self.cached_size = None

        self.text = Text(self, font=self.custom_font, *args, **kwargs)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.config(state="normal", cursor="xterm", insertbackground=self.bg)

        self.text.bind("<1>", lambda event: self.text.focus_set())

        self.screen = HistoryScreen(80, 24)
        self.text_rows = 24
        self.stream = pyte.ByteStream()
        self.stream.attach(self.screen)

        # self.child = pexpect.spawn('/home/ethical_haquer/TheAirBlow.Thor.Shell')
        self.child = pexpect.spawn("/bin/bash")
        # self.child = pexpect.spawn('ls -l')
        self.after_id = None
        self.bind("<Configure>", self.on_resize)
        self.text.bind("<KeyPress>", self.on_key_press, add=True)
        self.text.tag_configure("block_cursor", background=self.fg, foreground=self.bg)
        self.text.focus_set()

        # Scrollback buffer and alternate screen flag
        self.scrollback_buffer = []
        self.max_scrollback_size = 1000  # Adjust as needed
        self.in_alternate_screen = False  # Flag for alternate screen
        # Add a vertical scrollbar
        self.scrollbar = Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Link scrollbar to the text widget
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        # Create a context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)
        self.context_menu.add_command(
            label="Dump History", command=self.dump_pyte_history
        )
        self.context_menu.add_command(
            label="Repaint Screen", command=self.custom_repaint
        )

        # Bind right-click to show the context menu
        self.text.bind("<Button-3>", self.show_context_menu)  # For Windows/Linux

        self.output_thread = thrd.Thread(target=self.fetch_pexpect_data)
        self.output_thread.daemon = True
        self.output_thread.start()

    def paste_from_clipboard(self):
        try:
            clipboard_text = root.clipboard_get(type="STRING")
            self.text.insert(tk.INSERT, clipboard_text)
        except tk.TclError:  # If there is no data on clipboard
            pass

    def custom_repaint(self):
        print("ABABABABABABABABABABABABABABABAB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Redraw the terminal screen, update cursor position, and apply color.
        # Enable text widget editing to update the content
        self.text.config(state="normal")

        # Clear the current content of the text widget
        self.text.delete("1.0", tk.END)

        # Extract history as text lines
        history_lines = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            history_lines.append(processed_line)

        # Combine history and current screen content
        combined_lines = history_lines
        for line in self.screen.display:
            print(line)
        for line in self.screen.display:
            # If the line is a string, append it directly
            if isinstance(line, str):
                combined_lines.append(line)
            else:
                # If the line is not a string, it might be a list or another collection of characters
                line_str = ""
                for char in line:
                    # Check if char has a 'data' attribute
                    if hasattr(char, "data"):
                        line_str += char.data
                    else:
                        line_str += char  # Assuming char is a character
                combined_lines.append(line_str)

        # Calculate the terminal screen height in rows
        _, rows = self.calculate_size(self.text.winfo_width(), self.text.winfo_height())
        for line in combined_lines:
            print("combined lines ---------------------------------------")
            print(line)
        print("----------------------------------------")
        # Determine which lines to display based on the terminal size
        total_lines = len(combined_lines)
        start_line = max(0, total_lines - rows)
        lines_to_display = combined_lines[start_line:]

        # Join the lines and insert them into the Text widget
        full_text = "\n".join(combined_lines)
        self.text.insert("1.0", full_text)

        # Apply color tags
        for y, line in enumerate(lines_to_display, 1):
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg = COLOR_MAPPINGS.get(
                    char_style.fg, self.bg
                )  # Default to white if not found
                bg = COLOR_MAPPINGS.get(
                    char_style.bg, self.fg
                )  # Default to black if not found
                tag_name = f"color_{self.fg}_{self.bg}"

                # Create the tag if it doesn't exist
                if tag_name not in self.text.tag_names():
                    self.text.tag_configure(tag_name, foreground=fg, background=bg)

                self.text.tag_add(tag_name, f"{y}.{x}", f"{y}.{x + 1}")

        # Update block cursor position
        self.update_cursor()

        # Disable editing of the content to prevent user edits
        self.text.config(state="disabled")

        # Set the scrollbar to the bottom (most recent part of the output)
        self.text.yview_moveto(1)

    def dump_pyte_history(self):
        lines_as_text = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            lines_as_text.append(processed_line)

        # Now print or add to the text widget
        final_output = "\n".join(lines_as_text)
        print(final_output)  # or display in your text widget
        return final_output

    def show_context_menu(self, event):
        try:
            # Display the context menu
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure the menu is closed after selection
            self.context_menu.grab_release()

    def copy_to_clipboard(self):
        try:
            # Get the selected text
            selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Clear the clipboard and append the selected text
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected or other error
            pass

    def fetch_pexpect_data(self):
        def update_ui(data):
            self.stream.feed(data)  # Feed the raw byte data
            data_str = data.decode("utf-8", errors="ignore")

            self.handle_escape_sequences(
                data_str
            )  # Check for alternate screen escape sequences using the decoded string

            if not self.in_alternate_screen:
                # Handle scrolling only if not in alternate screen
                while len(self.screen.dirty) > 0:
                    line_index = self.screen.dirty.pop()
                    line = self.screen.buffer[line_index]
                    self.add_to_scrollback(line)

            self.redraw()
            self.update_cursor()

        while True:
            if self.child:
                data = self.child.read_nonblocking(4096, timeout=None)
                print(data)
            if not data:
                break
            update_ui(data)

    def handle_escape_sequences(self, data_str):
        # Entering alternate screen
        if "\x1b[?1049h" in data_str:
            self.in_alternate_screen = True
            self.screen.reset_mode(pyte.modes.LNM)

            self.redraw()
        # Leaving alternate screen
        elif "\x1b[?1049l" in data_str:
            self.in_alternate_screen = False
            self.redraw()

    def add_to_scrollback(self, line):
        if len(self.scrollback_buffer) >= self.max_scrollback_size:
            self.scrollback_buffer.pop(0)  # Remove the oldest line if we're at capacity
        self.scrollback_buffer.append(line)

    def on_key_press(self, event):
        keysym = event.keysym
        char = event.char

        special_keys = {
            "Return": "\r",
            "BackSpace": "\b",
            "Escape": "\x1b",
            "Up": "\x1b[A",
            "Down": "\x1b[B",
            "Right": "\x1b[C",
            "Left": "\x1b[D",
            "F1": "\x1bOP",
            "F2": "\x1bOQ",
            "F3": "\x1bOR",
            "F4": "\x1bOS",
            "F5": "\x1b[15~",
            "F6": "\x1b[17~",
            "F7": "\x1b[18~",
            "F8": "\x1b[19~",
            "F9": "\x1b[20~",
            "F10": "\x1b[21~",
            "F11": "\x1b[23~",
            "F12": "\x1b[24~",
            "Insert": "\x1b[2~",
            "Delete": "\x1b[3~",
            "Home": "\x1b[H",
            "End": "\x1b[F",
            "PageUp": "\x1b[5~",
            "PageDown": "\x1b[6~",
            "q": "\033[q",
        }

        # Check if the key is a special key
        if keysym in special_keys:
            self.child.send(special_keys[keysym])
        elif char:
            # Send the character if it's a regular key
            self.child.send(char)

    def on_resize(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(500, lambda: self.handle_resize(event))

    def handle_resize(self, event):
        cols, rows = self.calculate_size(event.width, event.height)
        self.text_rows = rows
        self.resize_pty(cols, rows)

    def calculate_size(self, width, height):
        char_width = self.custom_font.measure("M")
        char_height = self.custom_font.metrics("linespace")
        cols = width // char_width
        rows = height // char_height
        self.rows = rows
        self.cols = cols
        return cols, rows

    def resize_pty(self, cols, rows):
        self.child.setwinsize(rows, cols)
        self.screen.resize(rows, cols)
        self.rows = rows
        self.cols = cols
        self.redraw()

    def update_cursor(self):
        cursor_line, cursor_col = self.screen.cursor.y, self.screen.cursor.x

        if self.in_alternate_screen:
            cursor_line += 1

        cursor_pos = f"{cursor_line}.{cursor_col}"

        self.text.tag_remove("block_cursor", "1.0", tk.END)
        self.text.tag_add("block_cursor", cursor_pos, f"{cursor_pos} + 1c")
        self.text.tag_configure("block_cursor", background=self.fg, foreground=self.bg)
        self.text.mark_set("insert", cursor_pos)

        if not self.in_alternate_screen:
            total_lines_in_widget = int(self.text.index("end-1c").split(".")[0])
            lines_from_bottom = self.screen.lines - self.screen.cursor.y
            cursor_line = total_lines_in_widget - lines_from_bottom
            cursor_pos = f"{cursor_line + 1}.{cursor_col}"

        self.text.tag_remove("block_cursor", "1.0", tk.END)
        self.text.tag_add("block_cursor", cursor_pos, f"{cursor_pos} + 1c")
        self.text.tag_configure("block_cursor", background=self.fg, foreground=self.bg)
        self.text.mark_set("insert", f"{cursor_line + 1}.{cursor_col + 1}")
        self.text.see(cursor_pos)

    def extract_history_as_text(self, screen):
        lines_as_text = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            lines_as_text.append(processed_line)
        return lines_as_text

    def is_hex_color_code(self, s):
        # Define the regular expression pattern for a hexadecimal color code
        pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    
        # Check if the string matches the pattern
        if re.match(pattern, s):
            return True
        else:
            return False

    # Avg 12%, 28% CPU
    def redraw(self):
        old_fg = None
        old_bg = None
        fgd_bgd = None
        text_widget = self.text
        text_widget.config(state="normal")
        text_widget.configure(background=self.bg)

        history_lines = self.extract_history_as_text(self.screen)
        combined_lines = history_lines if not self.in_alternate_screen else []
        for line in self.screen.display:
            if isinstance(line, str):
                combined_lines.append(line)
            else:
                line_str = "".join(
                    char.data if hasattr(char, "data") else char for char in line
                )
                combined_lines.append(line_str)

        rows = self.text_rows
        total_lines = len(combined_lines)
        start_line = max(0, total_lines - rows)
        offset = total_lines - len(self.screen.display)

        full_text = "\n".join(combined_lines)
        text_widget.replace("1.0", tk.END, full_text)

        tag_ranges = {}
        tag_names = set()
        for y, line in enumerate(self.screen.display, start=start_line + 1):
            line_tags = []
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg = char_style.fg
                bg = char_style.bg
                
                if self.is_hex_color_code(fg):
                    if not fg.startswith("#"):
                        fg = f"#{fg}"
                else:
                    fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
                
                if self.is_hex_color_code(bg):
                    if not bg.startswith("#"):
                        bg = f"#{bg}"
                else:
                    bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
                
                if fg != old_fg:
                    old_fg = fg
                    print(fg + " fg")
                if bg != old_bg:
                    old_bg = bg
                    print(bg + " bg")
                    
                tag_name = f"color_{fg}_{bg}"
                if tag_name != fgd_bgd:
                    fgd_bgd = tag_name
                    print(tag_name)
                line_tags.append(
                    (tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")
                )
                tag_names.add(tag_name)

            tag_ranges[y] = line_tags

        for tag_name in tag_names:
            fg, bg = tag_name.split("_")[1:]
            text_widget.tag_configure(tag_name, foreground=fg, background=bg)

        for y, line_tags in tag_ranges.items():
            for tag_name, start_pos, end_pos in line_tags:
                text_widget.tag_add(tag_name, start_pos, end_pos)

        text_widget.tag_raise("block_cursor")
        text_widget.tag_raise("sel")

        cursor_line, cursor_col = (
            self.screen.cursor.y + 1 + offset,
            self.screen.cursor.x + 1,
        )
        text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
        text_widget.see("insert")

        text_widget.focus_set()

    def destroy(self):
        if self.child:
            self.child.terminate()
            self.output_thread.join(timeout=0.25)
            self.child = None
        super().destroy()

if __name__ == "__main__":
    log_file = "tkinter-terminal.log"
    ui_config = {
        "wrap": "none",
        "bg": "white",
        "fg": "black",
        "font_size": 11,
    }
    root = tk.Tk()
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    term = Terminal(root, log_file=log_file, **ui_config)
    term.grid(row=0, column=0, sticky="nsew")

    root.protocol("WM_DELETE_WINDOW", term.destroy)

    root.mainloop()
