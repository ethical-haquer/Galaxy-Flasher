"""
def redraw(self):
    self.text.config(state='normal')
    self.text.delete("1.0", tk.END)
    self.text.tag_configure("sel", background="blue", foreground="white")

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []

    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    _, rows = self.calculate_size(self.text.winfo_width(), self.text.winfo_height())
    total_lines = len(combined_lines)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    full_text = "\n".join(combined_lines)
    self.text.insert("1.0", full_text)
    self.text.yview_moveto(1)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"

            tag_names.add(tag_name)

            if tag_name not in self.text.tag_names():
                self.text.tag_configure(tag_name, foreground=fg, background=bg)
            self.text.tag_add(tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")

    for existing_tag in set(self.text.tag_names()) - tag_names:
        self.text.tag_remove(existing_tag, "1.0", tk.END)

    self.text.tag_raise('block_cursor')
    self.text.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    self.text.mark_set("insert", f"{cursor_line}.{cursor_col}")
    self.text.see("insert")

    self.text.focus_set()
    
    # Only colors first char of change
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            if prev_color != tag_name:
                tag_names.add(tag_name)
                self.text.tag_configure(tag_name, foreground=fg, background=bg)
                self.text.tag_add(tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")
            prev_color = tag_name

    # Remove any tags that are no longer needed
    for existing_tag in set(self.text.tag_names()) - tag_names:
        self.text.tag_remove(existing_tag, "1.0", tk.END)

    # Raises the cursor tag
    self.text.tag_raise('block_cursor')
    self.text.tag_raise('sel')

    # Sets the insert mark and focuses the text widget
    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    self.text.mark_set("insert", f"{cursor_line}.{cursor_col}")
    self.text.see("insert")
    self.text.focus_set()
    # Works, but uses crazy CPU and is slow
    tag_names = set()
    current_tag = None
    start_x = 0
    start_line = 0
    prev_color = None

    for y, line in enumerate(self.screen.display, start=start_line + 1):
        color_group_start = 0

        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"

            if prev_color != tag_name:
                if current_tag is not None:
                    self.text.tag_add(current_tag, f"{y + offset}.{color_group_start}", f"{y + offset}.{x}")
                current_tag = tag_name
                color_group_start = x

            tag_names.add(tag_name)
            self.text.tag_configure(tag_name, foreground=fg, background=bg)

        if current_tag is not None:
            self.text.tag_add(current_tag, f"{y + offset}.{color_group_start}", f"{y + offset}.{x + 1}")

        prev_color = tag_name

    for existing_tag in set(self.text.tag_names()) - tag_names:
        self.text.tag_remove(existing_tag, "1.0", tk.END)

    # Raises the cursor tag
    self.text.tag_raise('block_cursor')
    self.text.tag_raise('sel')

    # Sets the insert mark and focuses the text widget
    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    self.text.mark_set("insert", f"{cursor_line}.{cursor_col}")
    self.text.see("insert")
    self.text.focus_set()
    """


"""
# An attempt to have a second text widget come to the top and hide the updating text widget
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.configure(background='black')
    
    secondary_text_widget = tk.Text(self, wrap='none', bg='black', fg='white')
    secondary_text_widget.config(state='normal')
    secondary_text_widget.tag_configure("block_cursor", background="white", foreground="black")

    secondary_text_widget.replace("1.0", tk.END, text_widget.get("1.0", tk.END))

    secondary_text_widget.grid(row=0, column=0, sticky="nsew")

    #text_widget = self.text
    #text_widget.config(state='normal')
    #text_widget.configure(background='black')

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
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
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            line_tags.append((tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}"))
            tag_names.add(tag_name)
    
        tag_ranges[y] = line_tags

    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    for y, line_tags in tag_ranges.items():
        for tag_name, start_pos, end_pos in line_tags:
            text_widget.tag_add(tag_name, start_pos, end_pos)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")

    text_widget.lift()
    text_widget.focus_set()
    secondary_text_widget.destroy()
    """

"""
# Avg 12%, 29% CPU
# This optimized version batches tag configurations for each line, reducing the number of tag operations.
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.configure(background=self.bg)
    text_widget.delete("1.0", tk.END)
    text_widget.tag_configure("sel", background="blue", foreground="white")

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    rows = self.text_rows
    total_lines = len(combined_lines)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    full_text = "\n".join(combined_lines)
    text_widget.insert("1.0", full_text)
    text_widget.yview_moveto(1)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        line_tags = []
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            line_tags.append((tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}"))
            tag_names.add(tag_name)
    
        for tag_name, start_pos, end_pos in line_tags:
            text_widget.tag_add(tag_name, start_pos, end_pos)

    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")

    text_widget.focus_set()
    """

