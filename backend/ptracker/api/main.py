from fastapi import APIRouter

import logging

from ptracker.api.routes import candidates, citations, promises

logging.basicConfig(level=logging.INFO)

api_router = APIRouter()
api_router.include_router(candidates.router)
api_router.include_router(promises.router)
api_router.include_router(citations.router)
