import sqlite3
import cv2
import os
import platform
import subprocess
from pyzbar.pyzbar import decode
import platform
import geocoder  
from PIL import Image, ImageTk
import tkinter as tk
import threading

# Создаем глобальную переменную cap для управления видеопотоком
cap = None
running = False

def create_database_and_table():
    try:
        db = sqlite3.connect("qr_device_data.db")
        cursor = db.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scan_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_model TEXT NOT NULL,
            location TEXT NOT NULL,
            qr_code_data TEXT NOT NULL,
            scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            device_characteristics TEXT NOT NULL

        );
        """
        cursor.execute(create_table_query)
        db.commit()
    except sqlite3.Error as err:
        print(f"Ошибка: {err}")
    finally:
        if db:
            cursor.close()
            db.close()

def get_phone_model():
    os_name = platform.system()
    
    if os_name == "Windows":
        try:
            # Используем WMI для получения модели устройства на Windows
            import wmi
            computer = wmi.WMI()
            for system in computer.Win32_ComputerSystem():
                return f"{system.Manufacturer} {system.Model}"
        except ImportError:
            return "Windows Device (модуль WMI не установлен)"
        except Exception:
            return "Не удалось определить модель на Windows"
    
    elif os_name == "Linux":
        try:
            # Получаем модель устройства на Linux через sysfs
            model = open("/sys/devices/virtual/dmi/id/product_name").read().strip()
            manufacturer = open("/sys/devices/virtual/dmi/id/sys_vendor").read().strip()
            return f"{manufacturer} {model}"
        except Exception:
            return "Linux Device (не удалось определить модель)"
    
    elif os_name == "Darwin":  # macOS
        try:
            # Используем sysctl для получения модели устройства на macOS
            model = subprocess.check_output(["sysctl", "-n", "hw.model"]).strip().decode()
            return f"Mac Device {model}"
        except Exception:
            return "Mac Device (не удалось определить модель)"
    
    else:
        return f"{os_name} Device (модель неизвестна)"
    # return platform.system() + " Device"

def get_location():
    g = geocoder.ip('me')
    if g.ok:
        latitude, longitude = g.latlng
        return f"{latitude:.6f}, {longitude:.6f}"
    return "Не удалось определить местоположение"

def save_scan_data(device_model, location, qr_code_data, device_characteristics):
    # try:
    #     db = sqlite3.connect("qr_device_data.db")
    #     cursor = db.cursor()
    #     sql = """
    #     INSERT INTO scan_records (device_model, location, qr_code_data, device_characteristics)
    #     VALUES (?, ?, ?, ?)
    #     """
    #     cursor.execute(sql, (device_model, location, qr_code_data, device_characteristics))
    #     db.commit()
    # except sqlite3.Error as err:
    #     print(f"Ошибка при записи в базу данных: {err}")
    # finally:
    #     if db:
    #         cursor.close()
    #         db.close()
    try:
        db = sqlite3.connect("qr_device_data.db")
        cursor = db.cursor()

        # Проверка существования записи с тем же QR-кодом
        cursor.execute("SELECT id FROM scan_records WHERE qr_code_data = ?", (qr_code_data,))
        existing_record = cursor.fetchone()

        # Запись в базу данных, если такой QR-код еще не существует
        if not existing_record:
            sql = """
            INSERT INTO scan_records (device_model, location, qr_code_data, device_characteristics)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, (device_model, location, qr_code_data, device_characteristics))
            db.commit()
        else:
            print("QR-код уже существует в базе данных. Запись не добавлена.")
    except sqlite3.Error as err:
        print(f"Ошибка при записи в базу данных: {err}")
    finally:
        if db:
            cursor.close()
            

def scan_qr_code(window, label_output):
    global cap, running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        tk.messagebox.showerror("Ошибка", "Не удается открыть камеру.")
        running = False
        return

    device_model = get_phone_model()
    location = get_location()
    running = True

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_code_data = obj.data.decode('utf-8')
            device_characteristics = "OS: Undefined -- definitely"
            save_scan_data(device_model, location, qr_code_data, device_characteristics)

            details = f"Модель устройства: {device_model}\nМестоположение: {location}\nQR-данные: {qr_code_data}\nХарактеристики устройства: {device_characteristics}"
            label_output.config(text=details)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = ImageTk.PhotoImage(img)
        label_video.config(image=img)
        label_video.image = img

        window.update_idletasks()

    cap.release()
    cv2.destroyAllWindows()
    label_video.config(image="")
    label_output.config(text="Детали сканирования будут отображены здесь.")

def start_scan(window, label_output):
    global running
    if not running:
        threading.Thread(target=scan_qr_code, args=(window, label_output), daemon=True).start()

def stop_scan():
    global running, cap
    running = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

def create_gui():
    window = tk.Tk()
    window.title("QR Code Scanner")
    global label_video
    label_video = tk.Label(window)
    label_video.pack()
    button_start = tk.Button(window, text="Начать сканирование", command=lambda: start_scan(window, label_output))
    button_start.pack(pady=10)
    button_stop = tk.Button(window, text="Завершить сканирование", command=stop_scan)
    button_stop.pack(pady=10)
    label_output = tk.Label(window, text="Детали сканирования будут отображены здесь.", justify="left", padx=10, pady=10)
    label_output.pack()
    window.mainloop()

create_database_and_table()
create_gui()



















# import sqlite3
# import cv2
# from pyzbar.pyzbar import decode
# import platform
# import random
# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk
# import threading

# # Функция для создания базы данных и таблицы
# def create_database_and_table():
#     try:
#         # Подключаемся к базе данных SQLite (если она не существует, она будет создана)
#         db = sqlite3.connect("qr_device_data.db")  # Создается файл базы данных .db
#         cursor = db.cursor()

#         # Создаем таблицу, если она не существует
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS scan_records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             device_model TEXT NOT NULL,
#             location TEXT NOT NULL,
#             qr_code_data TEXT NOT NULL,
#             scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             device_characteristics TEXT NOT NULL
#         );
#         """
#         cursor.execute(create_table_query)
#         db.commit()
#         print("База данных и таблица успешно созданы!")

