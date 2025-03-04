from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import and_, col, func, select, Session
from typing import Any

from ptracker.api.models import (
    Action,
    ActionCreate,
    ActionPublic,
    ActionsPublic,
    ActionUpdate,
    Citation,
    Promise,
    PromiseActionLink,
)
from ptracker.core import constants
from ptracker.core.db import SessionArg
from ptracker.core.llm_utils import get_action_embedding, fetch_promises_by_embedding
from ptracker.core.settings import settings

router = APIRouter(prefix="/candidates/{candidate_id}/actions", tags=["actions"])
nested_promise_router = APIRouter(prefix="/candidates/{candidate_id}/promises/{promise_id}/actions", tags=["actions"])


@router.get("/", response_model=ActionsPublic)
def read_actions(session: SessionArg, candidate_id: int, after: int = 0, limit: int = 100) -> Any:
    count_query = select(func.count()).select_from(Action).where(Action.candidate_id == candidate_id)
    count = session.exec(count_query).one()  # one and only one result, else error

    action_query = select(Action).where(Action.candidate_id == candidate_id).offset(after).limit(limit)
    actions = session.exec(action_query).all()
    response_actions = _publicize_actions(session, actions)

    return ActionsPublic(data=response_actions, count=count)


@nested_promise_router.get("/", response_model=ActionsPublic)
def read_nested_actions(
        session: SessionArg,
        candidate_id: int,
        promise_id: int,
        after: int = 0,
        limit: int = 100
) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)

    count_query = select(func.count()).select_from(PromiseActionLink).where(PromiseActionLink.promise_id == promise_id)
    count = session.exec(count_query).one()  # all actions linked with the requested promise

    action_query = (select(Action)
                    .join(PromiseActionLink)
                    .where(PromiseActionLink.promise_id == promise_id)
                    .offset(after)
                    .limit(limit))
    actions = session.exec(action_query).all()
    response_actions = _publicize_actions(session, actions)

    return ActionsPublic(data=response_actions, count=count)


@router.get("/{action_id}", response_model=ActionPublic)
def read_action(session: SessionArg, candidate_id: int, action_id: int) -> Any:
    action = session.get(Action, action_id)

    if not action or action.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Action with id={action_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    num_citations = _get_citation_count_helper(session, action.id)
    num_promises = _get_promise_count_helper(session, action.id)
    return ActionPublic.model_validate(action, update={"citations": num_citations,
                                                       "promises": num_promises})


@nested_promise_router.get("/{action_id}")
def read_nested_action(session: SessionArg, candidate_id: int, promise_id: int, action_id: int) -> Any:
    _validate_promise(session=session, candidate_id=candidate_id, promise_id=promise_id)
    redirect_uri = settings.API_VERSION_STRING + router.prefix + "/{action_id}"
    return RedirectResponse(redirect_uri.format(candidate_id=candidate_id, action_id=action_id))


@router.post("/", response_model=ActionPublic)
def create_action(session: SessionArg, candidate_id: int, action_in: ActionCreate) -> Any:
    action_embedding = get_action_embedding(action_in.text)
    duplicates = session.exec(
        select(Action).where(Action.embedding.cosine_distance(action_embedding)
                             < constants.DUPLICATE_ENTITY_DIST_THRESHOLD)
    ).all()
    if duplicates:
        raise HTTPException(status_code=400, detail=f"Action with text {action_in.text} may be a duplicate of "
                                                    f"actions {[d.id for d in duplicates]}.")

    promises = []
    if action_in.promises:
        promise_query = (select(Promise).where(col(Promise.id).in_(action_in.promises)))
        promises = session.exec(promise_query).all()

        num_requested_promises = len(action_in.promises)
        num_found_promises = len(promises)
        if num_found_promises < num_requested_promises:
            missing_promise_ids = set(p.id for p in promises) - set(action_in.promises)
            raise HTTPException(status_code=400, detail=f"Requested to match {num_requested_promises} promises to "
                                                        f"newly created action, but only {num_found_promises} of them "
                                                        f"were found. Missing promise IDs: {missing_promise_ids}.")

        malformed_promises = [p.id for p in promises if p.candidate_id != candidate_id]
        if malformed_promises:
            raise HTTPException(status_code=400, detail=f"Actions must be mapped to promises of the "
                                                        f"same candidate, but requested promises {malformed_promises} "
                                                        f"are not associated with {candidate_id=}.")

    auto_assigned_promises = fetch_promises_by_embedding(session=session,
                                                         candidate_id=candidate_id,
                                                         action_embedding=action_embedding)
    seen = {p.id for p in promises}
    for auto_assigned_promise in auto_assigned_promises:
        # If user has already requested this promise to be manually added, no need to duplicate.
        if auto_assigned_promise.id not in seen:
            promises.append(auto_assigned_promise)

    # We disallow the creation of actions without citations, meaning we must create citations
    # as part of this action creation flow.
    citations = []
    # Length validations taken care of at Pydantic layer. There should be at least one.
    for citation_in in action_in.citations:
        citation_kwargs = citation_in.model_dump()
        citation_kwargs.update({"url": str(citation_in.url)})
        citation = Citation(**citation_kwargs)

        session.add(citation)
        citations.append(citation)

    action = Action.model_validate(action_in, update={"citations": citations,
                                                      "promises": promises,
                                                      "candidate_id": candidate_id,
                                                      "embedding": action_embedding})
    session.add(action)
    session.commit()
    session.refresh(action)

    return ActionPublic.model_validate(action, update={"citations": len(citations),
                                                       "promises": len(promises)})


@router.patch("/{action_id}", response_model=ActionPublic)
def update_action(session: SessionArg, candidate_id: int, action_id: int, action_in: ActionUpdate) -> Any:
    updated_action_embedding = None
    if action_in.text is not None:
        updated_action_embedding = get_action_embedding(action_in.text)
        duplicates = session.exec(
            select(Action).where(and_(Action.id != action_id,
                                      Action.embedding.cosine_distance(updated_action_embedding)
                                      < constants.DUPLICATE_ENTITY_DIST_THRESHOLD))
        ).all()
        if duplicates:
            raise HTTPException(status_code=400, detail=f"Action with text '{action_in.text}' may be a duplicate of "
                                                        f"actions {[d.id for d in duplicates]}.")

    action = session.get(Action, action_id)

    if not action or action.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Action with id={action_id} not found for candidate "
                                                    f"with id={candidate_id}.")

    update_dict = action_in.model_dump(exclude_unset=True)
    if updated_action_embedding is not None and action_in.text != action.text:
        # Text changed, resulting in a new embedding => update for this action.
        update_dict['embedding'] = updated_action_embedding
    action.sqlmodel_update(update_dict)

    # Auto-assign promises
    auto_assigned_promises = fetch_promises_by_embedding(session=session,
                                                         candidate_id=candidate_id,
                                                         action_embedding=updated_action_embedding)
    seen = {p.id for p in action.promises}
    num_promises = len(seen)
    for auto_assigned_promise in auto_assigned_promises:
        if auto_assigned_promise.id not in seen:
            action.promises.append(auto_assigned_promise)
            num_promises += 1

    session.add(action)
    session.commit()
    session.refresh(action)

    num_citations = _get_citation_count_helper(session, action.id)
    return ActionPublic.model_validate(action, update={"citations": num_citations,
                                                       "promises": num_promises})


