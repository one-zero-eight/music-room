from fastapi import FastAPI
from fastapi_swagger import patch_fastapi

import src.api.logging_  # noqa: F401
from src.api import docs
from src.api.docs import generate_unique_operation_id
from src.api.lifespan import lifespan
from src.config import api_settings

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
    root_path=api_settings.app_root_path,
    root_path_in_servers=False,
    generate_unique_id_function=generate_unique_operation_id,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

patch_fastapi(app)

from src.api.auth.routes import router as router_auth  # noqa: E402
from src.api.bookings.routes import router as router_booking  # noqa: E402
from src.api.root.routes import router as router_root  # noqa: E402
from src.api.users.routes import router as router_users  # noqa: E402

app.include_router(router_auth)
app.include_router(router_root)
app.include_router(router_booking)
app.include_router(router_users)
