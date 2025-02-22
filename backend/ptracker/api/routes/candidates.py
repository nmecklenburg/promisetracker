from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import Session, col, func, select
from typing import Any

from ptracker.api.models import (
    Action,
    Candidate,
    CandidateCreate,
    CandidatePublic,
    CandidateUpdate,
    CandidatesPublic,
    Promise,
    SourceRequest,
    SourceResponse,
)
from ptracker.core.constants import PromiseExtractionPhase
from ptracker.core.db import SessionArg
from ptracker.core.sources import analyze_sources
from ptracker.core.utils import get_logger

router = APIRouter(prefix="/candidates", tags=["candidates"])

logger = get_logger(__name__)


@router.get("/", response_model=CandidatesPublic)
def read_candidates(session: SessionArg, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Candidate)
    count = session.exec(count_query).one()  # one and only one result, else error

    candidate_query = select(Candidate).offset(after).limit(limit)
    candidates = session.exec(candidate_query).all()
    candidate_ids = [c.id for c in candidates]

    promise_candidate_query = \
        select(Promise.id, Promise.candidate_id).where(col(Promise.candidate_id).in_(candidate_ids))
    promise_candidate_tuples = session.exec(promise_candidate_query).all()

    pc_map = {}
    for promise_id, candidate_id in promise_candidate_tuples:
        if candidate_id not in pc_map:
            pc_map[candidate_id] = 0
        pc_map[candidate_id] += 1

    action_candidate_query = \
        select(Action.id, Action.candidate_id).where(col(Action.candidate_id).in_(candidate_ids))
    action_candidate_tuples = session.exec(action_candidate_query).all()

    ac_map = {}
    for action_id, candidate_id in action_candidate_tuples:
        if candidate_id not in ac_map:
            ac_map[candidate_id] = 0
        ac_map[candidate_id] += 1

    response_candidates = []
    for candidate in candidates:
        response_candidate = CandidatePublic.model_validate(candidate,
                                                            update={"promises": pc_map.get(candidate.id, 0),
                                                                    "actions": ac_map.get(candidate.id, 0)})
        response_candidates.append(response_candidate)

    return CandidatesPublic(data=response_candidates, count=count)


@router.get("/{candidate_id}", response_model=CandidatePublic)
def read_candidate(session: SessionArg, candidate_id: int) -> Any:
    candidate = session.get(Candidate, candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={candidate_id} not found.")

    num_promises = _get_promises_helper(session, candidate.id)
    num_actions = _get_actions_helper(session, candidate.id)
    return CandidatePublic.model_validate(candidate, update={"promises": num_promises,
                                                             "actions": num_actions})


@router.post("/", response_model=CandidatePublic)
def create_candidate(session: SessionArg, candidate_in: CandidateCreate) -> Any:
    maybe_stringified_profile_pic = None
    if candidate_in.profile_image_url is not None:
        maybe_stringified_profile_pic = str(candidate_in.profile_image_url)
    candidate = Candidate.model_validate(candidate_in, update={"profile_image_url": maybe_stringified_profile_pic})
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    return CandidatePublic.model_validate(candidate, update={"promises": 0,
                                                             "actions": 0})


@router.patch("/{candidate_id}", response_model=CandidatePublic)
def update_candidate(session: SessionArg, candidate_id: int, candidate_in: CandidateUpdate) -> Any:
    candidate = session.get(Candidate, candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={candidate_id} not found.")

    update_dict = candidate_in.model_dump(exclude_unset=True)
    if candidate_in.profile_image_url is not None:
        update_dict["profile_image_url"] = str(candidate_in.profile_image_url)

    candidate.sqlmodel_update(update_dict)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    num_promises = _get_promises_helper(session, candidate.id)
    num_actions = _get_actions_helper(session, candidate.id)
    return CandidatePublic.model_validate(candidate, update={"promises": num_promises,
                                                             "actions": num_actions})


@router.post("/{candidate_id}/sources", response_model=SourceResponse)
def add_candidate_sources(
        session: SessionArg,
        candidate_id: int,
        sources: SourceRequest,
        background_tasks: BackgroundTasks
) -> Any:
    # Main entrypoint to do promise extraction.
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={candidate_id} not found.")

    stringified_urls = [str(url) for url in sources.urls]
    background_tasks.add_task(analyze_sources, candidate, stringified_urls)

    return SourceResponse(status=PromiseExtractionPhase.STARTED)


def _get_promises_helper(session: Session, candidate_id: int) -> int:
    query = select(func.count()).select_from(Promise).where(Promise.candidate_id == candidate_id)
    num_promises = session.exec(query).one()
    return num_promises


def _get_actions_helper(session: Session, candidate_id: int) -> int:
    query = select(func.count()).select_from(Action).where(Action.candidate_id == candidate_id)
    num_actions = session.exec(query).one()
    return num_actions
