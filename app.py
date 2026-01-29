import streamlit as st
from datetime import date
import re
import os
import pandas as pd
from datetime import datetime

from database import (
    init_db,
    get_user_by_email,
    update_user_profile,
    get_user_count
)

from auth import (
    login_user,
    signup_user,
    reset_password,
    email_exists,
    generate_captcha
)

# from expense_manager import (
#     init_expense_file,
#     # add_expense,
#     get_user_expenses,
#     delete_expense
# )

from categories import (
    load_categories,
    get_bucket,
    add_category
)

from dashboard import show_dashboard
from utils import get_budget_map

from reports import (
    # load_month_data,
    export_csv,
    export_pdf,
    # get_month_name,
    send_report_email
)

from expense_service import (add_expense, delete_expense, get_user_expenses)
from reports import generate_report

from expense_db import create_expense_table

create_expense_table()


# ---------------- EMAIL CONFIG ----------------

GMAIL_ID = "pramod.com19@gmail.com"
APP_PASSWORD = "akbe amym kmdk yjox"


# -------------------------------------------------
# INIT
# -------------------------------------------------

init_db()

st.set_page_config(
    page_title="Expense Tracker",
    layout="wide"
)
# ---------------- UI Styling ----------------

st.markdown("""
<style>

div[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

div[data-baseweb="input"] > div {
    border-radius: 10px !important;
}

textarea {
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SCROLL TO TOP ----------------

def scroll_to_top():
    st.markdown("""
        <script>
            window.scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)

def show_app_intro():

    intro = """
    <div style="
        background: linear-gradient(135deg,#1f2937,#111827);
        padding: 30px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        height: 100%;
    ">

        <h2 style="color:#38bdf8;">💰 Personal Expense Tracker</h2>

        <p style="font-size:15px;line-height:1.6;">
        Take control of your finances with smart tracking, budgeting,
        and insights — all in one place.
        </p>

        <hr style="border:0.5px solid #374151;">

        <h4>🚀 Key Features</h4>

        <ul style="font-size:14px;line-height:1.8;">
            <li>📊 Smart Dashboard & Reports</li>
            <li>🗂 Category & Sub-Category Tracking</li>
            <li>💳 Payment Mode Management</li>
            <li>📈 Budget vs Actual Analysis</li>
            <li>📥 PDF / CSV Export</li>
            <li>📧 Email Report Delivery</li>
            <li>🔐 Secure Login System</li>
        </ul>

        <hr style="border:0.5px solid #374151;">

        <h4>👨‍💻 About Us</h4>

        <p style="font-size:14px;line-height:1.6;">
        We are passionate developers focused on building simple,
        powerful financial tools to help people manage money
        efficiently and stress-free.
        </p>

        <p style="font-size:13px;color:#9ca3af;">
        Developed with ❤️ in India
        </p>

    </div>
    """

    st.markdown(intro, unsafe_allow_html=True)

def show_app_intro_native():

    # st.subheader("💰 Personal Expense Tracker")

    st.caption("Track • Save • Grow your Money")

    # st.markdown("---")

    st.markdown("### 🚀 Key Features")

    st.markdown("""
    ✅ Smart Expense Dashboard  
    ✅ Category & Budget Tracking  
    ✅ Monthly Reports (PDF / CSV)  
    ✅ Email Report Delivery  
    ✅ Secure Login System  
    ✅ Profile Management  
    """)

    st.markdown("---")
    user_count = get_user_count()
    st.success(f"Built with ❤️ | Used by {user_count}+ users")

# -------------------------------------------------
# Initialize Expense File
# -------------------------------------------------

# init_expense_file()

# -------------------------------------------------
# SESSION INIT
# -------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "captcha" not in st.session_state:
    st.session_state.captcha = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "profile_updated" not in st.session_state:
    st.session_state.profile_updated = False

if "expense_added" not in st.session_state:
    st.session_state.expense_added = False

if "expense_deleted" not in st.session_state:
    st.session_state.expense_deleted = False
