from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select
from typing import Any

from ptracker.api.models import Candidate, CandidatePublic, CandidatesPublic, Promise
from ptracker.api.models._associations import SourceCandidateLink
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
        kwargs = candidate.dict()
        kwargs["promises"] = pc_map[candidate.id]
        kwargs["sources"] = sc_map[candidate.id]
        response_candidates.append(CandidatePublic(**kwargs))

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

    public_kwargs = candidate.dict()
    public_kwargs["promises"] = promise_ids
    public_kwargs["sources"] = source_ids
    return CandidatePublic(**public_kwargs)


# @router.post("/{cid}", response_model=CandidatePublic)
# def create_candidate(session)

# TODO nmecklenburg - what does workflow look like for inserting candidates, promises, sources, etc.
