from fastapi import APIRouter
from ptracker.api.routes import candidates, citations, promises


api_router = APIRouter()
api_router.include_router(candidates.router)
api_router.include_router(promises.router)
api_router.include_router(citations.router)
