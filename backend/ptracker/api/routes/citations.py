from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select, Session
from typing import Any

from ptracker.api.models import Citation, CitationCreate
from ptracker.core.db import SessionArg

router = APIRouter(prefix="/candidates/{cid}/promises/{pid}/citations", tags=["citations"])


def _create_citation_helper(session: Session, citation_in: CitationCreate) -> Citation:
    citation = Citation.model_validate(citation_in, update={"url": str(citation_in.url)})
    session.add(citation)
    session.commit()
    session.refresh(citation)
    return citation
