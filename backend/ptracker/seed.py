from sqlmodel import Session

from ptracker.core.db import engine, init_db
from ptracker.core.utils import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("Creating initial data.")
    with Session(engine) as session:
        init_db(session)
    logger.info("Finished seeding database.")


if __name__ == "__main__":
    main()
