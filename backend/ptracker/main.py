from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from ptracker.core.settings import settings
from ptracker.api.main import api_router


controller = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url=f"{settings.API_VERSION_STRING}/openapi.json",
    debug=True,  # TODO nmecklenburg - make this configurable
)

if settings.all_cors_origins:
    controller.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

controller.include_router(api_router, prefix=settings.API_VERSION_STRING)
