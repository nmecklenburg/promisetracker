# from fastapi import APIRouter, HTTPException
# from sqlmodel import col, func, select, Session
# from typing import Any
#
# from ptracker.api.models import Source, SourceCreate
# from ptracker.api.models._associations import SourceCandidateLink
# from ptracker.core.db import SessionArg
#
# router = APIRouter(prefix="/sources", tags=["sources"])
#
#
# def _create_source_helper(session: Session, source_in: SourceCreate) -> Source:
#     source = Source.model_validate(source_in, update={"url": str(source_in.url)})
#     session.add(source)
#     session.commit()
#     session.refresh(source)
#     return source
#
#
# # @router.post("/", response_model=SourcePublic)
# # def create_source(session: SessionArg, source_in: SourceCreate) -> Any:
# #     return _create_source_helper(session, source_in)
#
