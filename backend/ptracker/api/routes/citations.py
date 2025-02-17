from fastapi import APIRouter, HTTPException
from sqlmodel import func, select, Session
from typing import cast, Any

from ptracker.api.models import (
    Action,
    Citation,
    CitationCreate,
    CitationPublic,
    CitationsPublic,
    CitationUpdate,
    Promise
)
from ptracker.core.db import SessionArg

promise_router = APIRouter(prefix="/candidates/{candidate_id}/promises/{promise_id}/citations", tags=["citations"])
action_router = APIRouter(prefix="/candidates/{candidate_id}/actions/{action_id}/citations", tags=["citations"])


@promise_router.get("/", response_model=CitationsPublic)
def read_promise_citations(
        session: SessionArg,
        candidate_id: int,
        promise_id: int,
        after: int = 0,
        limit: int = 100
) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)

    count_query = select(func.count()).select_from(Citation).where(Citation.promise_id == promise_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    citation_query = select(Citation).where(Citation.promise_id == promise_id).offset(after).limit(limit)
    citations = session.exec(citation_query).all()

    response_citations = [CitationPublic.model_validate(citation) for citation in citations]
    return CitationsPublic(data=response_citations, count=count)


@promise_router.get("/{citation_id}", response_model=CitationPublic)
def read_promise_citation(session: SessionArg, candidate_id: int, promise_id: int, citation_id: int) -> Any:
    citation = _validate_citation(session=session,
                                  candidate_id=candidate_id,
                                  promise_id=promise_id,
                                  citation_id=citation_id)

    return CitationPublic.model_validate(citation)


@promise_router.post("/", response_model=CitationPublic)
def create_promise_citation(session: SessionArg, candidate_id: int, promise_id: int, citation_in: CitationCreate) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)

    citation = Citation.model_validate(citation_in, update={"promise_id": promise_id,
                                                            "url": str(citation_in.url)})
    session.add(citation)
    session.commit()

    return CitationPublic.model_validate(citation)


@promise_router.patch("/{citation_id}", response_model=CitationPublic)
def update_promise_citation(
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


@action_router.get("/", response_model=CitationsPublic)
def read_action_citations(session: SessionArg, candidate_id: int, action_id: int, after: int = 0, limit: int = 100) -> Any:
    _validate_action(session=session, candidate_id=candidate_id, action_id=action_id)

    count_query = select(func.count()).select_from(Citation).where(Citation.action_id == action_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    citation_query = select(Citation).where(Citation.action_id == action_id).offset(after).limit(limit)
    citations = session.exec(citation_query).all()

    response_citations = [CitationPublic.model_validate(citation) for citation in citations]
    return CitationsPublic(data=response_citations, count=count)


@action_router.get("/{citation_id}", response_model=CitationPublic)
def read_action_citation(session: SessionArg, candidate_id: int, action_id: int, citation_id: int) -> Any:
    citation = _validate_citation(session=session,
                                  candidate_id=candidate_id,
                                  action_id=action_id,
                                  citation_id=citation_id)

    return CitationPublic.model_validate(citation)


@action_router.post("/", response_model=CitationPublic)
def create_action_citation(session: SessionArg, candidate_id: int, action_id: int, citation_in: CitationCreate) -> Any:
    _validate_action(session=session, candidate_id=candidate_id, action_id=action_id)

    citation = Citation.model_validate(citation_in, update={"action_id": action_id,
                                                            "url": str(citation_in.url)})
    session.add(citation)
    session.commit()

    return CitationPublic.model_validate(citation)


@action_router.patch("/{citation_id}", response_model=CitationPublic)
def update_action_citation(
        session: SessionArg,
        candidate_id: int,
        action_id: int,
        citation_id: int,
        citation_in: CitationUpdate
) -> Any:
    citation = _validate_citation(session=session,
                                  candidate_id=candidate_id,
                                  action_id=action_id,
                                  citation_id=citation_id)

    update_dict = citation_in.model_dump(exclude_unset=True)
    citation.sqlmodel_update(update_dict)
    session.add(citation)
    session.commit()
    session.refresh(citation)

    return CitationPublic.model_validate(citation)


def _validate_action(session: Session, candidate_id: int, action_id: int) -> Action:
    action = session.get(Action, action_id)
    if action is None or action.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Page for {action_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")
    return cast(Action, action)


def _validate_promise(session: Session, candidate_id: int, promise_id: int) -> Promise:
    promise = session.get(Promise, promise_id)
    if promise is None or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Page for {promise_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")
    return cast(Promise, promise)


def _validate_citation(
        session: Session,
        candidate_id: int,
        citation_id: int,
        action_id: int | None = None,
        promise_id: int | None = None,
) -> Citation:
    citation = session.get(Citation, citation_id)

    if citation is None:
        raise HTTPException(status_code=404, detail=f"Citation with id={citation_id} not found for any action or "
                                                    f"promise. Something is wrong.")

    if promise_id is not None:
        if citation.promise_id != promise_id:
            raise HTTPException(status_code=404, detail=f"Page for {promise_id=} {citation_id=} does not exist. "
                                                        f"Did you get the IDs mixed up?")
        _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)
    elif action_id is not None:
        if citation.action_id != action_id:
            raise HTTPException(status_code=404, detail=f"Page for {action_id=} {citation_id=} does not exist. "
                                                        f"Did you get the IDs mixed up?")
        _validate_action(session=session, candidate_id=candidate_id, action_id=action_id)
    else:
        assert False, ("Tried to validate a citation for a null promise_id and a null citation_id. "
                       "This is a system error.")
    return cast(Citation, citation)
