from enum import Enum


class PromiseStatus(Enum):
    PROGRESSING = 0
    COMPLETE = 1
    BROKEN = 2
    COMPROMISED = 3


class PromiseExtractionPhase:
    STARTED = "started"
    FAILED = "failed"


DUPLICATE_ENTITY_SIM_THRESHOLD = 0.7
DUPLICATE_ENTITY_DIST_THRESHOLD = 0.3  # 1 - SIM
PROMISE_ACTION_SIM_THRESHOLD = 0.45
PROMISE_ACTION_DIST_THRESHOLD = 0.55  # 1 - SIM
