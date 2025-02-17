from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import and_, col, func, select, Session
from typing import Any

from ptracker.api.models import (
    Action,
    Citation,
    Promise,
    PromiseActionLink,
    PromiseCreate,
    PromisePublic,
    PromisesPublic,
    PromiseUpdate,
)
from ptracker.core import constants
from ptracker.core.db import SessionArg
from ptracker.core.llm_utils import get_promise_embedding, fetch_actions_by_embedding

router = APIRouter(prefix="/candidates/{candidate_id}/promises", tags=["promises"])
nested_action_router = APIRouter(prefix="/candidates/{candidate_id}/actions/{action_id}/promises", tags=["promises"])


@router.get("/", response_model=PromisesPublic)
def read_promises(session: SessionArg, candidate_id: int, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Promise).where(Promise.candidate_id == candidate_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    promise_query = select(Promise).where(Promise.candidate_id == candidate_id).offset(after).limit(limit)
    promises = session.exec(promise_query).all()
    response_promises = _publicize_promises(session, promises)

    return PromisesPublic(data=response_promises, count=count)


@nested_action_router.get("/", response_model=PromisesPublic)
def read_nested_promises(
        session: SessionArg,
        candidate_id: int,
        action_id: int,
        after: int = 0,
        limit: int = 100
) -> Any:
    _validate_action(session=session, candidate_id=candidate_id, action_id=action_id)

    count_query = select(func.count()).select_from(PromiseActionLink).where(PromiseActionLink.action_id == action_id)
    count = session.exec(count_query).one()  # all promises linked with the requested action

    promise_query = (select(Promise)
                     .join(PromiseActionLink)
                     .where(PromiseActionLink.action_id == action_id)
                     .offset(after)
                     .limit(limit))
    promises = session.exec(promise_query).all()
    response_promises = _publicize_promises(session, promises)

    return PromisesPublic(data=response_promises, count=count)


@router.get("/{promise_id}", response_model=PromisePublic)
def read_promise(session: SessionArg, candidate_id: int, promise_id: int) -> Any:
    promise = session.get(Promise, promise_id)

    if not promise or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Promise with id={promise_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    num_citations = _get_citation_count_helper(session, promise.id)
    num_actions = _get_action_count_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": num_citations,
                                                         "actions": num_actions})


@nested_action_router.get("/{promise_id}")
def read_nested_promise(session: SessionArg, candidate_id: int, action_id: int, promise_id: int) -> Any:
    _validate_action(session=session, candidate_id=candidate_id, action_id=action_id)
    redirect_uri = router.prefix + "/{promise_id}"
    return RedirectResponse(redirect_uri.format(candidate_id=candidate_id, promise_id=promise_id))


@router.post("/", response_model=PromisePublic)
def create_promise(session: SessionArg, candidate_id: int, promise_in: PromiseCreate) -> Any:
    promise_embedding = get_promise_embedding(promise_in.text)
    duplicates = session.exec(
        select(Promise).where(Promise.embedding.cosine_distance(promise_embedding)
                              < constants.DUPLICATE_ENTITY_DIST_THRESHOLD)
    ).all()
    if duplicates:
        raise HTTPException(status_code=400, detail=f"Promise with text {promise_in.text} may be a duplicate of "
                                                    f"promises {[d.id for d in duplicates]}.")

    actions = []
    if promise_in.actions:
        action_query = (select(Action)
                        .join(PromiseActionLink)
                        .where(col(PromiseActionLink.action_id).in_(promise_in.actions)))
        actions = session.exec(action_query).all()

        num_requested_actions = len(promise_in.actions)
        num_found_actions = len(actions)
        if num_found_actions < num_requested_actions:
            missing_action_ids = set(a.id for a in actions) - set(promise_in.actions)
            raise HTTPException(status_code=400, detail=f"Requested to match {num_requested_actions} actions to newly "
                                                        f"created promise, but only {num_found_actions} of them were "
                                                        f"found. Missing action IDs: {missing_action_ids}.")

        malformed_actions = [a.id for a in actions if a.candidate_id != candidate_id]
        if malformed_actions:
            raise HTTPException(status_code=400, detail=f"Promises must be mapped to actions of the "
                                                        f"same candidate, but requested actions {malformed_actions} "
                                                        f"are not associated with {candidate_id=}.")

    auto_assigned_actions = fetch_actions_by_embedding(session=session,
                                                       candidate_id=candidate_id,
                                                       promise_embedding=promise_embedding)
    seen = {a.id for a in actions}
    for auto_assigned_action in auto_assigned_actions:
        # If user has already requested this action to be manually added, no need to duplicate.
        if auto_assigned_action.id not in seen:
            actions.append(auto_assigned_action)

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
                                                         "actions": actions,
                                                         "candidate_id": candidate_id,
                                                         "embedding": promise_embedding})
    session.add(promise)
    session.commit()
    session.refresh(promise)

    return PromisePublic.model_validate(promise, update={"citations": len(citations),
                                                         "actions": len(actions)})


