import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

DB_NAME = "library_logsheet_v2.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        program_id TEXT PRIMARY KEY,
        program_name TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS purposes (
        purpose_id INTEGER PRIMARY KEY AUTOINCREMENT,
        purpose_name TEXT NOT NULL UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS library_sections (
        section_id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_name TEXT NOT NULL UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS library_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        program TEXT NOT NULL,
        purpose TEXT NOT NULL,
        section TEXT NOT NULL,
        log_date TEXT NOT NULL
    )
""")

cursor.executemany(
    "INSERT OR IGNORE INTO programs (program_id, program_name) VALUES (?, ?)",
    [
        ("BSIE", "Bachelor of Science in Industrial Engineering"),
        ("BSIT", "Bachelor of Science in Information Technology"),
    ],
)

cursor.executemany(
    "INSERT OR IGNORE INTO purposes (purpose_name) VALUES (?)",
    [
        ("Study",),
        ("Research",),
        ("Borrow / Return",),
        ("Computer / Printing",),
    ],
)

cursor.executemany(
    "INSERT OR IGNORE INTO library_sections (section_name) VALUES (?)",
    [
        ("General Reference",),
        ("Filipiniana",),
        ("Periodicals",),
        ("Quiet Study Zone",),
    ],
)
conn.commit()


BG_BLUSH = "#FFF0F5"
BG_ROSE = "#FADADD"
ACCENT_BERRY = "#C2185B"
ACCENT_DUSTY = "#D87093"
ACCENT_SOFT = "#F48FB1"
TEXT_DARK = "#222222"
WHITE = "#FFFFFF"

root = tk.Tk()
root.title("Library Logsheet System")
root.configure(bg=BG_BLUSH, padx=14, pady=12)

program_var = tk.StringVar(root, value="")
purpose_var = tk.StringVar(root, value="")
section_var = tk.StringVar(root, value="")


def populate_menu(menubutton, var, options):
    menu = menubutton.menu
    menu.delete(0, tk.END)
    for opt in options:
        menu.add_command(
            label=opt,
            command=lambda val=opt, v=var, btn=menubutton: select_option(btn, v, val),
        )


def select_option(menubutton, var, value):
    var.set(value)
    menubutton.configure(text=f"{value}   ▾")
    menubutton.update_idletasks()


def reset_dropdown(menubutton, var):
    var.set("")
    menubutton.configure(text="Select...   ▾")


def load_programs():
    options = ["BSIE", "BSIT"]
    cursor.execute("SELECT program_id FROM programs ORDER BY program_id")
    for row in cursor.fetchall():
        if row[0] and row[0] not in options:
            options.append(row[0])
    populate_menu(drop_program, program_var, options)


def load_purposes():
    cursor.execute("SELECT purpose_name FROM purposes ORDER BY purpose_name")
    options = [row[0] for row in cursor.fetchall() if row[0]]
    populate_menu(drop_purpose, purpose_var, options)


def load_sections():
    cursor.execute("SELECT section_name FROM library_sections ORDER BY section_name")
    options = [row[0] for row in cursor.fetchall() if row[0]]
    populate_menu(drop_section, section_var, options)


def add_log():
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()
    program = program_var.get().strip()
    purpose = purpose_var.get().strip()
    section = section_var.get().strip()
    log_date = entry_date.get().strip()

    if not student_id or not student_name or not program or not purpose or not section or not log_date:
        messagebox.showwarning(
            "Missing Fields",
            "Please fill in Student ID, Student Name, Program, Purpose, Section, and Date.",
        )
        return

    try:
        cursor.execute(
            """
            INSERT INTO library_logs (student_id, student_name, program, purpose, section, log_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, student_name, program, purpose, section, log_date),
        )
        conn.commit()
        messagebox.showinfo("Success", "Library log entry added.")
        clear_fields()
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Failed to add log:\n{err}")


def update_log():
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()
    program = program_var.get().strip()
    purpose = purpose_var.get().strip()
    section = section_var.get().strip()
    log_date = entry_date.get().strip()

    if not student_id:
        messagebox.showwarning("Missing Student ID", "Enter or search a Student ID first to update its latest log.")
        return

    if not student_name or not program or not purpose or not section or not log_date:
        messagebox.showwarning("Missing Fields", "Please complete all fields before updating.")
        return

    cursor.execute(
        "SELECT log_id FROM library_logs WHERE student_id = ? ORDER BY log_id DESC LIMIT 1",
        (student_id,),
    )
    row = cursor.fetchone()
    if not row:
        messagebox.showinfo("Not Found", f"No log record found for Student ID '{student_id}'.")
        return

    if not messagebox.askyesno("Confirm Update", f"Update the latest log for Student ID '{student_id}'?"):
        return

    try:
        cursor.execute(
            """
            UPDATE library_logs
            SET student_name = ?, program = ?, purpose = ?, section = ?, log_date = ?
            WHERE log_id = ?
            """,
            (student_name, program, purpose, section, log_date, row[0]),
        )
        conn.commit()
        messagebox.showinfo("Success", "Library log entry updated.")
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Failed to update log:\n{err}")


def search_log():
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()

    if not student_id and not student_name:
        messagebox.showwarning("Search Input Needed", "Enter a Student ID or Student Name to search.")
        return

    if student_id:
        cursor.execute(
            """
            SELECT student_id, student_name, program, purpose, section, log_date
            FROM library_logs
            WHERE student_id = ?
            ORDER BY log_id DESC LIMIT 1
            """,
            (student_id,),
        )
    else:
        cursor.execute(
            """
            SELECT student_id, student_name, program, purpose, section, log_date
            FROM library_logs
            WHERE student_name LIKE ?
            ORDER BY log_id DESC LIMIT 1
            """,
            (f"%{student_name}%",),
        )

    row = cursor.fetchone()
    if not row:
        messagebox.showinfo("Not Found", "No matching library log found.")
        return

    entry_id.delete(0, tk.END)
    entry_id.insert(0, row[0])

    entry_name.delete(0, tk.END)
    entry_name.insert(0, row[1])

    load_programs()
    select_option(drop_program, program_var, row[2])

    load_purposes()
    select_option(drop_purpose, purpose_var, row[3])

    load_sections()
    select_option(drop_section, section_var, row[4])

    entry_date.delete(0, tk.END)
    entry_date.insert(0, row[5])


