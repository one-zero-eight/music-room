__all__ = ["SMTPRepository"]

import contextlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

import jinja2
from email_validator import validate_email, EmailNotValidError

from src.config import settings

_template_path = Path(__file__).parent / "verification-code.jinja2"
_logo_path = Path(__file__).parent / "logo.png"
VERIFICATION_CODE_TEMPLATE: jinja2.Template = jinja2.Template(_template_path.read_text(), autoescape=True)


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
        html = VERIFICATION_CODE_TEMPLATE.render(code=code)
        msg_html = MIMEText(html, "html")
        mail.attach(msg_html)

        with open(_logo_path, "rb") as f:
            logo = MIMEImage(f.read(), name="logo.png")
            logo.add_header("Content-ID", "logo")
            mail.attach(logo)

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
