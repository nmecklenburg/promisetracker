from datetime import datetime
from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlmodel import (
    create_engine,
    select,
    text,
    Index,
    Session,
    SQLModel,
)
from typing import Annotated, Generator

from ptracker.api.models import (
    Action,
    Candidate,
    Promise,
    Citation,
)
from ptracker.core.llm_utils import get_action_embedding, get_promise_embedding
from ptracker.core.settings import settings
from ptracker.core.utils import get_logger

logger = get_logger(__name__)


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
    session.exec(text('CREATE EXTENSION IF NOT EXISTS vector'))
    # Create candidates, promises, citations, and links tables.
    SQLModel.metadata.create_all(engine)

    index_names = ["action_embeds", "prom_embeds"]
    for index_name, model in zip(index_names, (Action, Promise)):
        query = text(f"SELECT indexname FROM pg_indexes WHERE indexname = '{index_name}' LIMIT 1")
        if session.exec(query).first() is None:
            Index(index_name,
                  model.embedding,
                  postgresql_using='hnsw',
                  postgresql_with={'m': 16, 'ef_construction': 64},
                  postgresql_ops={'embedding': 'vector_cosine_ops'}).create(engine)
        else:
            logger.info(f"Index {index_name} already exists, so will not recreate it.")

    query = select(Candidate)
    results = session.exec(query)

    # Seed the database with some entries if it's empty.
    if not results.all():
        promise_citation = Citation(date=datetime.now(),
                                    url="https://www.nytimes.com/2024/09/26/us/politics/harris-trump-economy.html",
                                    extract="Sample extract text snipped from article via AI.")
        ptext = "Lower costs, reduce regulations, cut taxes for the middle class, and incentivize corporations to " \
                "build their products in the United States."
        promise = Promise(text=ptext,
                          _timestamp=datetime.today(),
                          status=0,
                          citations=[promise_citation],
                          embedding=get_promise_embedding(ptext))
        action_citation = Citation(date=datetime.now(),
                                   url="https://www.nytimes.com/2025/01/21/us/politics/harris-tariffs-action.html",
                                   extract="Sample extract text snipped from article via AI, but for an action!")
        atext = "Signed into law various import tariffs on foreign goods competing with US manufacturers."
        action = Action(text=atext,
                        date=datetime.today(),
                        citations=[action_citation],
                        promises=[promise],
                        embedding=get_action_embedding(atext))
        candidate = Candidate(name="Kamala Harris",
                              description="Candidate for 2024 US presidential election with Tim Walz as running mate.",
                              profile_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kamala_Harris_Vice_Presidential_Portrait.jpg/1200px-Kamala_Harris_Vice_Presidential_Portrait.jpg",
                              promises=[promise],
                              actions=[action])

        promise_citation2 = Citation(date=datetime.now(),
                                     url="https://www.google.com",
                                     extract="Sample extract text snipped from article via AI.")
        ptext2 = "Sample promise from article."
        promise2 = Promise(text=ptext2,
                           _timestamp=datetime.today(),
                           status=0,
                           citations=[promise_citation2],
                           embedding=get_promise_embedding(ptext2))
        candidate2 = \
            Candidate(name="Joe Biden",
                      description="Candidate for 2020 US presidential election with Kamala Harris as running mate.",
                      profile_image_url="https://bidenwhitehouse.archives.gov/wp-content/uploads/2025/01/biden-profile-31-1_w-1270.png",
                      promises=[promise2])

        session.add(candidate)
        session.add(candidate2)
        session.commit()

        session.refresh(promise_citation)
        session.refresh(action_citation)
        session.refresh(promise)
        session.refresh(action)
        session.refresh(candidate)

        logger.info(f"Seeded database with candidate {candidate}.")
        logger.info(f"Seeded database with promise {promise}.")
        logger.info(f"Seeded database with action {action}.")
        logger.info(f"Seeded database with promise citation {promise_citation}.")
        logger.info(f"Seeded database with action citation {action_citation}.")
    else:
        logger.info("Queried database found to have non-empty candidates table, so skipping seed process.")
