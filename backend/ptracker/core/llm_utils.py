from openai import OpenAI
from typing import Any

import logging
import numpy as np

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


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Assumes embeddings are *already normalized*, which is true for OpenAI models.
    return np.dot(a, b)
