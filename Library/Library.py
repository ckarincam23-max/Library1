import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from datetime import datetime


TITLE_FONT = "Georgia"


DARK = {
    "bg": "#141414",
    "card": "#1f1f1f",
    "text": "#ffffff",
    "muted": "#a0a0a0",
    "border": "#555555",
    "entry_bg": "#2e2e2e",
    "entry_fg": "#ffffff",
    "button_bg": "#ffffff",
    "button_fg": "#000000",
}

LIGHT = {
    "bg": "#ffffff",
    "card": "#ececec",
    "text": "#000000",
    "muted": "#4a4a4a",
    "border": "#6e6e6e",
    "entry_bg": "#dedede",
    "entry_fg": "#000000",
    "button_bg": "#000000",
    "button_fg": "#ffffff",
}

theme = {"name": "dark", "colors": DARK}
view = {"name": "home"}

root = tk.Tk()
root.title("LibTrack")
root.geometry("900x760")
root.minsize(860, 700)

FONT = tkfont.nametofont("TkDefaultFont").actual("family")


def clean_text(text):
    result = ""
    for character in text.lower():
        if character.isalnum():
            result = result + character
    return result


class Node:
    def __init__(self, book_name, borrower_name, date_borrowed):
        self.book_name = book_name
        self.borrower_name = borrower_name
        self.date_borrowed = date_borrowed
        self.date_returned = ""
        self.last_updated = ""
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, book_name, borrower_name, date_borrowed):
        new_node = Node(book_name, borrower_name, date_borrowed)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node

    def search_all(self, name):
        matches = []
        wanted = clean_text(name)
        if wanted == "":
            return matches
        current = self.head
        while current is not None:
            if wanted in clean_text(current.book_name):
                matches.insert(0, current)
            elif wanted in clean_text(current.borrower_name):
                matches.insert(0, current)
            current = current.next
        return matches

    def find_unreturned(self, book_name):
        wanted = clean_text(book_name)
        current = self.head
        while current is not None:
            if clean_text(current.book_name) == wanted:
                if current.date_returned == "":
                    return current
            current = current.next
        return None

    def get_all(self):
        records_list = []
        current = self.head
        while current is not None:
            records_list.append(current)
            current = current.next
        return records_list


records = LinkedList()


def get_status(node):
    if node.date_returned == "":
        return "Not Returned"
    return "Returned"


def get_last_updated(node):
    if node.last_updated == "":
        return "N/A"
    return node.last_updated


def live_date(text):
    result = ""
    for character in text:
        if character in "0123456789":
            result = result + character
        elif result != "" and result[-1] != "/":
            result = result + "/"
    return result


def format_date(text):
    result = live_date(text.strip())
    if result.endswith("/"):
        result = result[:-1]
    return result


class HintEntry(tk.Entry):
    def __init__(self, parent, hint="", **kwargs):
        tk.Entry.__init__(self, parent, **kwargs)
        self.hint = hint
        self.showing_hint = False
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.show_hint()

    def show_hint(self):
        if self.hint != "" and tk.Entry.get(self) == "":
            self.showing_hint = True
            self.configure(fg=theme["colors"]["muted"])
            tk.Entry.insert(self, 0, self.hint)

    def hide_hint(self):
        if self.showing_hint:
            tk.Entry.delete(self, 0, tk.END)
            self.showing_hint = False
            self.configure(fg=theme["colors"]["entry_fg"])

    def on_focus_in(self, event):
        self.hide_hint()

    def on_focus_out(self, event):
        self.show_hint()

    def get(self):
        if self.showing_hint:
            return ""
        return tk.Entry.get(self)

    def insert(self, index, text):
        self.hide_hint()
        tk.Entry.insert(self, index, text)

    def delete(self, first, last=None):
        self.hide_hint()
        tk.Entry.delete(self, first, last)

    def clear(self):
        self.hide_hint()
        tk.Entry.delete(self, 0, tk.END)
        self.show_hint()


def watch_date(entry):
    def fix(event):
        if entry.showing_hint:
            return
        text = entry.get()
        position = entry.index(tk.INSERT)
        fixed = live_date(text)
        if fixed != text:
            new_position = len(live_date(text[:position]))
            entry.delete(0, tk.END)
            entry.insert(0, fixed)
            entry.icursor(new_position)

    entry.bind("<KeyRelease>", fix)


def make_label(parent, text, size=10, bold=False, fg_key="text", bg_key="bg", serif=False):
    colors = theme["colors"]
    weight = "normal"
    if bold:
        weight = "bold"
    family = FONT
    if serif:
        family = TITLE_FONT
    label = tk.Label(parent, text=text, font=(family, size, weight),
                     bg=colors[bg_key], fg=colors[fg_key])
    return label


