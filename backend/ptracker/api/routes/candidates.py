from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select
from typing import Any

from ptracker.api.models import (
    Candidate,
    CandidateCreate,
    CandidatePublic,
    CandidateUpdate,
    CandidatesPublic,
    Promise,
    Source,
    SourceCreate,
)
from ptracker.api.models._associations import SourceCandidateLink
from ptracker.api.routes.sources import _create_source_helper
from ptracker.core.db import SessionArg

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=CandidatesPublic)
def read_candidates(session: SessionArg, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Candidate)
    count = session.exec(count_query).one()  # one and only one result, else error

    candidate_query = select(Candidate).offset(after).limit(limit)
    candidates = session.exec(candidate_query).all()

    pc_query = (select(Promise.id, Promise.candidate_id)
                .join(Candidate)
                .where(col(Promise.candidate_id).in_([c.id for c in candidates])))
    promise_candidate_tuples = session.exec(pc_query).all()

    pc_map = {}
    for promise_id, candidate_id in promise_candidate_tuples:
        if candidate_id not in pc_map:
            pc_map[candidate_id] = []

        pc_map[candidate_id].append(promise_id)

    sc_query = (select(SourceCandidateLink.source_id, SourceCandidateLink.candidate_id)
                .where(col(SourceCandidateLink.candidate_id).in_([c.id for c in candidates])))
    source_candidate_tuples = session.exec(sc_query).all()

    sc_map = {}
    for source_id, candidate_id in source_candidate_tuples:
        if source_id not in sc_map:
            sc_map[candidate_id] = []

        sc_map[candidate_id].append(source_id)

    response_candidates = []
    for candidate in candidates:
        response_candidate = CandidatePublic.model_validate(candidate,
                                                            update={"promises": pc_map.get(candidate.id, []),
                                                                    "sources": sc_map.get(candidate.id, [])})
        response_candidates.append(response_candidate)

    return CandidatesPublic(data=response_candidates, count=count)


@router.get("/{cid}", response_model=CandidatePublic)
def read_candidate(session: SessionArg, cid: int) -> Any:
    candidate = session.get(Candidate, cid)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={cid} not found.")

    # TODO nmecklenburg ... out of personal curiosity, what's the delta of simple looping through `.promises`
    #  and accessing id attrs
    query = select(Promise.id).where(Promise.candidate_id == candidate.id)
    promise_ids = session.exec(query).all()

    query = select(SourceCandidateLink.source_id).where(SourceCandidateLink.candidate_id == candidate.id)
    source_ids = session.exec(query).all()

    return CandidatePublic.model_validate(candidate, update={"promises": promise_ids, "sources": source_ids})


@router.post("/", response_model=CandidatePublic)
def create_candidate(session: SessionArg, candidate_in: CandidateCreate) -> Any:
    sources = []
    for source_or_id in candidate_in.sources:
        if isinstance(source_or_id, SourceCreate):
            sources.append(_create_source_helper(session, source_or_id))
        elif isinstance(source_or_id, int):
            this_source = session.get(Source, source_or_id)
            if not this_source:
                return HTTPException(status_code=400, detail=f"Tried to create candidate with a nonexistent source. "
                                                             f"Source with id {source_or_id} not found.")
            sources.append(this_source)

    candidate = Candidate.model_validate(candidate_in, update={"sources": sources})
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    return CandidatePublic.model_validate(candidate, update={"sources": [s.id for s in sources],
                                                             "promises": []})


@router.patch("/{cid}", response_model=CandidatePublic)
def update_candidate(session: SessionArg, candidate_in: CandidateUpdate) -> Any:
    pass