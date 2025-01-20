from sqlmodel import Session

import logging

from ptracker.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data.")
    with Session(engine) as session:
        init_db(session)
    logger.info("Finished seeding database.")


if __name__ == "__main__":
    main()
