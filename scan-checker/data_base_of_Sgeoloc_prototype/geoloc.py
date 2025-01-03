import sqlite3

def clear_data_from_table():
    try:
        # Подключаемся к базе данных
        db = sqlite3.connect("qr_device_data.db")
        cursor = db.cursor()

        # Очищаем все данные из таблицы, не удаляя таблицу
        cursor.execute("DELETE FROM scan_records")
        db.commit()

        print("Все данные из таблицы успешно удалены.")
    except sqlite3.Error as err:
        print(f"Ошибка при очистке данных: {err}")
    finally:
        if db:
            cursor.close()
            db.close()

# Вызов функции очистки данных
clear_data_from_table()