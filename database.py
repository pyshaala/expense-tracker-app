import sqlite3
from pathlib import Path


# -----------------------------------------
# DATABASE PATH
# -----------------------------------------

DB_PATH = Path("data/users.db")


# -----------------------------------------
# CONNECTION
# -----------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------------------
# INIT DB
# -----------------------------------------

def init_db():

    DB_PATH.parent.mkdir(exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,

            phone TEXT,
            dob TEXT,

            salary REAL,

            gender TEXT,
            job TEXT,

            address TEXT,

            pic TEXT,
            notify TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT,
            name TEXT,

            date TEXT,

            amount REAL,

            category TEXT,
            subcategory TEXT,

            bucket TEXT,

            spent_by TEXT,

            payment_mode TEXT,

            notes TEXT,

            other_income REAL
        )
        """)


    conn.commit()
    conn.close()


# -----------------------------------------
# CREATE USER
# -----------------------------------------

def insert_user(data: dict):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO users
            (name,email,password,phone,dob,salary,
             gender,job,address,pic,notify)

            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (

            data["name"],
            data["email"],
            data["password"],
            data["phone"],
            data["dob"],
            data["salary"],

            data["gender"],
            data["job"],
            data["address"],

            data.get("pic", ""),
            data.get("notify", "21:00")

        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# -----------------------------------------
# GET USER BY EMAIL
# -----------------------------------------

def get_user_by_email(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM users
        WHERE email=?
    """, (email,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return format_user(row)


# -----------------------------------------
# UPDATE PROFILE
# -----------------------------------------

def update_user_profile(
    email,
    name,
    phone,
    dob,
    salary,
    gender,
    job,
    address
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users

        SET
            name=?,
            phone=?,
            dob=?,
            salary=?,
            gender=?,
            job=?,
            address=?

        WHERE email=?
    """, (

        name,
        phone,
        dob,
        salary,
        gender,
        job,
        address,

        email
    ))

    conn.commit()
    conn.close()


# -----------------------------------------
# UPDATE PASSWORD
# -----------------------------------------

def update_password(email, new_pass):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET password=?
        WHERE email=?
    """, (new_pass, email))

    conn.commit()
    conn.close()


# -----------------------------------------
# FORMAT USER
# -----------------------------------------

def format_user(row):

    return {

        "id": row[0],

        "name": row[1],
        "email": row[2],
        "password": row[3],

        "phone": row[4],
        "dob": row[5],

        "salary": row[6],

        "gender": row[7],
        "job": row[8],

        "address": row[9],

        "pic": row[10],
        "notify": row[11]
    }

# -----------------------------------------
# GET USER COUNT
# -----------------------------------------

def get_user_count():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")

    count = cur.fetchone()[0]

    conn.close()

    return count
