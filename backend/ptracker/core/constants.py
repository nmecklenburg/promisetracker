from enum import Enum


class PromiseStatus(Enum):
    PROGRESSING = 0
    COMPLETE = 1
    BROKEN = 2
    COMPROMISED = 3


class PromiseExtractionPhase:
    STARTED = "started"
    FAILED = "failed"