def make_entry(parent, width=34, hint="", is_date=False):
    colors = theme["colors"]
    entry = HintEntry(parent, hint, font=(FONT, 10), width=width,
                      bg=colors["entry_bg"], fg=colors["entry_fg"],
                      insertbackground=colors["entry_fg"], relief="flat",
                      highlightthickness=1, highlightbackground=colors["border"],
                      highlightcolor=colors["text"])
    if is_date:
        watch_date(entry)
    return entry


def make_button(parent, text, command):
    colors = theme["colors"]
    button = tk.Button(parent, text=text, command=command, font=(FONT, 10),
                       bg=colors["button_bg"], fg=colors["button_fg"],
                       activebackground=colors["button_bg"],
                       activeforeground=colors["button_fg"],
                       relief="raised", bd=2, padx=14, pady=3, cursor="hand2")
    return button


def make_option(parent, text, command):
    colors = theme["colors"]
    label = tk.Label(parent, text=text, font=(FONT, 14, "underline"),
                     bg=colors["bg"], fg=colors["text"], cursor="hand2")
    label.bind("<Button-1>", lambda event: command())
    return label


TABLE_COLUMNS = [
    ("book", "Book Name", 170),
    ("borrower", "Borrower Name", 150),
    ("borrowed", "Date Borrowed", 105),
    ("returned", "Date Returned", 105),
    ("status", "Status", 100),
    ("updated", "Last Updated", 150),
]


def make_table(parent, height, record_list):
    table_frame = tk.Frame(parent)

    names = []
    for column in TABLE_COLUMNS:
        names.append(column[0])

    table = ttk.Treeview(table_frame, columns=names, show="headings", height=height)
    for column in TABLE_COLUMNS:
        table.heading(column[0], text=column[1])
        table.column(column[0], width=column[2])

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left")
    scrollbar.pack(side="right", fill="y")

    row_map = {}
    for record in record_list:
        returned = format_date(record.date_returned)
        if returned == "":
            returned = "-"
        item = table.insert("", tk.END, values=(record.book_name, record.borrower_name,
                                                format_date(record.date_borrowed), returned,
                                                get_status(record), get_last_updated(record)))
        row_map[item] = record

    return table_frame, table, row_map


def new_page(show_back):
    for widget in content_frame.winfo_children():
        widget.destroy()

    if show_back:
        make_button(content_frame, "← Back", show_home).pack(anchor="w", pady=(0, 10))

    body = tk.Frame(content_frame, bg=theme["colors"]["bg"])
    body.pack()
    return body


def show_home():
    view["name"] = "home"
    body = new_page(False)

    make_label(body, "Manage Your Library", 18, True).pack(pady=(40, 24))

    make_option(body, "Add Record", show_add).pack(pady=10)
    make_option(body, "Search", show_search).pack(pady=10)
    make_option(body, "Display All", show_display_all).pack(pady=10)
    make_option(body, "Update", show_update).pack(pady=10)
    make_option(body, "Exit", exit_program).pack(pady=10)


def show_add():
    view["name"] = "add"
    body = new_page(True)

    make_label(body, "Add Record", 16, True).pack(pady=(10, 12))

    make_label(body, "Book Name", 10, False, "muted").pack()
    book_entry = make_entry(body, 34, "ex. The Bible")
    book_entry.pack(pady=(2, 10), ipady=5)

    make_label(body, "Borrower Name", 10, False, "muted").pack()
    borrower_entry = make_entry(body, 34, "ex. da vinci")
    borrower_entry.pack(pady=(2, 10), ipady=5)

    make_label(body, "Date Borrowed", 10, False, "muted").pack()
    date_entry = make_entry(body, 34, "ex. 10/10/2010", True)
    date_entry.pack(pady=(2, 10), ipady=5)

    message_label = make_label(body, "", 10, True)
    message_label.configure(wraplength=400, justify="center")

    def save():
        book = book_entry.get().strip()
        borrower = borrower_entry.get().strip()
        date = format_date(date_entry.get())
        if book == "" or borrower == "" or date == "":
            message_label.configure(text="Please fill in all fields.")
            return
        unreturned = records.find_unreturned(book)
        if unreturned is not None:
            message_label.configure(text=unreturned.book_name + " is still borrowed by " +
                                    unreturned.borrower_name + ".")
            return
        records.add(book, borrower, date)
        root.focus_set()
        book_entry.clear()
        borrower_entry.clear()
        date_entry.clear()
        message_label.configure(text="Record Saved")

    make_button(body, "Save", save).pack(pady=8, ipady=2)
    message_label.pack(pady=5)