#     except sqlite3.Error as err:
#         print(f"Ошибка: {err}")
#     finally:
#         if db:
#             cursor.close()
#             db.close()

# # Функция для получения информации о модели устройства
# def get_phone_model():
#     return platform.system() + " Device"

# # Функция для получения случайного местоположения
# def get_location():
#     latitude = random.uniform(-90, 90)
#     longitude = random.uniform(-180, 180)
#     return f"{latitude:.6f}, {longitude:.6f}"

# # Функция для записи данных в базу данных SQLite
# def save_scan_data(device_model, location, qr_code_data, device_characteristics):
#     try:
#         db = sqlite3.connect("qr_device_data.db")
#         cursor = db.cursor()

#         sql = """
#         INSERT INTO scan_records (device_model, location, qr_code_data, device_characteristics)
#         VALUES (?, ?, ?, ?)
#         """
#         cursor.execute(sql, (device_model, location, qr_code_data, device_characteristics))
#         db.commit()
#         print("Данные успешно сохранены в базе данных.")

#     except sqlite3.Error as err:
#         print(f"Ошибка при записи в базу данных: {err}")
#     finally:
#         if db:
#             cursor.close()
#             db.close()

# # Функция для обработки сканирования QR-кодов
# def scan_qr_code(window, label_output):
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         messagebox.showerror("Ошибка", "Не удается открыть камеру.")
#         return

#     device_model = get_phone_model()
#     location = get_location()

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         decoded_objects = decode(frame)
#         for obj in decoded_objects:
#             qr_code_data = obj.data.decode('utf-8')
#             device_characteristics = "OS: Android 12, RAM: 4GB"

#             # Сохраняем данные в базу данных
#             save_scan_data(device_model, location, qr_code_data, device_characteristics)

#             # Обновляем текст в интерфейсе
#             details = f"Модель устройства: {device_model}\nМестоположение: {location}\nQR-данные: {qr_code_data}\nХарактеристики устройства: {device_characteristics}"
#             label_output.config(text=details)

#         # Показываем видеопоток
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         img = Image.fromarray(frame_rgb)
#         img = ImageTk.PhotoImage(img)
#         label_video.config(image=img)
#         label_video.image = img

#         window.update_idletasks()

#     cap.release()

# # Функция для начала сканирования
# def start_scan(window, label_output):
#     threading.Thread(target=scan_qr_code, args=(window, label_output), daemon=True).start()

# # Функция для завершения сканирования
# def stop_scan():
#     cv2.destroyAllWindows()

# # Функция для создания графического интерфейса
# def create_gui():
#     window = tk.Tk()
#     window.title("QR Code Scanner")

#     # Создаем метку для отображения видеопотока
#     global label_video
#     label_video = tk.Label(window)
#     label_video.pack()

