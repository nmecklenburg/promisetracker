from datetime import datetime
from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
    select,
    text
)
from typing import Annotated, Generator

import logging

from ptracker.api.models import (
    Candidate,
    Promise,
    Citation,
)
from ptracker.core.settings import settings

logger = logging.getLogger(__name__)


def _init_engine() -> Engine:
    database_uris = [
        ("IPv4", settings.SUPABASE_URL_IPV4.format(key=settings.SUPABASE_KEY)),
        ("IPv6", settings.SUPABASE_URL_IPV6.format(key=settings.SUPABASE_KEY)),
    ]

    for protocol, database_uri in database_uris:
        try:
            _engine = create_engine(database_uri)
            with _engine.connect() as connection:  # Quickly test the connection.
                connection.execute(text("SELECT 1"))
            return _engine
        except OperationalError as e:
            # Use pooled IPv4 sessions.
            logger.warning(f"Tried to establish connection to database via {protocol} but "
                           f"encountered:\n{e}\nRetrying with a different protocol.")
    raise RuntimeError("Fatal error: could not connect to database.")


engine = _init_engine()


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

        second_citation = Citation(date=datetime.now(),
                                   url="https://www.gooogle.com",
                                   title="Joe Biden 46th President",
                                   extract="Sample extract text snipped from article via AI.")
        second_promise = Promise(text="Sample promise from article.",
                                 _timestamp=datetime.today(),
                                 status=0,
                                 citations=[second_citation])
        second_candidate = Candidate(name="Joe Biden",
                                     description="Candidate for 2020 US presidential election with Kamala Harris as running mate.",
                                     promises=[second_promise])

        session.add(candidate)
        session.add(second_candidate)
        session.commit()

        session.refresh(citation)
        session.refresh(promise)
        session.refresh(candidate)

        logger.info(f"Seeded database with candidate {candidate}.")
        logger.info(f"Seeded database with promise {promise}.")
        logger.info(f"Seeded database with citation {citation}.")
    else:
        logger.info("Queried database found to have non-empty candidates table, so skipping seed process.")
