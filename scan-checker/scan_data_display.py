import sqlite3
import tkinter as tk
from tkinter import ttk

# Функция для получения всех записей из базы данных
def get_all_scans():
    conn = sqlite3.connect('scan_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY scanned_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Функция для создания главного окна с таблицей
def create_gui():
    # Создание главного окна
    window = tk.Tk()
    window.title("Таблица сканирований QR-кодов")
    
    # Создание таблицы с помощью ttk.Treeview
    tree = ttk.Treeview(window, columns=("ID", "Время", "IP-адрес", "Модель устройства", "Местоположение", "QR-данные", "URL назначения"), show="headings")
    
    # Настройка заголовков
    tree.heading("ID", text="ID")
    tree.heading("Время", text="Время сканирования")
    tree.heading("IP-адрес", text="IP-адрес")
    tree.heading("Модель устройства", text="Модель устройства")
    tree.heading("Местоположение", text="Местоположение")
    tree.heading("QR-данные", text="QR-данные")
    tree.heading("URL назначения", text="URL назначения")

    # Устанавливаем ширину столбцов
    tree.column("ID", width=30)
    tree.column("Время", width=150)
    tree.column("IP-адрес", width=150)
    tree.column("Модель устройства", width=150)
    tree.column("Местоположение", width=150)
    tree.column("QR-данные", width=200)
    tree.column("URL назначения", width=200)

    # Добавление данных в таблицу
    rows = get_all_scans()  # Получаем данные из базы
    for row in rows:
        tree.insert("", tk.END, values=row)

    # Размещение таблицы в окне
    tree.pack(padx=20, pady=20)

    # Кнопка для обновления таблицы
    def refresh():
        for item in tree.get_children():
            tree.delete(item)
        rows = get_all_scans()  # Получаем обновленные данные
        for row in rows:
            tree.insert("", tk.END, values=row)

    button_refresh = tk.Button(window, text="Обновить", command=refresh)
    button_refresh.pack(pady=10)

    # Запуск основного цикла
    window.mainloop()

if __name__ == "__main__":
    create_gui()  # Создание и запуск графического интерфейса
