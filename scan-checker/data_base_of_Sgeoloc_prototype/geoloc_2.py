import tkinter as tk
from tkinter import ttk
import sqlite3

def create_database_and_table():
    db = sqlite3.connect("qr_device_data.db")
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_model TEXT NOT NULL,
        location TEXT NOT NULL,
        qr_code_data TEXT NOT NULL,
        scan_time_str TEXT NOT NULL
    )
    """)
    db.commit()
    db.close()

def fetch_data():
    db = sqlite3.connect("qr_device_data.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM scan_records")
    rows = cursor.fetchall()
    db.close()
    return rows

def populate_table(tree):
    for row in fetch_data():
        tree.insert("", "end", values=row)

def create_gui():
    window = tk.Tk()
    window.title("QR Records Viewer")

    # Таблица с записями
    columns = ("id", "device_model", "location", "qr_code_data", "scan_time_str")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    tree.heading("id", text="ID")
    tree.heading("device_model", text="Device Model")
    tree.heading("location", text="Location")
    tree.heading("qr_code_data", text="QR Data")
    tree.heading("scan_time_str", text="Scan Time")
    tree.pack(fill="both", expand=True)

    populate_table(tree)
    window.mainloop()

create_database_and_table()
create_gui()







# ОСНОВА ГЕОЛОС_3_СКАННИНГ