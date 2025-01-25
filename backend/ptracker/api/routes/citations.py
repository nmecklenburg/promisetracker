from fastapi import APIRouter, HTTPException
from sqlmodel import func, select, Session
from typing import cast, Any

from ptracker.api.models import (
    Citation,
    CitationCreate,
    CitationPublic,
    CitationsPublic,
    CitationUpdate,
    Promise
)
from ptracker.core.db import SessionArg

router = APIRouter(prefix="/candidates/{candidate_id}/promises/{promise_id}/citations", tags=["citations"])


@router.get("/", response_model=CitationsPublic)
def read_citations(session: SessionArg, candidate_id: int, promise_id: int, after: int = 0, limit: int = 100) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)

    count_query = select(func.count()).select_from(Citation).where(Citation.promise_id == promise_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    citation_query = select(Citation).where(Citation.promise_id == promise_id).offset(after).limit(limit)
    citations = session.exec(citation_query).all()

    response_citations = [CitationPublic.model_validate(citation) for citation in citations]
    return CitationsPublic(data=response_citations, count=count)


@router.get("/{citation_id}", response_model=CitationPublic)
def read_citation(session: SessionArg, candidate_id: int, promise_id: int, citation_id: int) -> Any:
    citation = _validate_citation(session=session,
                                  candidate_id=candidate_id,
                                  promise_id=promise_id,
                                  citation_id=citation_id)

    return CitationPublic.model_validate(citation)


@router.post("/", response_model=CitationPublic)
def create_citation(session: SessionArg, candidate_id: int, promise_id: int, citation_in: CitationCreate) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)

    citation = Citation.model_validate(citation_in, update={"promise_id": promise_id,
                                                            "url": str(citation_in.url)})
    session.add(citation)
    session.commit()

    return CitationPublic.model_validate(citation)


@router.patch("/{citation_id}", response_model=CitationPublic)
def update_citation(
        session: SessionArg,
        candidate_id: int,
        promise_id: int,
        citation_id: int,
        citation_in: CitationUpdate
) -> Any:
    citation = _validate_citation(session=session,
                                  candidate_id=candidate_id,
                                  promise_id=promise_id,
                                  citation_id=citation_id)

    update_dict = citation_in.model_dump(exclude_unset=True)
    citation.sqlmodel_update(update_dict)
    session.add(citation)
    session.commit()
    session.refresh(citation)

    return CitationPublic.model_validate(citation)


def _validate_promise(session: Session, candidate_id: int, promise_id: int) -> Promise:
    promise = session.get(Promise, promise_id)
    if promise is None or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Page for {promise_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")
    return cast(Promise, promise)


def _validate_citation(session: Session, candidate_id: int, promise_id: int, citation_id: int) -> Citation:
    citation = session.get(Citation, citation_id)
    if citation is None or citation.promise_id != promise_id:
        raise HTTPException(status_code=404, detail=f"Page for {promise_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")

    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)
    return cast(Citation, citation)
