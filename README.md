# promisetracker

TODOs
- conda env specs
- dev guide
- find swagger at /docs endpoint
- super extra: bloom filter for source dedupe
- todo: alembic migrations

Deployment
- likely going to need to modify domain/host info

useful for local dev:
`set -o allexport && source .env && set +o allexport`

debugging:
- instead of fastapi dev ptracker/main.py, can run `uvicorn ptracker.main:controller --host="0.0.0.0" --port=8000 --log-level=debug`

resolve all the todos in code, too.