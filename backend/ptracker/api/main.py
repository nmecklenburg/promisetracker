from fastapi import APIRouter
from ptracker.api.routes import actions, candidates, citations, promises


api_router = APIRouter()
api_router.include_router(actions.router)
api_router.include_router(actions.nested_promise_router)
api_router.include_router(candidates.router)
api_router.include_router(citations.action_router)
api_router.include_router(citations.promise_router)
api_router.include_router(promises.router)
api_router.include_router(promises.nested_action_router)