if "sel_category" not in st.session_state:
    st.session_state.sel_category = ""

if "sel_subcategory" not in st.session_state:
    st.session_state.sel_subcategory = ""
# -------------------------------------------------
# LOGIN CHECK
# -------------------------------------------------

def require_login():

    if "user" not in st.session_state:
        st.warning("⚠️ Please login first")
        st.stop()

    if st.session_state.user is None:
        st.warning("⚠️ Session expired. Please login again.")
        st.stop()


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

def logout():

    st.session_state.user = None
    st.session_state.captcha = None
    st.session_state.page = "Dashboard"

    st.rerun()


# -------------------------------------------------
# VALIDATORS
# -------------------------------------------------

def valid_name(name):
    return bool(re.match("^[A-Za-z ]+$", name))


def valid_phone(phone):
    return phone.isdigit() and len(phone) == 10



# -------------------------------------------------
# SIDEBAR (AFTER LOGIN)
# -------------------------------------------------

if st.session_state.user:

    with st.sidebar:

        st.success(f"👤 {st.session_state.user['name']}")

        menu = st.radio(
            "Menu",
            ["Dashboard", "Add Expense", "View Expenses", "My Profile", "Reports", "Logout"],
            key="sidebar_menu"
        )

        if menu == "Logout":
            logout()
        else:
            st.session_state.page = menu

# -------------------------------------------------
# AUTH UI (BEFORE LOGIN)
# -------------------------------------------------

if not st.session_state.user:

    st.title("💰 Personal Expense Tracker")

    left, right = st.columns([1.2, 1])

    with left:
        # show_app_intro()
        show_app_intro_native()

    with right:

        tab1, tab2, tab3 = st.tabs(
            ["Login", "Signup", "Reset"]
        )

        # ================= LOGIN =================
        with tab1:

            login_email = st.text_input(
                "Email", key="login_email"
            )

            login_pass = st.text_input(
                "Password",
                type="password",
                key="login_pass"
            )

            if st.button("Login", key="login_btn"):

                user = login_user(login_email, login_pass)

                if user:

                    st.session_state.user = user
                    st.session_state.page = "Dashboard"

                    st.success("Login Successful ✅")

                    st.rerun()

                else:
                    st.error("Invalid Credentials")


        # ================= SIGNUP =================
        with tab2:

            st.subheader("Signup")

            su_name = st.text_input("Name", key="su_name")
            su_email = st.text_input("Email", key="su_email")
            su_phone = st.text_input("Phone", key="su_phone")

            su_pass = st.text_input(
                "Password", type="password", key="su_pass"
            )

            su_confirm = st.text_input(
                "Confirm", type="password", key="su_confirm"
            )

            su_dob = st.date_input(
                "DOB",
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                key="signup_dob_unique"
            )

            su_salary = st.number_input(
                "Salary",
                min_value=0.0,
                key="su_salary"
            )

            su_gender = st.selectbox(
                "Gender",
                ["Prefer Not", "Male", "Female"],
                key="su_gender"
            )

            su_job = st.selectbox(
                "Job",
                ["Prefer Not", "Govt", "Private", "Business", "Other"],
                key="su_job"
            )

            su_address = st.text_area(
                "Address",
                key="su_address"
            )


            if st.button("Signup", key="signup_btn"):

                if not su_name or not su_email or not su_phone or not su_dob:
                    st.error("All required fields missing")

                elif not valid_name(su_name):
                    st.error("Invalid Name")

                elif not valid_phone(su_phone):
                    st.error("Invalid Phone")

                elif su_pass != su_confirm:
                    st.error("Password mismatch")

                elif email_exists(su_email):
                    st.error("Email already exists")

                else:

                    data = {
                        "name": su_name,
                        "email": su_email,
                        "password": su_pass,
                        "phone": su_phone,
                        "dob": str(su_dob),
                        "salary": su_salary,
                        "gender": su_gender,
                        "job": su_job,
                        "address": su_address,
                        "pic": "",
                        "notify": "21:00"
                    }

                    if signup_user(data):
                        st.success("Signup Successful ✅")
                    else:
                        st.error("Signup Failed")


        # ================= RESET =================
        with tab3:

            rp_email = st.text_input(
                "Email", key="rp_email"
            )

            rp_dob = st.date_input(
                "DOB",
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                key="reset_dob_unique"
            )

            if st.session_state.captcha is None:
                st.session_state.captcha = generate_captcha()

            a, b, ans = st.session_state.captcha

            st.info(f"{a} + {b} = ?")

            rp_ans = st.number_input(
                "Answer",
                step=1,
                key="rp_ans"
            )

            rp_new = st.text_input(
                "New Password",
                type="password",
                key="rp_new"
            )

            rp_conf = st.text_input(
                "Confirm",
                type="password",
                key="rp_conf"
            )

            if st.button("Reset", key="reset_btn"):

                if rp_ans != ans:
                    st.error("Wrong Captcha")

                elif not rp_new:
                    st.error("Password required")

                elif rp_new != rp_conf:
                    st.error("Password mismatch")

                else:

                    if reset_password(
                        rp_email,
                        str(rp_dob),
                        rp_new
                    ):
                        st.success("Reset Done ✅")

                    else:
                        st.error("Reset Failed")

                    st.session_state.captcha = generate_captcha()

        st.stop()


