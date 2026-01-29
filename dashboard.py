import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
import os
from utils import map_to_bucket, get_bucket_categories
import matplotlib.pyplot as plt
from expense_db import get_connection


# ---------------------------------
# GET AVAILABLE MONTHS (SAFE)
# ---------------------------------

def get_month_list(df):

    # Safety check
    if df.empty or "date" not in df.columns:
        return []

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        return []

    df = df.copy()

    df["year_month"] = df["date"].dt.strftime("%Y-%m")

    months = sorted(
        df["year_month"].dropna().unique(),
        reverse=True
    )

    return months


# ---------------------------------
# LOAD USER EXPENSES (SAFE)
# ---------------------------------

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


    # No data
    if df.empty:
        return df


    # Missing column
    if "date" not in df.columns:
        return pd.DataFrame()


    # Safe datetime convert
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )


    # Remove bad dates
    df = df.dropna(subset=["date"])


    return df


# ---------------------------------
# MONTHLY SUMMARY (SAFE)
# ---------------------------------

def monthly_summary(df, salary, selected_month):

    if df.empty:
        return 0, salary, salary, 0, df

    year, month = selected_month.split("-")

    year = int(year)
    month = int(month)

    df_m = df[
        (df["date"].dt.year == year) &
        (df["date"].dt.month == month)
    ]

    expense = df_m["amount"].sum()
    income = salary + df_m["other_income"].sum()

    savings = income - expense

    percent = (savings / income * 100) if income else 0

    return expense, income, savings, percent, df_m


# ---------------------------------
# PIE CHART
# ---------------------------------

def category_pie(df):

    if df.empty:
        return None

    fig = px.pie(
        df,
        names="category",
        values="amount",
        title="Category-wise Spending"
    )

    return fig


# ---------------------------------
# DAILY TREND
# ---------------------------------

def daily_trend(df):

    if df.empty:
        return None

    daily = df.groupby("date")["amount"].sum().reset_index()

    fig = px.line(
        daily,
        x="date",
        y="amount",
        title="Daily Expense Trend",
        markers=True
    )

    return fig


# ---------------------------------
# SALARY VS EXPENSE
# ---------------------------------

def salary_vs_expense(income, expense):

    data = {
        "Type": ["Income", "Expense"],
        "Amount": [income, expense]
    }

    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x="Type",
        y="Amount",
        title="Income vs Expense"
    )

    return fig


# ---------------------------------
# BUDGET ANALYSIS
# ---------------------------------

def budget_analysis(df, budget_map, income):

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Bucket",
                "Categories",
                "Limit",
                "Spent",
                "Status"
            ]
        )

    df = df.copy()

    df["final_bucket"] = df["category"].apply(map_to_bucket)

    bucket_categories = get_bucket_categories()

    result = []

    for bucket, percent in budget_map.items():

        limit = income * percent / 100

        spent = df[
            df["final_bucket"] == bucket
        ]["amount"].sum()

        status = "OK🟢"

        if spent > limit:
            status = "Overspent🔴"

        cats = bucket_categories.get(bucket, [])

        cat_text = ", ".join(cats) if cats else "-"

        result.append(
            (
                bucket,
                cat_text,
                round(limit, 2),
                round(spent, 2),
                status
            )
        )

    return pd.DataFrame(
        result,
        columns=[
            "Bucket",
            "Categories",
            "Limit",
            "Spent",
            "Status"
        ]
    )


# ---------------------------------
# INSIGHTS ENGINE
# ---------------------------------

def generate_insights(budget_df, savings_percent):

    insights = []

    if budget_df.empty:
        return ["ℹ️ No data for insights"]

    for _, row in budget_df.iterrows():

        if row["Status"] == "Overspent🔴":
            insights.append(
                f"⚠️ {row['Bucket']} exceeded limit"
            )

    if savings_percent < 10:
        insights.append("⚠️ Savings below 10%")

    if savings_percent >= 20:
        insights.append("✅ Good savings habit")

    if not insights:
        insights.append("🎯 Good financial health")

    return insights


# ---------------------------------
# DASHBOARD UI (SAFE)
# ---------------------------------

def show_dashboard(user, budget_map):

    df = load_expenses(user["email"])


    # No expenses at all
    if df.empty:
        st.info("📭 No expenses yet. Start adding some!")
        return


    # ---------------- Month Selector ----------------

    months = get_month_list(df)

    if not months:
        st.info("📅 No valid date data found")
        return


    current = datetime.now().strftime("%Y-%m")

    default_index = months.index(current) if current in months else 0


    selected_month = st.selectbox(
        "📅 Select Month",
        months,
        index=default_index
    )


    # ---------------- Summary ----------------

    exp, inc, sav, perc, df_m = monthly_summary(
        df,
        user["salary"],
        selected_month
    )


    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Expense", f"₹{exp:,.0f}")
    c2.metric("Income", f"₹{inc:,.0f}")
    c3.metric("Savings", f"₹{sav:,.0f}")
    c4.metric("Savings %", f"{perc:.1f}%")

    st.divider()


    # ---------------- Charts ----------------

    col1, col2 = st.columns(2)

    with col1:

        fig1 = category_pie(df_m)

        if fig1:
            st.plotly_chart(fig1, use_container_width=True)


    with col2:

        fig2 = daily_trend(df_m)

        if fig2:
            st.plotly_chart(fig2, use_container_width=True)


    st.plotly_chart(
        salary_vs_expense(inc, exp),
        use_container_width=True
    )


    st.divider()


    # ---------------- Budget ----------------

    st.subheader("📌 Budget vs Actual")

    budget_df = budget_analysis(
        df_m,
        budget_map,
        inc
    )

    st.dataframe(budget_df, use_container_width=True)


    # ---------------- Insights ----------------

    st.subheader("🤖 Smart Insights")

    for i in generate_insights(budget_df, perc):
        st.info(i)
