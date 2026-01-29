import sqlite3
import os


DB_PATH = "data/expenses.db"


def get_connection():

    os.makedirs("data", exist_ok=True)

    return sqlite3.connect(DB_PATH)


def create_expense_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,
        date TEXT,
        amount REAL,

        category TEXT,
        subcategory TEXT,
        bucket TEXT,

        spent_by TEXT,
        payment_mode TEXT,

        notes TEXT,

        other_income REAL DEFAULT 0,

        email TEXT
    )
    """)

    conn.commit()
    conn.close()
