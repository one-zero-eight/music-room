import secrets
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from config import settings


async def generate_temporary_code():
    length = 6
    characters = string.digits
    code = "".join(secrets.choice(characters) for _ in range(length))
    return code


async def send_email(to_email, code):
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()

        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = "Temporary code for registration"

        msg.attach(MIMEText(code, "plain"))

        server.sendmail(settings.SMTP_USERNAME, to_email, msg.as_string())

        server.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