# -------------------------------------------------
# MAIN APP
# -------------------------------------------------

require_login()


# ================= DASHBOARD =================

if st.session_state.page == "Dashboard":

    st.title("📊 Dashboard")

    st.success(
        f"Welcome {st.session_state.user['name']}"
    )

    budget_map = get_budget_map()

    show_dashboard(
        st.session_state.user,
        budget_map
    )


# ================= ADD EXPENSE =================

elif st.session_state.page == "Add Expense":

    require_login()

    st.title("➕ Add Expense")


    # Success message
    if st.session_state.expense_added:
        st.success("✅ Expense Added Successfully")
        st.session_state.expense_added = False


    user = st.session_state.user


    # Reload categories every time
    cats = load_categories()


    cat_list = list(cats.keys()) + ["➕ Add New"]
    sub_list = []


    # ---------------- CATEGORY ----------------

    category = st.selectbox(
        "Category",
        cat_list,
        key="category_select"
    )


    if category != "➕ Add New" and category in cats:
        sub_list = list(cats[category].keys())

    sub_list = sub_list + ["➕ Add New"]


    # ---------------- SUB CATEGORY ----------------

    subcategory = st.selectbox(
        "Sub Category",
        sub_list,
        key="subcategory_select"
    )


    # ---------------- NEW CATEGORY INPUT ----------------

    new_cat = None
    new_sub = None


    if category == "➕ Add New":

        new_cat = st.text_input(
            "New Category Name",
            key="new_cat_input"
        )


    if subcategory == "➕ Add New":

        new_sub = st.text_input(
            "New Sub Category Name",
            key="new_sub_input"
        )


    # ---------------- MAIN FORM ----------------

    with st.form("expense_form"):


        exp_date = st.date_input("Date", value=date.today())


        amount = st.number_input(
            "Amount",
            min_value=1.0,
            step=1.0
        )


        spent_by = st.selectbox(
            "Spent By",
            ["Self", "Wife", "Husband", "Child", "Parent", "Other"],
            index=0
        )


        payment = st.selectbox(
            "Payment Mode",
            ["UPI", "Cash", "Card", "Net Banking", "Wallet"],
            index=0
        )


        other_income = st.number_input(
            "Other Income (Optional)",
            min_value=0.0
        )


        notes = st.text_area("Notes (Optional)")


        submit = st.form_submit_button("💾 Save Expense")


        # ---------------- SUBMIT ----------------

    if submit:


        # ---------- Validation ----------

        if amount <= 0:
            st.error("Invalid amount")
            st.stop()


        if category == "➕ Add New" and not new_cat:
            st.error("Enter new category name")
            st.stop()


        if subcategory == "➕ Add New" and not new_sub:
            st.error("Enter new sub category name")
            st.stop()


        # ---------- Final Values ----------

        final_cat = new_cat if new_cat else category
        final_sub = new_sub if new_sub else subcategory


        # ---------- Save New Mapping ----------

        if new_cat or new_sub:

            add_category(
                final_cat,
                final_sub,
                "Lifestyle"
            )


        # Reload after save
        cats = load_categories()


        bucket = get_bucket(final_cat, final_sub)


        # ---------- Save Expense ----------

        data = {
            "email": user["email"],
            "name": user["name"],
            "date": str(exp_date),
            "amount": amount,
            "category": final_cat,
            "subcategory": final_sub,
            "bucket": bucket,
            "spent_by": spent_by,
            "payment_mode": payment,
            "notes": notes,
            "other_income": other_income
        }


        add_expense(data)


        # ---------- Reset widgets safely ----------

        if "category_select" in st.session_state:
            del st.session_state["category_select"]

        if "subcategory_select" in st.session_state:
            del st.session_state["subcategory_select"]


        st.session_state.expense_added = True
        scroll_to_top()
        st.rerun()

