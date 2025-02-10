from fastapi import APIRouter, HTTPException
from sqlmodel import and_, col, func, select, Session
from typing import Any

from ptracker.api.models import (
    Citation,
    Promise,
    PromiseCreate,
    PromisePublic,
    PromisesPublic,
    PromiseUpdate,
)
from ptracker.core.db import SessionArg
from ptracker.core.llm_utils import get_promise_embedding

router = APIRouter(prefix="/candidates/{candidate_id}/promises", tags=["promises"])


@router.get("/", response_model=PromisesPublic)
def read_promises(session: SessionArg, candidate_id: int, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Promise).where(Promise.candidate_id == candidate_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    promise_query = select(Promise).where(Promise.candidate_id == candidate_id).offset(after).limit(limit)
    promises = session.exec(promise_query).all()

    cp_query = (select(Citation.id, Citation.promise_id)
                .where(col(Citation.promise_id).in_([p.id for p in promises])))
    citation_promise_tuples = session.exec(cp_query).all()

    cp_map = {}
    for citation_id, promise_id in citation_promise_tuples:
        if promise_id not in cp_map:
            cp_map[promise_id] = 0

        cp_map[promise_id] += 1

    response_promises = []
    for promise in promises:
        response_promise = PromisePublic.model_validate(promise,
                                                        update={"citations": cp_map.get(promise.id, 0)})
        response_promises.append(response_promise)

    return PromisesPublic(data=response_promises, count=count)


@router.get("/{promise_id}", response_model=PromisePublic)
def read_promise(session: SessionArg, candidate_id: int, promise_id: int) -> Any:
    promise = session.get(Promise, promise_id)

    if not promise or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Promise with id={promise_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    num_citations = _get_citation_count_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": num_citations})


@router.post("/", response_model=PromisePublic)
def create_promise(session: SessionArg, candidate_id: int, promise_in: PromiseCreate) -> Any:
    embedding = get_promise_embedding(promise_in.text)
    duplicates = session.exec(select(Promise).filter(Promise.embedding.cosine_distance(embedding) < 0.3)).all()
    if duplicates:
        raise HTTPException(status_code=400, detail=f"Promise with text {promise_in.text} may be a duplicate of "
                                                    f"promises {[d.id for d in duplicates]}.")

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
                                                         "candidate_id": candidate_id,
                                                         "embedding": embedding})
    session.add(promise)
    session.commit()
    session.refresh(promise)

    return PromisePublic.model_validate(promise, update={"citations": len(citations)})


@router.patch("/{promise_id}", response_model=PromisePublic)
def update_promise(session: SessionArg, candidate_id: int, promise_id: int, promise_in: PromiseUpdate) -> Any:
    embedding = get_promise_embedding(promise_in.text)
    duplicates = session.exec(select(Promise).filter(and_(Promise.id != promise_id,
                                                          Promise.embedding.cosine_distance(embedding) < 0.3))).all()
    if duplicates:
        raise HTTPException(status_code=400, detail=f"Promise with text {promise_in.text} may be a duplicate of "
                                                    f"promises {[d.id for d in duplicates]}.")
    promise = session.get(Promise, promise_id)

    if not promise or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Promise with id={promise_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    update_dict = promise_in.model_dump(exclude_unset=True)
    if promise_in.text and promise_in.text != promise.text:
        # Update embedding
        update_dict['embedding'] = get_promise_embedding(promise_in.text)
    promise.sqlmodel_update(update_dict)
    session.add(promise)
    session.commit()
    session.refresh(promise)

    num_citations = _get_citation_count_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": num_citations})


def _get_citation_count_helper(session: Session, promise_id: int) -> int:
    query = select(func.count()).select_from(Citation).where(Citation.promise_id == promise_id)
    num_citations = session.exec(query).one()
    return num_citations
