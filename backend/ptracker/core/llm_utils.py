from openai import OpenAI
from sqlmodel import and_, col, select, Session
from typing import cast, Any

import logging
import numpy as np

from ptracker.api.models import Action, Promise
from ptracker.core import constants
from ptracker.core.settings import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_KEY)


def get_promise_embedding(text: str) -> Any:
    return client.embeddings.create(
        input=text,
        model="text-embedding-3-large",
        encoding_format="float",
        dimensions=settings.PROMISE_EMBEDDING_DIM,
    ).data[0].embedding


def get_action_embedding(text: str) -> Any:
    return client.embeddings.create(
        input=text,
        model="text-embedding-3-large",
        encoding_format="float",
        dimensions=settings.ACTION_EMBEDDING_DIM,
    ).data[0].embedding


def fetch_promises_by_embedding(session: Session, candidate_id: int, action_embedding: list[float]) -> list[Promise]:
    auto_assigned_promises = session.exec(
        select(Promise).where(
            and_(Promise.candidate_id == candidate_id,
                 Promise.embedding.cosine_distance(action_embedding) < constants.PROMISE_ACTION_DIST_THRESHOLD)
        )
    ).all()

    return cast(list[Promise], auto_assigned_promises)


def fetch_actions_by_embedding(session: Session, candidate_id: int, promise_embedding: list[float]) -> list[Action]:
    auto_assigned_actions = session.exec(
        select(Action).where(
            and_(Action.candidate_id == candidate_id,
                 Action.embedding.cosine_distance(promise_embedding) < constants.PROMISE_ACTION_DIST_THRESHOLD)
        )
    ).all()

    return cast(list[Action], auto_assigned_actions)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Assumes embeddings are *already normalized*, which is true for OpenAI models.
    return np.dot(a, b)
