import flet as ft
import sqlite3
import os
from datetime import datetime
import csv

DB_PATH = "defects_offline.db"
PHOTO_DIR = "photos_offline"

os.makedirs(PHOTO_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            object_name TEXT,
            location TEXT,
            element TEXT,
            defect_type TEXT,
            params TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()


def main(page: ft.Page):
    init_db()
    page.title = "Журнал обследования"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # Поля ввода
    txt_object = ft.TextField(label="Объект / Адрес", hint_text="ул. Ленина, 10")
    txt_location = ft.TextField(label="Локация", hint_text="Оси А-Б / 2 этаж")

    dd_element = ft.Dropdown(
        label="Конструктивный элемент",
        options=[
            ft.dropdown.Option("Фундамент"),
            ft.dropdown.Option("Стена / Перегородка"),
            ft.dropdown.Option("Колонна"),
            ft.dropdown.Option("Балка / Ригель"),
            ft.dropdown.Option("Плита перекрытия"),
            ft.dropdown.Option("Кровля"),
        ],
        value="Фундамент"
    )

    dd_defect = ft.Dropdown(
        label="Тип дефекта",
        options=[
            ft.dropdown.Option("Трещина"),
            ft.dropdown.Option("Скол бетона"),
            ft.dropdown.Option("Коррозия арматуры"),
            ft.dropdown.Option("Высолы / Протечка"),
            ft.dropdown.Option("Прогиб / Деформация"),
        ],
        value="Трещина"
    )

    txt_params = ft.TextField(
        label="Замеры и параметры",
        multiline=True,
        hint_text="Раскрытие 0.8мм, длина 1.2м"
    )

    dd_category = ft.Dropdown(
        label="Категория состояния",
        options=[
            ft.dropdown.Option("Исправное"),
            ft.dropdown.Option("Работоспособное"),
            ft.dropdown.Option("Ограниченно-работоспособное"),
            ft.dropdown.Option("Аварийное"),
        ],
        value="Работоспособное"
    )

    status_text = ft.Text(value="", color="green")

    def save_defect(e):
        if not txt_object.value or not txt_location.value:
            status_text.value = "Заполните 'Объект' и 'Локацию'!"
            status_text.color = "red"
            page.update()
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO defects (timestamp, object_name, location, element, defect_type, params, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, txt_object.value, txt_location.value, dd_element.value, dd_defect.value, txt_params.value,
              dd_category.value))
        conn.commit()
        conn.close()

        status_text.value = "Успешно сохранено локально!"
        status_text.color = "green"
        txt_params.value = ""
        page.update()

    def export_data(e):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM defects")
        rows = c.fetchall()
        conn.close()

        export_file = f"defects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(export_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['ID', 'Дата/Время', 'Объект', 'Локация', 'Элемент', 'Дефект', 'Параметры', 'Категория'])
            writer.writerows(rows)

        status_text.value = f"Выгружено в файл: {export_file}"
        status_text.color = "blue"
        page.update()

    btn_save = ft.ElevatedButton("💾 Сохранить в память телефона", on_click=save_defect)
    btn_export = ft.OutlinedButton("📥 Экспорт ведомости (CSV/Excel)", on_click=export_data)

    page.add(
        ft.Text("🏗️ Полевой журнал (Офлайн)", size=22, weight=ft.FontWeight.BOLD),
        txt_object,
        txt_location,
        dd_element,
        dd_defect,
        txt_params,
        dd_category,
        btn_save,
        status_text,
        ft.Divider(),
        btn_export
    )


ft.app(target=main)