def show_search():
    view["name"] = "search"
    body = new_page(True)
    colors = theme["colors"]

    make_label(body, "Search Record", 16, True).pack(pady=(10, 4))
    make_label(body, "Type a book or borrower name, then press Enter", 10, False, "muted").pack(pady=(0, 10))

    row = tk.Frame(body, bg=colors["bg"])
    row.pack()

    search_entry = make_entry(row, 40)
    search_entry.pack(side="left", ipady=3)

    result_frame = tk.Frame(body, bg=colors["bg"])

    def do_search(event=None):
        for widget in result_frame.winfo_children():
            widget.destroy()

        name = search_entry.get()
        if name.strip() == "":
            make_label(result_frame, "Please type a name.", 10, True).pack(pady=14)
            return

        matches = records.search_all(name)

        if len(matches) == 0:
            make_label(result_frame, "Record Not Found", 10, True).pack(pady=14)
            return

        if len(matches) == 1:
            count_text = "1 record found"
        else:
            count_text = str(len(matches)) + " records found"
        make_label(result_frame, count_text, 10, False, "muted").pack(pady=(12, 6))

        table_frame, table, row_map = make_table(result_frame, 10, matches)
        table_frame.pack()

    search_entry.bind("<Return>", do_search)
    make_button(row, "Search", do_search).pack(side="left", padx=(8, 0))
    result_frame.pack()


def show_display_all():
    view["name"] = "display"
    body = new_page(True)

    make_label(body, "All Records", 18, True, "text", "bg", True).pack(pady=(10, 12))

    all_records = records.get_all()

    table_frame, table, row_map = make_table(body, 10, all_records)
    table_frame.pack(padx=20)

    if len(all_records) == 0:
        make_label(body, "No records yet.", 11, False, "muted").pack(pady=10)


def show_update():
    view["name"] = "update"
    body = new_page(True)
    colors = theme["colors"]

    make_label(body, "Update Record", 16, True).pack(pady=(10, 4))
    make_label(body, "Type a book or borrower name, then press Enter", 10, False, "muted").pack(pady=(0, 10))

    row = tk.Frame(body, bg=colors["bg"])
    row.pack()

    name_entry = make_entry(row, 40)
    name_entry.pack(side="left", ipady=3)

    result_frame = tk.Frame(body, bg=colors["bg"])
    editor_frame = tk.Frame(body, bg=colors["bg"])

    def open_editor(found):
        for widget in editor_frame.winfo_children():
            widget.destroy()

        make_label(editor_frame, "Edit Record", 14, True).grid(
            row=0, column=0, columnspan=2, pady=(14, 6))

        make_label(editor_frame, "Book Name", 9, False, "muted").grid(row=1, column=0, sticky="w", padx=14)
        book_entry = make_entry(editor_frame, 28)
        book_entry.insert(0, found.book_name)
        book_entry.grid(row=2, column=0, padx=14, pady=(2, 8), ipady=3)

        make_label(editor_frame, "Borrower Name", 9, False, "muted").grid(row=1, column=1, sticky="w", padx=14)
        borrower_entry = make_entry(editor_frame, 28)
        borrower_entry.insert(0, found.borrower_name)
        borrower_entry.grid(row=2, column=1, padx=14, pady=(2, 8), ipady=3)

        make_label(editor_frame, "Date Borrowed", 9, False, "muted").grid(row=3, column=0, sticky="w", padx=14)
        borrowed_entry = make_entry(editor_frame, 28, "", True)
        borrowed_entry.insert(0, found.date_borrowed)
        borrowed_entry.grid(row=4, column=0, padx=14, pady=(2, 8), ipady=3)

        make_label(editor_frame, "Date Returned", 9, False, "muted").grid(row=3, column=1, sticky="w", padx=14)
        returned_entry = make_entry(editor_frame, 28, "", True)
        returned_entry.insert(0, found.date_returned)
        returned_entry.grid(row=4, column=1, padx=14, pady=(2, 8), ipady=3)

        status_label = make_label(editor_frame, "", 10, True, "muted")
        status_label.grid(row=5, column=0, columnspan=2, pady=(4, 0))
        status_label.configure(text="Status: " + get_status(found) + "     |     Last Updated: " + get_last_updated(found))

        message_label = make_label(editor_frame, "", 10, True)

        def save_changes():
            found.book_name = book_entry.get()
            found.borrower_name = borrower_entry.get()
            found.date_borrowed = format_date(borrowed_entry.get())
            found.date_returned = format_date(returned_entry.get())
            borrowed_entry.delete(0, tk.END)
            borrowed_entry.insert(0, found.date_borrowed)
            returned_entry.delete(0, tk.END)
            returned_entry.insert(0, found.date_returned)
            found.last_updated = datetime.now().strftime("%b %d, %Y %I:%M %p")
            status_label.configure(text="Status: " + get_status(found) + "     |     Last Updated: " + get_last_updated(found))
            message_label.configure(text="Record Updated")

        make_button(editor_frame, "Save Changes", save_changes).grid(
            row=6, column=0, columnspan=2, pady=(8, 4))
        message_label.grid(row=7, column=0, columnspan=2, pady=(0, 4))

    def do_find(event=None):
        for widget in result_frame.winfo_children():
            widget.destroy()
        for widget in editor_frame.winfo_children():
            widget.destroy()

        name = name_entry.get()
        if name.strip() == "":
            make_label(result_frame, "Please type a name.", 10, True).pack(pady=14)
            return

        matches = records.search_all(name)

        if len(matches) == 0:
            make_label(result_frame, "Record Not Found", 10, True).pack(pady=14)
            return

        if len(matches) == 1:
            open_editor(matches[0])
            return

        count_text = str(len(matches)) + " records found. Select one and click Edit."
        make_label(result_frame, count_text, 10, False, "muted").pack(pady=(12, 6))

        table_frame, table, row_map = make_table(result_frame, 4, matches)
        table_frame.pack()

        select_message = make_label(result_frame, "", 10, True)

        def edit_selected():
            chosen = table.selection()
            if len(chosen) == 0:
                select_message.configure(text="Select a record first.")
                return
            select_message.configure(text="")
            open_editor(row_map[chosen[0]])

        def on_double_click(event):
            edit_selected()

        table.bind("<Double-1>", on_double_click)
        make_button(result_frame, "Edit", edit_selected).pack(pady=(8, 2))
        select_message.pack()

    name_entry.bind("<Return>", do_find)
    make_button(row, "Find", do_find).pack(side="left", padx=(8, 0))
    result_frame.pack()
    editor_frame.pack()


