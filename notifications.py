import smtplib
from email.message import EmailMessage


def send_email(to, msg):
    email = EmailMessage()
    email.set_content(msg)

    email['Subject'] = "Expense Reminder"
    email['From'] = "pramod.com19@gmail.com"
    email['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login("pramod.com19@gmail.com","akbe amym kmdk yjox")
        smtp.send_message(email)