def delete_log():
    student_id = entry_id.get().strip()
    if not student_id:
        messagebox.showwarning("Missing Student ID", "Enter or search a Student ID to delete its log.")
        return

    cursor.execute(
        "SELECT log_id FROM library_logs WHERE student_id = ? ORDER BY log_id DESC LIMIT 1",
        (student_id,),
    )
    row = cursor.fetchone()
    if not row:
        messagebox.showinfo("Not Found", f"No log record found for Student ID '{student_id}'.")
        return

    if not messagebox.askyesno("Confirm Delete", f"Delete the latest log for Student ID '{student_id}'?"):
        return

    try:
        cursor.execute("DELETE FROM library_logs WHERE log_id = ?", (row[0],))
        conn.commit()
        messagebox.showinfo("Success", "Library log entry deleted.")
        clear_fields()
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Failed to delete log:\n{err}")


def clear_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    reset_dropdown(drop_program, program_var)
    reset_dropdown(drop_purpose, purpose_var)
    reset_dropdown(drop_section, section_var)
    entry_date.delete(0, tk.END)
    entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))


def make_dropdown(parent, row):
    btn = tk.Menubutton(
        parent,
        text="Select...   ▾",
        bg=WHITE,
        fg=TEXT_DARK,
        activebackground=BG_ROSE,
        activeforeground=TEXT_DARK,
        font=("Arial", 12, "bold"),
        anchor="w",
        padx=8,
        pady=4,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=ACCENT_SOFT,
        highlightcolor=ACCENT_BERRY,
        cursor="hand2",
    )
    menu = tk.Menu(
        btn,
        tearoff=0,
        bg=WHITE,
        fg=TEXT_DARK,
        activebackground=ACCENT_SOFT,
        activeforeground=TEXT_DARK,
        font=("Arial", 11),
    )
    btn.configure(menu=menu)
    btn.menu = menu
    btn.grid(row=row, column=1, columnspan=4, padx=6, pady=6, sticky="ew")
    return btn


header = tk.Label(
    root,
    text="LIBRARY LOGSHEET",
    font=("Arial", 13, "bold"),
    bg=ACCENT_BERRY,
    fg=WHITE,
    pady=6,
)
header.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 10))

label_opts = {"bg": BG_BLUSH, "fg": "#4A152B", "font": ("Arial", 10, "bold")}
entry_opts = {
    "bg": WHITE,
    "fg": TEXT_DARK,
    "insertbackground": ACCENT_BERRY,
    "highlightthickness": 1,
    "highlightbackground": ACCENT_SOFT,
    "highlightcolor": ACCENT_BERRY,
    "relief": "flat",
    "font": ("Arial", 11),
}

tk.Label(root, text="Student ID:", **label_opts).grid(row=1, column=0, padx=6, pady=6, sticky="w")
entry_id = tk.Entry(root, width=32, **entry_opts)
entry_id.grid(row=1, column=1, columnspan=4, padx=6, pady=6, ipady=3, sticky="ew")

tk.Label(root, text="Student Name:", **label_opts).grid(row=2, column=0, padx=6, pady=6, sticky="w")
entry_name = tk.Entry(root, width=32, **entry_opts)
entry_name.grid(row=2, column=1, columnspan=4, padx=6, pady=6, ipady=3, sticky="ew")

tk.Label(root, text="Program:", **label_opts).grid(row=3, column=0, padx=6, pady=6, sticky="w")
drop_program = make_dropdown(root, 3)
load_programs()

tk.Label(root, text="Purpose:", **label_opts).grid(row=4, column=0, padx=6, pady=6, sticky="w")
drop_purpose = make_dropdown(root, 4)
load_purposes()

tk.Label(root, text="Section:", **label_opts).grid(row=5, column=0, padx=6, pady=6, sticky="w")
drop_section = make_dropdown(root, 5)
load_sections()

tk.Label(root, text="Date (YYYY-MM-DD):", **label_opts).grid(row=6, column=0, padx=6, pady=6, sticky="w")
entry_date = tk.Entry(root, width=32, **entry_opts)
entry_date.grid(row=6, column=1, columnspan=4, padx=6, pady=6, ipady=3, sticky="ew")
entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

btn_opts = {
    "width": 10,
    "bg": ACCENT_DUSTY,
    "fg": WHITE,
    "activebackground": ACCENT_BERRY,
    "activeforeground": WHITE,
    "font": ("Arial", 9, "bold"),
    "relief": "flat",
    "cursor": "hand2",
    "pady": 4,
}

tk.Button(root, text="Add", command=add_log, **btn_opts).grid(row=7, column=0, padx=4, pady=10)
tk.Button(root, text="Update", command=update_log, **btn_opts).grid(row=7, column=1, padx=4, pady=10)
tk.Button(root, text="Search", command=search_log, **btn_opts).grid(row=7, column=2, padx=4, pady=10)
tk.Button(root, text="Delete", command=delete_log, **btn_opts).grid(row=7, column=3, padx=4, pady=10)
tk.Button(root, text="Clear", command=clear_fields, **btn_opts).grid(row=7, column=4, padx=4, pady=10)

root.mainloop()
conn.close()