def _get_citation_count_helper(session: Session, action_id: int) -> int:
    query = select(func.count()).select_from(Citation).where(Citation.action_id == action_id)
    num_citations = session.exec(query).one()
    return num_citations


def _get_promise_count_helper(session: Session, action_id: int) -> int:
    query = select(func.count()).select_from(PromiseActionLink).where(PromiseActionLink.action_id == action_id)
    num_promises = session.exec(query).one()
    return num_promises


def _publicize_actions(session: Session, actions: list[Action]) -> list[ActionPublic]:
    action_ids = [a.id for a in actions]

    # Fetch num citations without O(P) database calls
    citation_action_query = select(Citation.id, Citation.action_id).where(col(Citation.action_id).in_(action_ids))
    citation_action_tuples = session.exec(citation_action_query).all()
    ca_map = {}
    for citation_id, action_id in citation_action_tuples:
        if action_id not in ca_map:
            ca_map[action_id] = 0
        ca_map[action_id] += 1

    # Fetch num promises without O(P) database calls
    promise_action_query = (select(PromiseActionLink.promise_id, PromiseActionLink.action_id)
                            .where(col(PromiseActionLink.action_id).in_(action_ids)))
    promise_action_tuples = session.exec(promise_action_query).all()
    pa_map = {}
    for promise_id, action_id in promise_action_tuples:
        if action_id not in pa_map:
            pa_map[action_id] = 0
        pa_map[action_id] += 1

    response_actions = []
    for action in actions:
        response_action = ActionPublic.model_validate(action,
                                                      update={"citations": ca_map.get(action.id, 0),
                                                              "promises": pa_map.get(action.id, 0)})
        response_actions.append(response_action)
    return response_actions


def _validate_promise(session: Session, candidate_id: int, promise_id: int) -> None:
    promise = session.get(Promise, promise_id)
    if promise is None or promise.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail=f"Page for {promise_id=} {candidate_id=} does not exist. "
                                                    f"Did you get the IDs mixed up?")
    return None
