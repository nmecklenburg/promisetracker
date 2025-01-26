from datetime import datetime
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel


class PromiseStatus(Enum):
    PROGRESSING = 0
    COMPLETE = 1
    BROKEN = 2
    COMPROMISED = 3


class PromiseBase(SQLModel):
    _timestamp: datetime
    status: int
    text: str


class PromiseCreate(PromiseBase):
    # Forbid the creation of a promise without citations.
    citations: list["CitationCreate"] = Field(min_items=1)  # noqa: F821


class PromiseUpdate(PromiseBase):
    pass


class Promise(PromiseBase, table=True):
    candidate_id: int = Field(foreign_key="candidate.id", ondelete="CASCADE")
    id: int = Field(default=None, primary_key=True)
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    citations: list["Citation"] = Relationship(back_populates="promise", cascade_delete=True)  # noqa: F821

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")


class PromisePublic(PromiseBase):
    id: int
    candidate_id: int
    citations: int = Field(description="Number of citations backing this promise.")


class PromisesPublic(SQLModel):
    data: list[PromisePublic] = Field(description="List of promise jsons.")
    count: int = Field(description="Total number of promises tracked for this candidate.")
