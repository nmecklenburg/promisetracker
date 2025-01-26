from bs4 import BeautifulSoup
from datetime import datetime
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import Any, Generator

import requests

from ptracker.api.models import PromiseStatus
from ptracker.core.settings import settings
from ptracker.core.utils import get_logger

logger = get_logger(__name__)


client = AzureOpenAI(
    azure_endpoint=settings.AOAI_ENDPOINT,
    api_key=settings.AOAI_KEY,
    api_version=settings.AOAI_API_VERSION,
)


PROMISE_SYSTEM_PROMPT = """You are an expert in analyzing political speech by or about the politician {{name}}. Your task is to extract structured information about politicians, their promises, and the exact quotes containing only the promise fragment that meets the following strict criteria:
Criteria for a Promise Fragment:
- Actionable: The statement must clearly describe an action or initiative the politician commits to taking (e.g., 'I will build 500 affordable housing units').
- Measurable: The promise must include specific and quantifiable outcomes or timelines (e.g., 'within the next year').
- Exclusion of implied or vague statements: Do not include aspirational, motivational, or rhetorical statements. If the statement lacks specificity or does not commit to a direct action, exclude it.
- Focus on direct fragments: If the statement contains multiple sentences, extract only the fragment directly fulfilling the actionable and measurable criteria. Exclude all additional context, introductory phrases, or rhetorical elements.
Your output must strictly follow this JSON structure for each extracted promise:
{
    "politician_name": "Name of the politician",
    "is_promise": true or false,
    "promise_text": "A succinct description of the politician's actionable and measurable promise", 
    "exact_quote": "The verbatim snippet from the input text containing the actionable and measurable promise."
}

For each promise, ensure:
- `politician_name` contains the name of the politician making the promise.
- `is_promise` is `true` if the statement meets the criteria of being actionable and measurable; otherwise, `false`.
- `promise_text` is your succinct and accurate summary of the politician's actionable and measurable promise.
- `exact_quote` contains only the verbatim snippet of input referencing the politician's actionable and measurable promise.
"""


class LLMPromiseResponse(BaseModel):
    politician_name: str
    is_promise: bool
    promise_text: str
    exact_quote: str


def extract_promises(name: str, urls: list[str]) -> list[dict]:
    # Hmm, for a future phase -- should we try to bypass paywalls? Probably not
    # For now, assume all content is easily accessible.
    promise_dicts = []
    logger.info(f"Received {len(urls)} urls for candidate {name}. Beginning promise extraction; "
                f"looping through them now.")
    for url in urls:
        text = _get_article_text_wiki_test(url)
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
    messages = [
        {"role": "system", "content": PROMISE_SYSTEM_PROMPT.replace("{{name}}", candidate_name)},
        {"role": "user", "content": extract}
    ]

    response = client.beta.chat.completions.parse(
        model=settings.AOAI_DEPLOYMENT_NAME,
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


def stub_extract_promises(urls: list[str]) -> list[dict]:
    return [
        {
            "_timestamp": "2024-01-05",
            "status": 0,
            "text": "some sample text",
            "citations": [
                {
                    "date": "2024-08-01",
                    "extract": "this is a sample extract",
                    "url": "https://www.google.com"
                },
                {
                    "date": "2008-05-13",
                    "extract": "this is a second sample extract",
                    "url": "https://www.bing.com"
                }
            ],
        },
        {
            "_timestamp": "2024-01-07",
            "status": 2,
            "text": "some more sample text",
            "citations": [
                {
                    "date": "2024-07-12",
                    "extract": "this is a third sample extract",
                    "url": "https://www.stanford.edu"
                },
                {
                    "date": "2011-12-21",
                    "extract": "this is a fourth sample extract",
                    "url": "https://www.berkeley.edu"
                }
            ],
        },
    ]
