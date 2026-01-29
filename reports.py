import os
import sqlite3
import pandas as pd
import smtplib
import matplotlib.pyplot as plt

from email.message import EmailMessage
from fpdf import FPDF
from datetime import datetime


# ---------------------------------------
# PATHS
# ---------------------------------------

BASE_DIR = os.getcwd()

DB_PATH = os.path.join(BASE_DIR, "data", "expenses.db")

REPORT_DIR = os.path.join(BASE_DIR, "data", "reports")
CHART_DIR = os.path.join(BASE_DIR, "data", "charts")

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)


# ---------------------------------------
# DB CONNECTION
# ---------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ---------------------------------------
# CLEAN TEXT (UNICODE SAFE)
# ---------------------------------------

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    # Replace common unicode
    text = text.replace("₹", "INR ")
    text = text.replace("➕", "+")
    text = text.replace("–", "-")

    return text.encode("latin-1", "ignore").decode("latin-1")


# ---------------------------------------
# LOAD EXPENSES FROM DB
# ---------------------------------------

def load_expenses(email):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM expenses
        WHERE email=?
        """,
        conn,
        params=(email,)
    )

    conn.close()

    return df


# ---------------------------------------
# FILTER MONTH
# ---------------------------------------

def filter_month(df, month, year):

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.dropna(subset=["date"])

    return df[
        (df["date"].dt.month == month) &
        (df["date"].dt.year == year)
    ]


# ---------------------------------------
# GENERATE CHARTS
# ---------------------------------------

def generate_charts(df, month, year):

    files = []


    # -------- PIE --------

    pie_path = os.path.join(
        CHART_DIR,
        f"pie_{month}_{year}.png"
    )

    cat = df.groupby("category")["amount"].sum()

    plt.figure(figsize=(6, 6))

    cat.plot.pie(autopct="%1.1f%%")

    plt.title("Category Distribution")

    plt.ylabel("")

    plt.tight_layout()

    plt.savefig(pie_path, dpi=150)

    plt.close()

    files.append(pie_path)


    # -------- LINE --------

    line_path = os.path.join(
        CHART_DIR,
        f"daily_{month}_{year}.png"
    )

    daily = df.groupby("date")["amount"].sum()

    plt.figure(figsize=(8, 4))

    daily.plot(marker="o")

    plt.title("Daily Spending")

    plt.xlabel("Date")

    plt.ylabel("Amount (INR)")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(line_path, dpi=150)

    plt.close()

    files.append(line_path)


    return files


# ---------------------------------------
# EXPORT CSV
# ---------------------------------------

def export_csv(df, month, year):

    name = os.path.join(
        REPORT_DIR,
        f"{month}_{year}.csv"
    )

    df.to_csv(name, index=False)

    return name


# ---------------------------------------
# EXPORT PDF
# ---------------------------------------

def export_pdf(df, charts, month, year, user_name):

    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()


    # ---------- TITLE ----------

    pdf.set_font("Arial", "B", 18)

    title = f"Expense Report - {month}/{year}"

    pdf.cell(0, 12, clean_text(title), ln=1, align="C")

    pdf.ln(5)


    # ---------- USER ----------

    pdf.set_font("Arial", "", 12)

    pdf.cell(
        0, 8,
        f"User: {clean_text(user_name)}",
        ln=1
    )

    pdf.cell(
        0, 8,
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        ln=1
    )

    pdf.ln(5)


    # ---------- SUMMARY ----------

    total = round(df["amount"].sum(), 2)
    count = len(df)

    pdf.set_font("Arial", "B", 12)

    pdf.cell(0, 8, "Summary", ln=1)

    pdf.set_font("Arial", "", 11)

    pdf.cell(
        0, 8,
        f"Total Expense: INR {total}",
        ln=1
    )

    pdf.cell(
        0, 8,
        f"Total Entries: {count}",
        ln=1
    )

    pdf.ln(5)


    # ---------- TABLE ----------

    pdf.set_font("Arial", "B", 9)

    headers = [
        "Date", "Amount", "Category",
        "SubCat", "Mode", "Notes"
    ]

    widths = [22, 18, 28, 28, 22, 60]


    for h, w in zip(headers, widths):

        pdf.cell(w, 7, h, 1)

    pdf.ln()


    pdf.set_font("Arial", "", 8)


    for _, row in df.iterrows():

        values = [

            row["date"],
            row["amount"],
            row["category"],
            row["subcategory"],
            row["payment_mode"],
            row["notes"]

        ]


        for v, w in zip(values, widths):

            pdf.cell(
                w, 7,
                clean_text(v)[:30],
                1
            )

        pdf.ln()


    # ---------- CHARTS ----------

    pdf.add_page()

    pdf.set_font("Arial", "B", 14)

    pdf.cell(0, 10, "Analytics", ln=1)

    pdf.ln(5)


    for img in charts:

        if os.path.exists(img):

            pdf.image(img, x=15, w=180)

            pdf.ln(15)


    # ---------- SAVE ----------

    name = os.path.join(
        REPORT_DIR,
        f"{month}_{year}.pdf"
    )

    pdf.output(name)

    return name


# ---------------------------------------
# EMAIL SENDER
# ---------------------------------------

def send_report_email(
    user_name,
    to_email,
    file_path,
    month,
    year,
    gmail,
    app_password
):

    msg = EmailMessage()

    subject = f"Expense Report For {month}/{year}"

    msg["Subject"] = subject
    msg["From"] = gmail
    msg["To"] = to_email

    user_first_name = user_name.split()[0]
    msg.set_content(f"""
Hello {user_first_name},

Attached is your expense report for {month}/{year}.

Regards,
Expense Tracker by @PyShaala
""")


    with open(file_path, "rb") as f:
        data = f.read()


    msg.add_attachment(
        data,
        maintype="application",
        subtype="octet-stream",
        filename=os.path.basename(file_path)
    )


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

        server.login(gmail, app_password)

        server.send_message(msg)


# ---------------------------------------
# MAIN HANDLER
# ---------------------------------------

def generate_report(
    user,
    month,
    year,
    report_type="PDF",
    send_email=False,
    gmail=None,
    app_password=None
):

    df = load_expenses(user["email"])

    if df.empty:
        return None, "No Data Found"


    df = filter_month(df, month, year)

    if df.empty:
        return None, "No Records For Selected Month"


    charts = generate_charts(df, month, year)


    if report_type == "CSV":

        file = export_csv(df, month, year)

    else:

        file = export_pdf(
            df,
            charts,
            month,
            year,
            user["name"]
        )


    if send_email:

        send_report_email(
            user["name"],
            user["email"],
            file,
            month,
            year,
            gmail,
            app_password
        )


    return file, "Success"
