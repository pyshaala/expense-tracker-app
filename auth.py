import bcrypt
import random
from database import get_connection
from database import get_user_by_email
import bcrypt

# ---------------- PASSWORD ----------------

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


# ---------------- SIGNUP ----------------

from database import insert_user


def signup_user(data):

    hashed = bcrypt.hashpw(
        data["password"].encode(),
        bcrypt.gensalt()
    )

    data["password"] = hashed.decode()

    return insert_user(data)


# ---------------- LOGIN ----------------

from database import get_user_by_email

def login_user(email, password):

    user = get_user_by_email(email)

    if not user:
        return None

    stored_pass = user["password"].encode()
    input_pass = password.encode()

    if bcrypt.checkpw(input_pass, stored_pass):
        return user   # ✅ return FULL USER DICT

    return None



# ---------------- CHECK EMAIL ----------------

def email_exists(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    conn.close()

    return True if user else False


# ---------------- RESET PASSWORD ----------------

from database import get_user_by_email, update_password
import bcrypt


def reset_password(email, dob, new_pass):

    user = get_user_by_email(email)

    if not user:
        return False

    if user["dob"] != dob:
        return False

    hashed = bcrypt.hashpw(
        new_pass.encode(),
        bcrypt.gensalt()
    )

    update_password(email, hashed.decode())

    return True



# ---------------- CAPTCHA ----------------

def generate_captcha():

    a = random.randint(10, 99)
    b = random.randint(1, 9)

    return a, b, a + b
