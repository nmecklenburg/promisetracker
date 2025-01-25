from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select, Session
from typing import Any

from ptracker.api.models import (
    Candidate,
    CandidateCreate,
    CandidatePublic,
    CandidateUpdate,
    CandidatesPublic,
    Citation,
    Promise,
    SourceRequest
)
from ptracker.core.db import SessionArg
from ptracker.core.source_analyzer import extract_promises

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=CandidatesPublic)
def read_candidates(session: SessionArg, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Candidate)
    count = session.exec(count_query).one()  # one and only one result, else error

    candidate_query = select(Candidate).offset(after).limit(limit)
    candidates = session.exec(candidate_query).all()

    pc_query = (select(Promise.id, Promise.candidate_id)
                .where(col(Promise.candidate_id).in_([c.id for c in candidates])))
    promise_candidate_tuples = session.exec(pc_query).all()

    pc_map = {}
    for promise_id, candidate_id in promise_candidate_tuples:
        if candidate_id not in pc_map:
            pc_map[candidate_id] = 0

        pc_map[candidate_id] += 1

    response_candidates = []
    for candidate in candidates:
        response_candidate = CandidatePublic.model_validate(candidate,
                                                            update={"promises": pc_map.get(candidate.id, 0)})
        response_candidates.append(response_candidate)

    return CandidatesPublic(data=response_candidates, count=count)


@router.get("/{cid}", response_model=CandidatePublic)
def read_candidate(session: SessionArg, cid: int) -> Any:
    candidate = session.get(Candidate, cid)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={cid} not found.")

    num_promises = _get_promises_helper(session, candidate.id)
    return CandidatePublic.model_validate(candidate, update={"promises": num_promises})


@router.post("/", response_model=CandidatePublic)
def create_candidate(session: SessionArg, candidate_in: CandidateCreate) -> Any:
    candidate = Candidate.model_validate(candidate_in)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    return CandidatePublic.model_validate(candidate, update={"promises": 0})


@router.patch("/{cid}", response_model=CandidatePublic)
def update_candidate(session: SessionArg, cid: int, candidate_in: CandidateUpdate) -> Any:
    candidate = session.get(Candidate, cid)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={cid} not found.")

    update_dict = candidate_in.model_dump(exclude_unset=True)
    candidate.sqlmodel_update(update_dict)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    num_promises = _get_promises_helper(session, candidate.id)
    return CandidatePublic.model_validate(candidate, update={"promises": num_promises})


def _get_promises_helper(session: Session, candidate_id: int) -> int:
    query = select(func.count()).select_from(Promise).where(Promise.candidate_id == candidate_id)
    num_promises = session.exec(query).one()
    return num_promises


@router.post("/{cid}/sources")  #, response_model=CandidatePublic)
def add_candidate_sources(session: SessionArg, cid: int, sources: SourceRequest):
    # Main entrypoint to do promise extraction.
    promise_creation_jsons: list[dict] = extract_promises(cast(list[str], sources.urls))
    new_promises = []
    for promise_json in promise_creation_jsons:
        citation_jsons = promise_json["citations"]
        assert len(citation_jsons) > 0, "Unexpected got no citations for extracted promise. This is a system error."
        citations = _commitless_citation_helper(session, citation_jsons)  # type: list[Citation]
        promise = Promise.parse_obj(promise_json, update={"citations": citations})
        new_promises.append(promise)
        session.add(promise)

    session.commit()

    for promise in new_promises:
        session.refresh(promise)

    candidate = session.get(Candidate, cid)
    candidate.sqlmodel_update({"promises": candidate.promises + new_promises})
    candidate.promises.extend(promises)
    session.


def _commitless_citation_helper(session: Session, citation_jsons: list[dict]) -> list[Citation]:
    # TODO: this probably belongs elsewhere
    citations = []
    for citation_json in citation_jsons:
        citation = Citation.parse_obj(citation_json)
        citations.append(citation)
        session.add(citation)
    return citations
