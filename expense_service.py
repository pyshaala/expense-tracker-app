from expense_db import get_connection
import pandas as pd


# --------------------------------
# ADD EXPENSE
# --------------------------------

def add_expense(data):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO expenses (

        name, date, amount,

        category, subcategory, bucket,

        spent_by, payment_mode,

        notes, other_income, email
    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (

        data["name"],
        data["date"],
        float(data["amount"]),

        data["category"],
        data["subcategory"],
        data["bucket"],

        data["spent_by"],
        data["payment_mode"],

        data["notes"],
        float(data["other_income"]),

        data["email"]
    ))

    conn.commit()
    conn.close()


# --------------------------------
# GET USER EXPENSES (FOR DASHBOARD)
# --------------------------------

def get_user_expenses(email):

    conn = get_connection()

    query = """
    SELECT

        id,

        name, date, amount,

        category, subcategory, bucket,

        spent_by, payment_mode,

        notes, other_income

    FROM expenses

    WHERE email = ?

    ORDER BY date DESC
    """

    df = pd.read_sql(query, conn, params=(email,))

    conn.close()


    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


# --------------------------------
# DELETE EXPENSE (BY ID)
# --------------------------------

def delete_expense(expense_id, email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM expenses
        WHERE id=? AND email=?
    """, (expense_id, email))

    conn.commit()

    rows = cur.rowcount   # how many rows deleted

    conn.close()

    return rows > 0