"""
#Avg 12%, 30% CPU
# This version updates the terminal screen dynamically by replacing the entire text content and only adding or updating tags for the changed portions of the screen. This approach minimizes unnecessary tag operations and text updates, improving the rendering efficiency.
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.configure(background=self.bg)

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    rows = self.text_rows
    total_lines = len(combined_lines)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    full_text = "\n".join(combined_lines)
    text_widget.replace("1.0", tk.END, full_text)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        line_tags = []
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            line_tags.append((tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}"))
            tag_names.add(tag_name)
    
        for tag_name, start_pos, end_pos in line_tags:
            text_widget.tag_add(tag_name, start_pos, end_pos)

    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")

    text_widget.focus_set()
    """

"""
# Avg. 18%, 54% CPU
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.delete("1.0", tk.END)
    text_widget.tag_configure("sel", background="blue", foreground="white")

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    rows = self.text_rows
    print(rows)
    total_lines = len(combined_lines)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    full_text = "\n".join(combined_lines)
    text_widget.insert("1.0", full_text)
    text_widget.yview_moveto(1)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            tag_names.add(tag_name)
            text_widget.tag_add(tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")

    text_widget.tag_remove("all", "1.0", tk.END)  # Clear all tags
    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")

    text_widget.focus_set()
    """

"""
# Avg 19%, 56% CPU
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.delete("1.0", tk.END)
    text_widget.tag_configure("sel", background="blue", foreground="white")

    rows = self.text_rows
    total_lines = len(self.screen.display)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    combined_lines = []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    full_text = "\n".join(combined_lines)
    text_widget.insert("1.0", full_text)
    text_widget.yview_moveto(1)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            tag_names.add(tag_name)
            text_widget.tag_add(tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")

    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")
    text_widget.focus_set()
    """
"""
# Avg 1.5%, 3% CPU, no color
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.delete("1.0", tk.END)
    text_widget.tag_configure("sel", background="blue", foreground="white")

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []
    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    full_text = "\n".join(combined_lines)
    text_widget.insert("1.0", full_text)
    text_widget.yview_moveto(1)

    start_line, rows = self.calculate_size(text_widget.winfo_width(), text_widget.winfo_height())

    # Create tag ranges for styling blocks of text
    tag_ranges = []
    tag_start = "1.0"
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        line_text = ''.join(char.data if hasattr(char, 'data') else char for char in line)
        tag_ranges.append((tag_start, f"{tag_start}+{len(line_text)}c"))
        tag_start = f"{tag_start}+{len(line_text)+1}c"

    # Apply tags to tag ranges
    for tag_range in tag_ranges:
        text_widget.tag_add("block_style", tag_range[0], tag_range[1])

    # Configure the block_style tag
    text_widget.tag_configure("block_style", foreground=self.fg, background=self.bg)

    # Set cursor position and focus
    cursor_line, cursor_col = self.screen.cursor.y + 1, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")
    text_widget.focus_set()
    """

"""
# Avg 18%, 64% CPU
def redraw(self):
    text_widget = self.text
    text_widget.config(state='normal')
    text_widget.delete("1.0", tk.END)
    text_widget.tag_configure("sel", background="blue", foreground="white")

    history_lines = self.extract_history_as_text(self.screen)
    combined_lines = history_lines if not self.in_alternate_screen else []

    for line in self.screen.display:
        if isinstance(line, str):
            combined_lines.append(line)
        else:
            line_str = "".join(char.data if hasattr(char, 'data') else char for char in line)
            combined_lines.append(line_str)

    _, rows = self.calculate_size(text_widget.winfo_width(), text_widget.winfo_height())
    total_lines = len(combined_lines)
    start_line = max(0, total_lines - rows)
    offset = total_lines - len(self.screen.display)

    full_text_lines = combined_lines[start_line:]
    full_text = "\n".join(full_text_lines)

    text_widget.insert("1.0", full_text)
    text_widget.yview_moveto(1)

    tag_names = set()
    for y, line in enumerate(self.screen.display, start=start_line + 1):
        for x, char in enumerate(line):
            char_style = self.screen.buffer[y - 1][x]
            fg = COLOR_MAPPINGS.get(char_style.fg, self.fg)
            bg = COLOR_MAPPINGS.get(char_style.bg, self.bg)
            tag_name = f"color_{fg}_{bg}"
            tag_names.add(tag_name)
            text_widget.tag_add(tag_name, f"{y + offset}.{x}", f"{y + offset}.{x + 1}")

    # Remove only the tags that are not in tag_names
    for tag in text_widget.tag_names():
        if tag not in tag_names and tag != "sel":
            text_widget.tag_remove(tag, "1.0", tk.END)
            
    for tag_name in tag_names:
        fg, bg = tag_name.split('_')[1:]
        text_widget.tag_configure(tag_name, foreground=fg, background=bg)

    text_widget.tag_raise('block_cursor')
    text_widget.tag_raise('sel')

    cursor_line, cursor_col = self.screen.cursor.y + 1 + offset, self.screen.cursor.x + 1
    text_widget.mark_set("insert", f"{cursor_line}.{cursor_col}")
    text_widget.see("insert")

    text_widget.focus_set()
    """
