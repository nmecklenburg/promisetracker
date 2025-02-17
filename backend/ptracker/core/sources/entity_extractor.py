from abc import ABC, abstractmethod
from datetime import datetime
from openai import OpenAI, LengthFinishReasonError
from pydantic import BaseModel
from sqlmodel import select, Session
from typing import Any

from ptracker.api.models import (
    Action,
    Citation,
    Promise,
)
from ptracker.core import prompts
from ptracker.core import constants
from ptracker.core.db import engine
from ptracker.core.llm_utils import (
    cosine_similarity,
    fetch_actions_by_embedding,
    fetch_promises_by_embedding,
    get_action_embedding,
    get_promise_embedding,
)
from ptracker.core.settings import settings
from ptracker.core.utils import get_logger

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_KEY)


class LLMPromiseResponse(BaseModel):
    politician_name: str
    is_promise: bool
    promise_text: str
    exact_quote: str


class ActionInfo(BaseModel):
    text: str
    verbatim_quote: str


class LLMActionResponse(BaseModel):
    actions: list[ActionInfo]


class EntityExtractor(ABC):
    @staticmethod
    @abstractmethod
    def get_entities_from_extract(extract: str, candidate_name: str, url: str) -> list[dict[str, Any]] | None:
        pass

    @staticmethod
    @abstractmethod
    def deduplicate_entities(entity_jsons: list[dict]) -> list[dict]:
        pass

    @staticmethod
    @abstractmethod
    def add_entities_to_session(candidate_id: int, entity_jsons: list[dict]) -> None:
        pass

    @staticmethod
    def _commitless_add_citations(session: Session, citation_jsons: list[dict]) -> list[Citation]:
        citations = []
        for citation_json in citation_jsons:
            citation = Citation(**citation_json)
            citations.append(citation)
            session.add(citation)
        return citations


class PromiseExtractor(EntityExtractor):
    @staticmethod
    def get_entities_from_extract(extract: str, candidate_name: str, url: str) -> list[dict[str, Any]] | None:
        sys_prompt_template = prompts.PROMISE_EXTRACTION_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": sys_prompt_template.replace("{{name}}", candidate_name)},
            {"role": "user", "content": extract}
        ]

        try:
            response = client.beta.chat.completions.parse(
                model=settings.OPENAI_MODEL_NAME,
                messages=messages,
                max_tokens=1200,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                response_format=LLMPromiseResponse,
            )
        except LengthFinishReasonError:
            return None  # Squash this for now.

        raw_promise = response.choices[0].message.parsed

        if raw_promise is None:
            return None

        if not raw_promise.is_promise or raw_promise.exact_quote not in extract:
            logger.warning(
                "Received response that was either not a promise or which did not adhere to our requirements. "
                f"is_promise={raw_promise.is_promise} is_quote={raw_promise.exact_quote in extract}"
            )
            return None

        logger.info(f"Extracted promise: {raw_promise.promise_text}")
        logger.info(f"Verbatim extraction honored: {raw_promise.exact_quote in extract}")
        logger.info(f"Article extract: {raw_promise.exact_quote}")
        return [{
            "_timestamp": datetime.now(),
            "status": constants.PromiseStatus.PROGRESSING,
            "text": raw_promise.promise_text,
            "embedding": get_promise_embedding(raw_promise.promise_text),
            "citations": [
                {
                    "date": datetime.now(),
                    "extract": raw_promise.exact_quote,
                    "url": url,
                }
            ]
        }]

    @staticmethod
    def deduplicate_entities(entity_jsons: list[dict]) -> list[dict]:
        filtered_promise_dicts = []
        promise_idxs = set(range(len(entity_jsons)))
        while promise_idxs:
            this_idx = promise_idxs.pop()
            dup_idxs = [
                other_idx for other_idx in promise_idxs if
                cosine_similarity(entity_jsons[this_idx]['embedding'],
                                  entity_jsons[other_idx]['embedding']) >= constants.DUPLICATE_ENTITY_SIM_THRESHOLD
            ]
            # Break ties in favor of longer promise text, for now.
            longest_promise = entity_jsons[this_idx]
            for idx in dup_idxs:
                promise_idxs.remove(idx)
                dup_promise = entity_jsons[idx]
                if len(dup_promise['text']) > len(longest_promise['text']):
                    longest_promise = dup_promise

            with Session(engine) as session:
                duplicate = session.exec(
                    select(Promise).where(Promise.embedding.cosine_distance(longest_promise['embedding'])
                                          < constants.DUPLICATE_ENTITY_DIST_THRESHOLD).limit(1)
                ).first()
                # Regardless of length, existing promises take precedence.
                if duplicate is None:
                    filtered_promise_dicts.append(longest_promise)
        return filtered_promise_dicts

    @staticmethod
    def add_entities_to_session(candidate_id: int, entity_jsons: list[dict]) -> None:
        with Session(engine) as session:
            new_promises = []
            for promise_json in entity_jsons:
                citation_jsons = promise_json["citations"]
                assert len(citation_jsons) > 0, \
                    "Unexpectedly got no citations for extracted promise. This is a system error."
                citations = EntityExtractor._commitless_add_citations(session, citation_jsons)  # type: list[Citation]
                promise = Promise.model_validate(promise_json, update={"candidate_id": candidate_id})
                promise.citations = citations
                # Optimize this?
                promise.actions = fetch_actions_by_embedding(session=session,
                                                             candidate_id=candidate_id,
                                                             promise_embedding=promise.embedding)
                new_promises.append(promise)
                session.add(promise)
            session.commit()
        return