#     # Кнопка для начала сканирования
#     button_start = tk.Button(window, text="Начать сканирование", command=lambda: start_scan(window, label_output))
#     button_start.pack(pady=10)

#     # Кнопка для завершения сканирования
#     button_stop = tk.Button(window, text="Завершить сканирование", command=stop_scan)
#     button_stop.pack(pady=10)

#     # Метка для вывода подробностей о сканировании
#     label_output = tk.Label(window, text="Детали сканирования будут отображены здесь.", justify="left", padx=10, pady=10)
#     label_output.pack()

#     window.mainloop()

# # Создание базы данных и таблицы
# create_database_and_table()

# # Создание графического интерфейса
# create_gui()







# import sqlite3
# import cv2
# from pyzbar.pyzbar import decode
# import platform
# import geocoder  
# from PIL import Image, ImageTk
# import tkinter as tk
# import threading

# def create_database_and_table():
#     try:
#         db = sqlite3.connect("qr_device_data.db")
#         cursor = db.cursor()
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS scan_records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             device_model TEXT NOT NULL,
#             location TEXT NOT NULL,
#             qr_code_data TEXT NOT NULL,
#             scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             device_characteristics TEXT NOT NULL
#         );
#         """
#         cursor.execute(create_table_query)
#         db.commit()
#     except sqlite3.Error as err:
#         print(f"Ошибка: {err}")
#     finally:
#         if db:
#             cursor.close()
#             db.close()

# def get_phone_model():
#     return platform.system() + " Device"

# def get_location():
#     """
#     Функция для получения точного местоположения.
#     Использует geocoder для определения широты и долготы.
#     """
#     g = geocoder.ip('me')  # Получение координат по IP (интернет-подключение требуется)
#     if g.ok:
#         latitude, longitude = g.latlng
#         return f"{latitude:.6f}, {longitude:.6f}"
#     return "Не удалось определить местоположение"

# def save_scan_data(device_model, location, qr_code_data, device_characteristics):
#     try:
#         db = sqlite3.connect("qr_device_data.db")
#         cursor = db.cursor()
#         sql = """
#         INSERT INTO scan_records (device_model, location, qr_code_data, device_characteristics)
#         VALUES (?, ?, ?, ?)
#         """
#         cursor.execute(sql, (device_model, location, qr_code_data, device_characteristics))
#         db.commit()
#     except sqlite3.Error as err:
#         print(f"Ошибка при записи в базу данных: {err}")
#     finally:
#         if db:
#             cursor.close()
#             db.close()

# def scan_qr_code(window, label_output):
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         tk.messagebox.showerror("Ошибка", "Не удается открыть камеру.")
#         return

#     device_model = get_phone_model()
#     location = get_location()

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         decoded_objects = decode(frame)
#         for obj in decoded_objects:
#             qr_code_data = obj.data.decode('utf-8')
#             device_characteristics = "OS: Android 12, RAM: 4GB"
#             save_scan_data(device_model, location, qr_code_data, device_characteristics)

#             details = f"Модель устройства: {device_model}\nМестоположение: {location}\nQR-данные: {qr_code_data}\nХарактеристики устройства: {device_characteristics}"
#             label_output.config(text=details)

#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         img = Image.fromarray(frame_rgb)
#         img = ImageTk.PhotoImage(img)
#         label_video.config(image=img)
#         label_video.image = img

#         window.update_idletasks()

#     cap.release()
#     label_video.config(image="")
#     label_output.config(text="Детали сканирования будут отображены здесь.")

# def start_scan(window, label_output):
#     threading.Thread(target=scan_qr_code, args=(window, label_output), daemon=True).start()

# def stop_scan():
#     global stop_event
#     stop_event.set()
#     cv2.destroyAllWindows()

# def create_gui():
#     window = tk.Tk()
#     window.title("QR Code Scanner")
#     global label_video
#     label_video = tk.Label(window)
#     label_video.pack()
#     button_start = tk.Button(window, text="Начать сканирование", command=lambda: start_scan(window, label_output))
#     button_start.pack(pady=10)
#     button_stop = tk.Button(window, text="Завершить сканирование", command=stop_scan)
#     button_stop.pack(pady=10)
#     label_output = tk.Label(window, text="Детали сканирования будут отображены здесь.", justify="left", padx=10, pady=10)
#     label_output.pack()
#     window.mainloop()


# stop_event = threading.Event()

# create_database_and_table()
# create_gui()







