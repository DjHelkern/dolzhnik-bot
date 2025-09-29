import sqlite3
import threading
from config import DATABASE_NAME

# Создаем thread-local хранилище для соединений
thread_local = threading.local()


def get_conn():
    """Возвращает соединение с БД, уникальное для каждого потока."""
    if not hasattr(thread_local, "conn"):
        # check_same_thread=False нужен для pyTelegramBotAPI, т.к. он использует потоки
        thread_local.conn = sqlite3.connect(
            DATABASE_NAME, check_same_thread=False)
    return thread_local.conn


def init_db():
    """Инициализирует базу данных и создает таблицу, если её нет."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            item TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("Database initialized.")


def add_debt(name: str, item: str):
    """Добавляет новый долг в БД."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO debts (name, item) VALUES (?, ?)",
        (name.lower(), item)
    )
    conn.commit()


def get_debts_by_name(name: str) -> list:
    """Получает список долгов для конкретного человека."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, item FROM debts WHERE name = ? ORDER BY created_at ASC",
        (name.lower(),)
    )
    return cursor.fetchall()


def get_all_debts() -> list:
    """Получает все долги, сгруппированные по имени."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, item FROM debts ORDER BY name, created_at ASC")

    # Группируем долги по имени
    debts_dict = {}
    for name, item in cursor.fetchall():
        if name not in debts_dict:
            debts_dict[name] = []
        debts_dict[name].append(item)
    return debts_dict


def delete_debt_by_id(debt_id: int) -> bool:
    """Удаляет долг по его уникальному ID."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
    conn.commit()
    # aвто-инкремент rowcount вернет 1, если строка была удалена
    return cursor.rowcount > 0
