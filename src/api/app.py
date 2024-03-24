from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from src.api import docs
from src.api.docs import generate_unique_operation_id
from src.api.routers import routers
from src.config import api_settings
from src.storage.sql import SQLAlchemyStorage

# App definition
app = FastAPI(
    title=docs.TITLE,
    summary=docs.SUMMARY,
    description=docs.DESCRIPTION,
    version=docs.VERSION,
    contact=docs.CONTACT_INFO,
    license_info=docs.LICENSE_INFO,
    openapi_tags=docs.TAGS_INFO,
    servers=[
        {"url": api_settings.app_root_path, "description": "Current"},
    ],
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "persistAuthorization": True,
        "filter": True,
    },
    root_path=api_settings.app_root_path,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    generate_unique_id_function=generate_unique_operation_id,
)


async def setup_repositories():
    from src.repositories.participants.repository import participant_repository
    from src.repositories.bookings.repository import booking_repository
    from src.repositories.auth.repository import auth_repository

    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    participant_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    auth_repository.update_storage(storage)


def setup_timezone():
    import sys
    import os
    import time

    if sys.platform != "win32":  # unix only
        os.environ["TZ"] = "Europe/Moscow"
        time.tzset()


@app.on_event("startup")
async def startup_event():
    setup_timezone()
    await setup_repositories()


# Redirect root to docs
@app.get("/", tags=["Root"], include_in_schema=False)
async def redirect_to_docs(request: Request):
    return RedirectResponse(url=request.url_for("swagger_ui_html"))


for _router in routers:
    app.include_router(_router)
