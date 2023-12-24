from pydantic import Field, BaseModel


class MailingTemplate(BaseModel):
    subject: str = Field(..., description="Subject of the email")
    file: str = Field(..., description="Path to the template file (relative to static folder)")

    def render_html(self, **environment) -> str:
        from src.api.dependencies import Dependencies
        from jinja2 import Environment

        main = Dependencies.get(Environment).get_template(self.file)

        html = main.render(**environment)
        return html