def exit_program():
    root.destroy()


def show_current_view():
    if view["name"] == "add":
        show_add()
    elif view["name"] == "search":
        show_search()
    elif view["name"] == "display":
        show_display_all()
    elif view["name"] == "update":
        show_update()
    else:
        show_home()


def apply_theme():
    colors = theme["colors"]

    root.configure(bg=colors["bg"])
    header_frame.configure(bg=colors["bg"])
    title_box.configure(bg=colors["bg"])
    title_label.configure(bg=colors["bg"], fg=colors["text"])
    subtitle_label.configure(bg=colors["bg"], fg=colors["muted"])
    line_frame.configure(bg=colors["border"])
    content_frame.configure(bg=colors["bg"])

    theme_button.configure(bg=colors["button_bg"], fg=colors["button_fg"],
                           activebackground=colors["button_bg"],
                           activeforeground=colors["button_fg"])
    if theme["name"] == "dark":
        theme_button.configure(text="Light Mode")
    else:
        theme_button.configure(text="Dark Mode")

    style.configure("Treeview", background=colors["card"], fieldbackground=colors["card"],
                    foreground=colors["text"], rowheight=28, font=(FONT, 10))
    style.configure("Treeview.Heading", background=colors["button_bg"],
                    foreground=colors["button_fg"], font=(FONT, 10, "bold"))
    style.map("Treeview", background=[("selected", colors["button_bg"])],
              foreground=[("selected", colors["button_fg"])])

    show_current_view()


def toggle_theme():
    if theme["name"] == "dark":
        theme["name"] = "light"
        theme["colors"] = LIGHT
    else:
        theme["name"] = "dark"
        theme["colors"] = DARK
    apply_theme()


style = ttk.Style()
style.theme_use("clam")

header_frame = tk.Frame(root)
header_frame.pack(fill="x", padx=25, pady=(18, 8))

title_box = tk.Frame(header_frame)
title_box.pack(side="left")

title_label = tk.Label(title_box, text="LibTrack", font=(FONT, 22, "bold"))
title_label.pack(anchor="w")

subtitle_label = tk.Label(title_box, text="Library Borrow Records", font=(FONT, 10))
subtitle_label.pack(anchor="w")

theme_button = tk.Button(header_frame, text="Light Mode", font=(FONT, 10),
                         relief="raised", bd=2, padx=14, pady=3, cursor="hand2",
                         command=toggle_theme)
theme_button.pack(side="right")

line_frame = tk.Frame(root, height=1)
line_frame.pack(fill="x", padx=25)

content_frame = tk.Frame(root)
content_frame.pack(fill="both", expand=True, padx=25, pady=15)

apply_theme()

root.mainloop()