class ActionExtractor(EntityExtractor):
    @staticmethod
    def get_entities_from_extract(extract: str, candidate_name: str, url: str) -> list[dict[str, Any]] | None:
        sys_prompt_template = prompts.ACTION_EXTRACTION_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": sys_prompt_template.replace("{{name}}", candidate_name)},
            {"role": "user", "content": extract}
        ]

        try:
            response = client.beta.chat.completions.parse(
                model=settings.OPENAI_MODEL_NAME,
                messages=messages,
                max_tokens=1200,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                response_format=LLMActionResponse,
            )
        except LengthFinishReasonError:
            return None  # Squash this for now.

        action_response_object = response.choices[0].message.parsed
        action_info_list = action_response_object.actions
        if not action_info_list:
            return None

        formal_action_jsons = []
        for action_info in action_info_list:
            if action_info.verbatim_quote not in extract:
                logger.warning("Received action response without a corresponding verbatim quote, so will skip it.")
                continue
            logger.info(f"Extracted action: {action_info.text}")
            logger.info(f"Article extract: {action_info.verbatim_quote}")
            formal_action_json = {
                "date": datetime.now(),
                "text": action_info.text,
                "embedding": get_action_embedding(action_info.text),
                "citations": [
                    {
                        "date": datetime.now(),
                        "extract": action_info.verbatim_quote,
                        "url": url
                    }
                ]
            }
            formal_action_jsons.append(formal_action_json)
        return formal_action_jsons

    @staticmethod
    def deduplicate_entities(entity_jsons: list[dict]) -> list[dict]:
        filtered_action_dicts = []
        action_idxs = set(range(len(entity_jsons)))
        while action_idxs:
            this_idx = action_idxs.pop()
            dup_idxs = [
                other_idx for other_idx in action_idxs if
                cosine_similarity(entity_jsons[this_idx]['embedding'],
                                  entity_jsons[other_idx]['embedding']) >= constants.DUPLICATE_ENTITY_SIM_THRESHOLD
            ]
            # Break ties in favor of longer action text, for now.
            longest_action = entity_jsons[this_idx]
            for idx in dup_idxs:
                action_idxs.remove(idx)
                dup_action = entity_jsons[idx]
                if len(dup_action['text']) > len(dup_action['text']):
                    longest_action = dup_action

            with Session(engine) as session:
                duplicate = session.exec(
                    select(Action).where(Action.embedding.cosine_distance(longest_action['embedding'])
                                         < constants.DUPLICATE_ENTITY_DIST_THRESHOLD).limit(1)
                ).first()
                # Regardless of length, existing promises take precedence.
                if duplicate is None:
                    filtered_action_dicts.append(longest_action)
        return filtered_action_dicts

    @staticmethod
    def add_entities_to_session(candidate_id: int, entity_jsons: list[dict]) -> None:
        with Session(engine) as session:
            new_actions = []
            for action_json in entity_jsons:
                citation_jsons = action_json["citations"]
                assert len(citation_jsons) > 0, \
                    "Unexpectedly got no citations for extracted action. This is a system error."
                citations = EntityExtractor._commitless_add_citations(session, citation_jsons)  # type: list[Citation]
                action = Action.model_validate(action_json, update={"candidate_id": candidate_id})
                action.citations = citations
                # Optimize this too?
                action.promises = fetch_promises_by_embedding(session=session,
                                                              candidate_id=candidate_id,
                                                              action_embedding=action.embedding)
                new_actions.append(action)
                session.add(action)
            session.commit()
        return
