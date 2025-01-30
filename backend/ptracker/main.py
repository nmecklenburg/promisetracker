from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import colorama
import logging
import uvicorn

from ptracker.core.settings import settings
from ptracker.api.main import api_router

colorama.init(strip=False)

controller = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url=f"{settings.API_VERSION_STRING}/openapi.json",
    debug=settings.is_debug,
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

uvicorn.config.LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s %(levelname)s || %(message)s"
uvicorn.config.LOGGING_CONFIG["formatters"]["access"]["use_colors"] = True
uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelname)s || %(message)s"
uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["use_colors"] = True


if __name__ == "__main__":
    # FastAPI CLI is just a thin wrapper above `uvicorn.run`
    # See https://github.com/fastapi/fastapi-cli/blob/9a4741816dc288bbd931e693166117d98ee14dea/src/fastapi_cli/cli.py#L162C9-L162C21  # noqa
    uvicorn.run(
        "main:controller",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.is_debug,
        log_level=logging.DEBUG,
        use_colors=True,
    )
