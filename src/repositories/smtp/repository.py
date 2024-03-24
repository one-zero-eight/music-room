__all__ = ["SMTPRepository", "smtp_repository"]

import contextlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from email_validator import validate_email, EmailNotValidError

from src.config import api_settings

VERIFICATION_CODE_TEMPLATE = (Path(__file__).parent / "templates/verification-code.html").read_text()


class SMTPRepository:
    _server: smtplib.SMTP

    def __init__(self):
        self._server = smtplib.SMTP(api_settings.smtp_server, api_settings.smtp_port)

    @contextlib.contextmanager
    def _context(self):
        self._server.connect(api_settings.smtp_server, api_settings.smtp_port)
        self._server.starttls()
        self._server.login(api_settings.smtp_username, api_settings.smtp_password)
        yield
        self._server.quit()

    def render_verification_message(self, target_email: str, code: str) -> str:
        mail = MIMEMultipart("related")
        html = VERIFICATION_CODE_TEMPLATE.replace("${{code}}", code)
        msg_html = MIMEText(html, "html")
        mail.attach(msg_html)

        mail["Subject"] = "Verification code"
        mail["From"] = f"Music Room <{api_settings.smtp_username}>"
        mail["To"] = target_email

        return mail.as_string()

    def send(self, message: str, to: str):
        try:
            valid = validate_email(to)
            to = valid.normalized
        except EmailNotValidError as e:
            raise ValueError(e)
        with self._context():
            self._server.sendmail(api_settings.smtp_username, to, message)


smtp_repository = SMTPRepository()
