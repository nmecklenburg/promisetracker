from sqlmodel import Session, SQLModel, create_engine

from ptracker.core.settings import settings

engine = create_engine(settings.SUPABASE_URL.format(key=settings.SUPABASE_KEY))


def init_db(session: Session) -> None:
    # Create candidates, promises, sources, and links tables.
    SQLModel.metadata.create_all(engine)
