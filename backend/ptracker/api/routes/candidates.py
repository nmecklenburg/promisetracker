from fastapi import APIRouter, HTTPException
from typing import Any

from ptracker.api.models import Candidate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/{cid}", response_model=Candidate)
def read_candidate(session, cid: int) -> Any:
    candidate = session.get(Candidate, cid)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id={cid} not found.")
    return candidate


# @router.post("/{cid}", response_model=Candidate)
# def create_candidate(session)

# TODO nmecklenburg - what does workflow look like for inserting candidates, promises, sources, etc.
