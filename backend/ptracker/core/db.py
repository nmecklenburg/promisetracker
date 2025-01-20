from datetime import datetime
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
    select,
)

from ptracker.api.models import (
    Candidate,
    Promise,
    Source
)
from ptracker.core.settings import settings

engine = create_engine(settings.SUPABASE_URL.format(key=settings.SUPABASE_KEY))


def init_db(session: Session) -> None:
    # Create candidates, promises, sources, and links tables.
    SQLModel.metadata.create_all(engine)

    query = select(Candidate)
    results = session.exec(query)

    # Seed the database with some entries if it's empty.
    if not results.all():
        source = Source(creation_date=datetime.now(),
                        url="https://www.nytimes.com/2024/09/26/us/politics/harris-trump-economy.html",
                        title="Harris Now Has an Economic Plan. Can It Best Trump's Promises?")
        promise = Promise(text="Lower costs, reduce regulations, cut taxes for the middle class, and incentivize "
                               "corporations to build their products in the United States.",
                          _timestamp=datetime.today(),
                          status=0,
                          sources=[source])
        candidate = Candidate(name="Kamala Harris",
                              description="Candidate for 2024 US presidential election with Tim Walz as running mate.",
                              promises=[promise],
                              sources=[source])

        session.add(candidate)
        session.commit()

        session.refresh(source)
        session.refresh(promise)
        session.refresh(candidate)

        print(f"Seeded database with candidate {candidate}.")
        print(f"Seeded database with promise {promise}.")
        print(f"Seeded database with source {source}.")
