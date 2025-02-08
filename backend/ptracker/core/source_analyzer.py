from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel
from sqlmodel import Session
from typing import Any, Generator

import requests

from ptracker.api.models import (
    Candidate,
    Citation,
    Promise,
)
from ptracker.core import prompts
from ptracker.core.constants import PromiseStatus
from ptracker.core.db import engine
from ptracker.core.settings import settings
from ptracker.core.utils import get_logger

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_KEY)


class LLMPromiseResponse(BaseModel):
    politician_name: str
    is_promise: bool
    promise_text: str
    exact_quote: str


def extract_promises(
    candidate: Candidate, urls: list[str]
) -> None:
    promise_creation_jsons = construct_promise_jsons(name=candidate.name, urls=urls)
    # Only spin up session connection once I/O calls to OpenAI are complete.
    with (Session(engine) as session):
        new_promises = []
        for promise_json in promise_creation_jsons:
            citation_jsons = promise_json["citations"]
            assert len(citation_jsons) > 0, \
                "Unexpectedly got no citations for extracted promise. This is a system error."
            citations = _commitless_add_citations(session, citation_jsons)  # type: list[Citation]
            promise = Promise.model_validate(promise_json, update={"candidate_id": candidate.id})
            promise.citations = citations
            new_promises.append(promise)
            session.add(promise)
        session.commit()
    return


def _commitless_add_citations(session: Session, citation_jsons: list[dict]) -> list[Citation]:
    citations = []
    for citation_json in citation_jsons:
        citation = Citation(**citation_json)
        citations.append(citation)
        session.add(citation)
    return citations


def construct_promise_jsons(name: str, urls: list[str]) -> list[dict]:
    # Hmm, for a future phase -- should we try to bypass paywalls? Probably not
    # For now, assume all content is easily accessible.
    promise_dicts = []
    logger.info(f"Received {len(urls)} urls for candidate {name}. Beginning promise extraction; "
                f"looping through them now.")
    for url in urls:
        text = _get_article_text(url)
        if not text:
            logger.warning(f"Failed to extract text from {url}.")
            continue

        for idx, extract in enumerate(_chunked_text_iterator(text)):
            promise_dict = _get_promises_from_extract(extract=extract, candidate_name=name, url=url)
            if promise_dict is None:
                logger.info(f"Did not extract any promises from chunk {idx} of {url} for candidate {name}.")
            else:
                promise_dicts.append(promise_dict)
    return promise_dicts


def _get_article_text(url: str) -> str | None:
    response = requests.get(url)
    if response.status_code == 200:  # brittle?
        text = BeautifulSoup(response.text, "html.parser").get_text()
        return text
    else:
        logger.warning(f"In trying to visit '{url}' as part of promise extraction flow, "
                       f"received unhappy status code {response.status_code}.")
        return None


def _get_article_text_wiki_test(url: str) -> str | None:
    response = requests.get(url)
    if response.status_code == 200:  # brittle?
        text = BeautifulSoup(response.text, "html.parser").get_text()
        return text[:len(text) // 2]
    else:
        logger.warning(f"In trying to visit '{url}' as part of promise extraction flow, "
                       f"received unhappy status code {response.status_code}.")
        return None


def _get_article_text_wiki_test_subsample(url: str) -> str | None:
    response = requests.get(url)
    sections = ["campaign", "election"]
    paragraphs = []
    capturing = False
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        for section in sections:
            for tag in soup.find_all(["h2", "h3", "p"]):
                if tag.name in {"h2", "h3"} and section.lower() == tag.get_text().lower():
                    capturing = True
                elif tag.name in {"h2", "h3"} and capturing:
                    break
                elif capturing and tag.name == "p":
                    paragraphs.append(tag.get_text())
    return '\n'.join(paragraphs)


def _chunked_text_iterator(text: str) -> Generator[str, None, None]:
    for idx in range(0, len(text), settings.CITATION_EXTRACT_LENGTH):
        yield text[idx:idx + settings.CITATION_EXTRACT_LENGTH * 2]


def _get_promises_from_extract(extract: str, candidate_name: str, url: str) -> dict[str, Any] | None:
    sys_prompt_template = prompts.PROMISE_EXTRACTION_SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": sys_prompt_template.replace("{{name}}", candidate_name)},
        {"role": "user", "content": extract}
    ]

    response = client.beta.chat.completions.parse(
        model=settings.OPENAI_MODEL_NAME,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        response_format=LLMPromiseResponse,
    )
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
    return {
        "_timestamp": datetime.now(),
        "status": PromiseStatus.PROGRESSING,
        "text": raw_promise.promise_text,
        "citations": [
            {
                "date": datetime.now(),
                "extract": raw_promise.exact_quote,
                "url": url,
            }
        ]
    }
