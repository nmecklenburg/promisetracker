from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select, Session
from typing import cast, Any

from ptracker.api.models import (
    Citation,
    Promise,
    PromiseCreate,
    PromisePublic,
    PromisesPublic,
    PromiseUpdate,
)
from ptracker.core.db import SessionArg

router = APIRouter(prefix="/candidates/{cid}/promises", tags=["promises"])


@router.get("/", response_model=PromisesPublic)
def read_promises(session: SessionArg, cid: int, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Promise).where(Promise.candidate_id == cid)
    count = session.exec(count_query).one()  # one and only one result, else error

    promise_query = select(Promise).where(Promise.candidate_id == cid).offset(after).limit(limit)
    promises = session.exec(promise_query).all()

    cp_query = (select(Citation.id, Citation.promise_id)
                .join(Promise)
                .where(col(Citation.promise_id).in_([p.id for p in promises])))
    citation_promise_tuples = session.exec(cp_query).all()

    cp_map = {}
    for citation_id, promise_id in citation_promise_tuples:
        if promise_id not in cp_map:
            cp_map[promise_id] = []

        cp_map[promise_id].append(citation_id)

    response_promises = []
    for promise in promises:
        response_promise = PromisePublic.model_validate(promise,
                                                        update={"citations": cp_map.get(promise.id, [])})
        response_promises.append(response_promise)

    return PromisesPublic(data=response_promises, count=count)


@router.get("/{pid}", response_model=PromisePublic)
def read_promise(session: SessionArg, cid: int, pid: int) -> Any:
    promise = session.get(Promise, pid)

    if not promise:
        raise HTTPException(status_code=404, detail=f"Promise with id={pid} not found for candidate with id={cid}.")

    citation_ids = _get_citation_ids_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": citation_ids})


@router.post("/", response_model=PromisePublic)
def create_promise(session: SessionArg, cid: int, promise_in: PromiseCreate) -> Any:
    # We disallow the creation of promises without citations, meaning we must create citations
    # as part of this promise creation flow.
    citations = []
    # Length validations taken care of at Pydantic layer. There should be at least one.
    for citation_in in promise_in.citations:
        citation_kwargs = citation_in.model_dump()
        citation_kwargs.update({"url": str(citation_in.url)})
        citation = Citation(**citation_kwargs)

        session.add(citation)
        citations.append(citation)

    promise = Promise.model_validate(promise_in, update={"citations": citations,
                                                         "candidate_id": cid})
    session.add(promise)
    session.commit()
    session.refresh(promise)

    return PromisePublic.model_validate(promise, update={"citations": [cit.id for cit in citations]})


@router.patch("/{pid}", response_model=PromisePublic)
def update_promise(session: SessionArg, cid: int, pid: int, promise_in: PromiseUpdate) -> Any:
    promise = session.get(Promise, pid)

    if not promise:
        raise HTTPException(status_code=404, detail=f"Promise with id={pid} not found for candidate with id={cid}.")

    update_dict = promise_in.model_dump(exclude_unset=True)
    promise.sqlmodel_update(update_dict)
    session.add(promise)
    session.commit()
    session.refresh(promise)

    citation_ids = _get_citation_ids_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": citation_ids})


def _get_citation_ids_helper(session: Session, promise_id: int) -> list[int]:
    query = select(Citation.id).where(Citation.promise_id == promise_id)
    citation_ids = session.exec(query).all()
    return cast(list[int], citation_ids)
