from bs4 import BeautifulSoup
from typing import Generator

import requests

from ptracker.api.models import Action, Candidate, Promise
from ptracker.core.settings import settings
from ptracker.core.utils import get_logger
from ptracker.core.sources import ActionExtractor, EntityExtractor, PromiseExtractor

logger = get_logger(__name__)


class SourceAnalyzer:
    def __init__(self):
        self.entity_registry: dict[type, EntityExtractor] = {}

    def register_entity(self, entity: type, extractor: EntityExtractor):
        self.entity_registry[entity] = extractor

    @staticmethod
    def _get_article_text(url: str) -> str | None:
        response = requests.get(url)
        if response.status_code == 200:  # brittle?
            text = BeautifulSoup(response.text, "html.parser").get_text()
            return text
        else:
            logger.warning(f"In trying to visit '{url}' as part of promise extraction flow, "
                           f"received unhappy status code {response.status_code}.")
            return None

    @staticmethod
    def _chunked_text_iterator(text: str) -> Generator[str, None, None]:
        for idx in range(0, len(text), settings.CITATION_EXTRACT_LENGTH):
            yield text[idx:idx + settings.CITATION_EXTRACT_LENGTH * 2]

    def construct_entity_jsons(self, candidate_name: str, urls: list[str]) -> dict[type, list]:
        entity_jsons = {}
        logger.info(f"Received {len(urls)} urls for candidate {candidate_name}. Beginning entity extraction; "
                    f"looping through them now.")
        for url in urls:
            text = SourceAnalyzer._get_article_text(url)
            if not text:
                logger.warning(f"Failed to extract text from {url}.")
                continue

            for idx, extract in enumerate(SourceAnalyzer._chunked_text_iterator(text)):
                for entity in self.entity_registry:
                    entity_dict_collection = self.entity_registry[entity].get_entities_from_extract(
                        extract=extract,
                        candidate_name=candidate_name,
                        url=url
                    )

                    if not entity_dict_collection:
                        logger.info(f"Did not extract any {entity.__name__} entities from chunk {idx} of {url} for "
                                    f"candidate {candidate_name}.")
                    else:
                        entity_jsons[entity] = entity_jsons.get(entity, []) + entity_dict_collection
        return entity_jsons

    def extract_entities(self, candidate: Candidate, urls: list[str]):
        entity_jsons = self.construct_entity_jsons(candidate_name=candidate.name, urls=urls)
        for entity in self.entity_registry:
            this_entity_json_collection = entity_jsons[entity]
            logger.info(f"Number of {entity.__name__} entities before deduplication: "
                        f"{len(this_entity_json_collection)}.")
            filtered_jsons = \
                self.entity_registry[entity].deduplicate_entities(entity_jsons=this_entity_json_collection)
            logger.info(f"Number of {entity.__name__} entities after deduplication: {len(filtered_jsons)}.")
            self.entity_registry[entity].add_entities_to_session(candidate_id=candidate.id,
                                                                 entity_jsons=filtered_jsons)


def analyze_sources(candidate: Candidate, urls: list[str]) -> None:
    analyzer = SourceAnalyzer()
    analyzer.register_entity(entity=Promise, extractor=PromiseExtractor())
    analyzer.register_entity(entity=Action, extractor=ActionExtractor())
    analyzer.extract_entities(candidate=candidate, urls=urls)
