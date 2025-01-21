from fastapi import APIRouter

from ptracker.api.routes import candidates

api_router = APIRouter()
api_router.include_router(candidates.router)