# ================= VIEW EXPENSE =================

elif st.session_state.page == "View Expenses":

    require_login()

    st.title("📄 My Expenses")


    # Init flag
    if "expense_deleted" not in st.session_state:
        st.session_state.expense_deleted = False


    # Success message
    if st.session_state.expense_deleted:
        st.success("✅ Expense Deleted Successfully")
        st.session_state.expense_deleted = False


    user = st.session_state.user

    df = get_user_expenses(user["email"])



    if df.empty:
        st.info("No expenses yet")
        st.stop()


    # --------------------------
    # Add Row Number
    # --------------------------

    df_view = df.copy()

    df_view.insert(
        0,
        "Row No",
        range(1, len(df_view) + 1)
    )
    # # Hide DB id
    # df_view = df_view.drop(columns=["id"])

    # cols_to_show = [
    #                 "No", "date", "amount",
    #                 "category", "subcategory",
    #                 "payment_mode", "notes"
    #                 ]

    # st.dataframe(df_view[cols_to_show], use_container_width=True)

    st.dataframe(
        df_view,
        use_container_width=True, hide_index=True,
        column_config={
                        "id": None    }
    )
    



    # --------------------------
    # Delete Section
    # --------------------------

    st.subheader("🗑️ Delete Expense")


    row_no = st.number_input(
        "Enter Row Number",
        min_value=1,
        max_value=len(df_view),
        step=1
    )

    # selected = st.selectbox(
    # "Select Expense to Delete",
    # df_view["Row No"])
    # st.write(selected)

    if st.button("Delete Expense"):

        # Map Row → DB id
        selected_row = df_view.iloc[row_no - 1]

        expense_id = int(selected_row["id"])

        success = delete_expense(expense_id, user["email"])
        if success:
            # st.write("Deleting ID:", expense_id)
            st.session_state.expense_deleted = True
            scroll_to_top()
            st.rerun()
        else:
            st.error("❌ Unable to delete expense")

    
# ================= PROFILE =================

