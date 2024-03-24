from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from src.api import docs
from src.api.docs import generate_unique_operation_id
from src.api.lifespan import lifespan
from src.api.routers import routers
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
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "persistAuthorization": True,
        "filter": True,
    },
    root_path=api_settings.app_root_path,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    generate_unique_id_function=generate_unique_operation_id,
    lifespan=lifespan,
)


# Redirect root to docs
@app.get("/", tags=["Root"], include_in_schema=False)
async def redirect_to_docs(request: Request):
    return RedirectResponse(url=request.url_for("swagger_ui_html"))


for _router in routers:
    app.include_router(_router)
