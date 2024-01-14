__all__ = ["SMTPRepository"]

import contextlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from email_validator import validate_email, EmailNotValidError

from src.config import settings

VERIFICATION_CODE_TEMPLATE = (Path(__file__).parent / "templates/verification-code.html").read_text()


class SMTPRepository:
    _server: smtplib.SMTP

    def __init__(self):
        self._server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)

    @contextlib.contextmanager
    def _context(self):
        self._server.connect(settings.SMTP_SERVER, settings.SMTP_PORT)
        self._server.starttls()
        self._server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        yield
        self._server.quit()

    def render_verification_message(self, target_email: str, code: str) -> str:
        mail = MIMEMultipart("related")
        html = VERIFICATION_CODE_TEMPLATE.replace("${{code}}", code)
        msg_html = MIMEText(html, "html")
        mail.attach(msg_html)

        mail["Subject"] = "Music Room: Verification code"
        mail["From"] = settings.SMTP_USERNAME
        mail["To"] = target_email

        return mail.as_string()

    def send(self, message: str, to: str):
        try:
            valid = validate_email(to)
            to = valid.normalized
        except EmailNotValidError as e:
            raise ValueError(e)
        with self._context():
            self._server.sendmail(settings.SMTP_USERNAME, to, message)