elif st.session_state.page == "My Profile":

    require_login()

    st.title("👤 My Profile")
    # Show success message after reload
    if st.session_state.profile_updated:
        st.success("✅ Profile Updated Successfully")
        # Reset flag
        st.session_state.profile_updated = False

    user = get_user_by_email(
        st.session_state.user["email"]
    )

    if not user:
        st.error("User not found")
        st.stop()


    with st.form("profile_form", clear_on_submit=False):

        name = st.text_input(
            "Name",
            value=user["name"],
            key="pf_name"
        )

        email = st.text_input(
            "Email",
            value=user["email"],
            disabled=True,
            key="pf_email"
        )

        phone = st.text_input(
            "Phone",
            value=user["phone"],
            key="pf_phone"
        )

        dob = st.date_input(
            "DOB",
            value=date.fromisoformat(user["dob"]),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            key="profile_dob_form"
        )

        salary = st.number_input(
            "Salary",
            value=float(user["salary"] or 0),
            min_value=0.0,
            key="pf_salary"
        )

        gender = st.selectbox(
            "Gender",
            ["Prefer Not", "Male", "Female"],
            index=["Prefer Not", "Male", "Female"]
            .index(user["gender"] or "Prefer Not"),
            key="pf_gender"
        )

        job = st.selectbox(
            "Job",
            ["Prefer Not", "Govt", "Private", "Business", "Other"],
            index=["Prefer Not", "Govt", "Private",
                   "Business", "Other"]
            .index(user["job"] or "Prefer Not"),
            key="pf_job"
        )

        address = st.text_area(
            "Address",
            value=user["address"],
            key="pf_address"
        )

        submit_btn = st.form_submit_button("💾 Save Profile")


    # ---- AFTER FORM SUBMIT ----

    if submit_btn:

        if not valid_name(name):
            st.error("Invalid Name (Only letters allowed)")

        elif not valid_phone(phone):
            st.error("Invalid Phone (10 digits only)")

        else:

            update_user_profile(
                email=user["email"],
                name=name,
                phone=phone,
                dob=str(dob),
                salary=salary,
                gender=gender,
                job=job,
                address=address
            )

            # Refresh session
            st.session_state.user = get_user_by_email(
                user["email"]
            )

            st.session_state.profile_updated = True

            st.rerun()

# ================= REPORTS =================

elif st.session_state.page == "Reports":

    st.title("📄 Monthly Expense Report")


    # ---------------- CURRENT DATE ----------------

    today = date.today()

    current_month = today.month
    current_year = today.year


    # ---------------- MONTH SELECT ----------------

    month = st.selectbox(
        "Select Month",
        list(range(1, 13)),
        index=current_month - 1
    )

    year = st.selectbox(
        "Select Year",
        list(range(2020, current_year + 1)),
        index=current_year - 2020
    )


    # ---------------- REPORT TYPE ----------------

    report_type = st.radio(
        "Report Format",
        ["PDF", "CSV"],
        horizontal=True
    )


    # ---------------- EMAIL OPTION ----------------

    send_email = st.checkbox(
        "📧 Send to my Email"
    )


    st.divider()


    # ---------------- GENERATE BUTTON ----------------

    if st.button("📥 Generate Report", use_container_width=True):

        with st.spinner("Generating report..."):

            file, msg = generate_report(

                user=st.session_state.user,

                month=month,
                year=year,

                report_type=report_type,

                send_email=send_email,

                gmail=GMAIL_ID,
                app_password=APP_PASSWORD
            )


        if file:

            st.success("✅ Report Generated Successfully")


            # DOWNLOAD BUTTON

            with open(file, "rb") as f:

                st.download_button(
                    "⬇ Download Report",
                    f,
                    file_name=os.path.basename(file),
                    use_container_width=True
                )


            if send_email:
                st.success("📧 Email Sent Successfully")


        else:
            st.error(msg)

######FOOTER###########
def show_footer():

    footer = """
    <style>

    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117;
        color: #ffffff;
        text-align: center;
        padding: 12px 10px;
        font-size: 14px;
        z-index: 1000;
        border-top: 1px solid #333;
    }

    .footer a {
        color: #4da6ff;
        text-decoration: none;
        margin: 0 10px;
        font-weight: 500;
    }

    .footer a:hover {
        text-decoration: underline;
        color: #66ccff;
    }

    </style>

    <div class="footer">
        © 2026 Expense Tracker | Developed by <b>PyShaala</b> 🚀 |
        <!--<a href="https://linkedin.com" target="_blank">LinkedIn</a>
        <a href="https://github.com" target="_blank">GitHub</a>-->
        <a href="https://instagram.com/pyshaala" target="_blank">Instagram</a> 
        <a href="https://youtube.com/@pyshaala">Youtube</a>
    </div>
    """

    st.markdown(footer, unsafe_allow_html=True)

#calliing footer
show_footer()
st.markdown(
    "<div style='margin-bottom:70px;'></div>",
    unsafe_allow_html=True
)