@router.patch("/{promise_id}", response_model=PromisePublic)
def update_promise(session: SessionArg, candidate_id: int, promise_id: int, promise_in: PromiseUpdate) -> Any:
    updated_promise_embedding = None
    if promise_in.text is not None:
        updated_promise_embedding = get_promise_embedding(promise_in.text)
        duplicates = session.exec(
            select(Promise).where(and_(Promise.id != promise_id,
                                       Promise.embedding.cosine_distance(updated_promise_embedding)
                                       < constants.DUPLICATE_ENTITY_DIST_THRESHOLD))
        ).all()
        if duplicates:
            raise HTTPException(status_code=400, detail=f"Promise with text '{promise_in.text}' may be a duplicate of "
                                                        f"promises {[d.id for d in duplicates]}.")

    promise = session.get(Promise, promise_id)

    if not promise or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Promise with id={promise_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    update_dict = promise_in.model_dump(exclude_unset=True)
    if updated_promise_embedding is not None and promise_in.text != promise.text:
        # Text changed, resulting in a new embedding => update for this promise.
        update_dict['embedding'] = updated_promise_embedding
    promise.sqlmodel_update(update_dict)

    # Auto-assign actions
    auto_assigned_actions = fetch_actions_by_embedding(session=session,
                                                       candidate_id=candidate_id,
                                                       promise_embedding=updated_promise_embedding)
    seen = {a.id for a in promise.actions}
    num_actions = len(seen)
    for auto_assigned_action in auto_assigned_actions:
        if auto_assigned_action.id not in seen:
            promise.actions.append(auto_assigned_action)
            num_actions += 1

    session.add(promise)
    session.commit()
    session.refresh(promise)

    num_citations = _get_citation_count_helper(session, promise.id)
    return PromisePublic.model_validate(promise, update={"citations": num_citations,
                                                         "actions": num_actions})


def _get_citation_count_helper(session: Session, promise_id: int) -> int:
    query = select(func.count()).select_from(Citation).where(Citation.promise_id == promise_id)
    num_citations = session.exec(query).one()
    return num_citations


def _get_action_count_helper(session: Session, promise_id: int) -> int:
    query = select(func.count()).select_from(PromiseActionLink).where(PromiseActionLink.promise_id == promise_id)
    num_actions = session.exec(query).one()
    return num_actions


def _publicize_promises(session: Session, promises: list[Promise]) -> list[PromisePublic]:
    promise_ids = [p.id for p in promises]

    # Fetch num citations without O(P) database calls
    citation_promise_query = select(Citation.id, Citation.promise_id).where(col(Citation.promise_id).in_(promise_ids))
    citation_promise_tuples = session.exec(citation_promise_query).all()
    cp_map = {}
    for citation_id, promise_id in citation_promise_tuples:
        if promise_id not in cp_map:
            cp_map[promise_id] = 0
        cp_map[promise_id] += 1

    # Fetch num actions without O(P) database calls
    action_promise_query = (select(PromiseActionLink.action_id, PromiseActionLink.promise_id)
                            .where(col(PromiseActionLink.promise_id).in_(promise_ids)))
    action_promise_tuples = session.exec(action_promise_query).all()
    ap_map = {}
    for action_id, promise_id in action_promise_tuples:
        if promise_id not in ap_map:
            ap_map[promise_id] = 0
        ap_map[promise_id] += 1

    response_promises = []
    for promise in promises:
        response_promise = PromisePublic.model_validate(promise,
                                                        update={"citations": cp_map.get(promise.id, 0),
                                                                "actions": ap_map.get(promise.id, 0)})
        response_promises.append(response_promise)
    return response_promises


def _validate_action(session: Session, candidate_id: int, action_id: int) -> None:
    action = session.get(Action, action_id)
    if action is None or action.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Page for {action_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")
    return None
