import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string


def generate_random_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_email_with_code(email, code):
    smtp_server = "your-smtp-server.com"
    smtp_port = 587
    smtp_username = "your-smtp-username"
    smtp_password = "your-smtp-password"

    from_email = "your-email@example.com"
    to_email = email
    subject = "Authentication Code"

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    text = f"Your authentication code is: {code}"
    message.attach(MIMEText(text, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, message.as_string())
