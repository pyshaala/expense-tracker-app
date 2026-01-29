import pandas as pd
from pathlib import Path
from datetime import datetime


# ---------------------------------
# FILE PATH
# ---------------------------------

DATA_PATH = Path("data/expenses.csv")


# ---------------------------------
# INIT FILE
# ---------------------------------

def init_expense_file():

    DATA_PATH.parent.mkdir(exist_ok=True)

    if not DATA_PATH.exists():

        df = pd.DataFrame(columns=[
                                    "email",
                                    "name",
                                    "date",
                                    "amount",
                                    "category",
                                    "subcategory",
                                    "bucket",
                                    "spent_by",
                                    "payment_mode",
                                    "notes",
                                    "other_income"
                                ])


        df.to_csv(DATA_PATH, index=False)


# ---------------------------------
# ADD EXPENSE
# ---------------------------------

def add_expense(data: dict):

    init_expense_file()

    df = pd.read_csv(DATA_PATH)

    df = pd.concat([df, pd.DataFrame([data])])

    df.to_csv(DATA_PATH, index=False)


# ---------------------------------
# GET USER EXPENSES
# ---------------------------------

def get_user_expenses(email):

    init_expense_file()

    df = pd.read_csv(DATA_PATH)

    return df[df["email"] == email]


# ---------------------------------
# DELETE EXPENSE
# ---------------------------------

def delete_expense(index):

    df = pd.read_csv(DATA_PATH)

    df = df.drop(index)

    df.to_csv(DATA_PATH, index=False)
