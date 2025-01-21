from datetime import datetime
from fastapi import Depends
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
    select,
)
from typing import Annotated, Generator

import logging

from ptracker.api.models import (
    Candidate,
    Promise,
    Citation,
)
from ptracker.core.settings import settings

engine = create_engine(settings.SUPABASE_URL.format(key=settings.SUPABASE_KEY))
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionArg = Annotated[Session, Depends(get_db)]


def init_db(session: Session) -> None:
    # Create candidates, promises, citations, and links tables.
    SQLModel.metadata.create_all(engine)

    query = select(Candidate)
    results = session.exec(query)

    # Seed the database with some entries if it's empty.
    if not results.all():
        citation = Citation(date=datetime.now(),
                            url="https://www.nytimes.com/2024/09/26/us/politics/harris-trump-economy.html",
                            title="Harris Now Has an Economic Plan. Can It Best Trump's Promises?",
                            extract="Sample extract text snipped from article via AI.")
        promise = Promise(text="Lower costs, reduce regulations, cut taxes for the middle class, and incentivize "
                               "corporations to build their products in the United States.",
                          _timestamp=datetime.today(),
                          status=0,
                          citations=[citation])
        candidate = Candidate(name="Kamala Harris",
                              description="Candidate for 2024 US presidential election with Tim Walz as running mate.",
                              promises=[promise])

        session.add(candidate)
        session.commit()

        session.refresh(citation)
        session.refresh(promise)
        session.refresh(candidate)

        logger.info(f"Seeded database with candidate {candidate}.")
        logger.info(f"Seeded database with promise {promise}.")
        logger.info(f"Seeded database with citation {citation}.")
    else:
        logger.info("Queried database found to have non-empty candidates table, so skipping seed process.")
