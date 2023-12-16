__all__ = ["SMTPRepository"]

import contextlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_validator import validate_email, EmailNotValidError

from src.config import settings
from src.schemas.smtp import MailingTemplate


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

    def render_message(self, template: "MailingTemplate", target_email: str, **environment) -> str:
        mail = MIMEMultipart("related")
        html = template.render_html(**environment)
        msg_html = MIMEText(html, "html")
        mail.attach(msg_html)

        mail["Subject"] = template.subject
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
