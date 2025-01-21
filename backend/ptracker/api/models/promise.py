from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Union


class PromiseBase(SQLModel):
    _timestamp: datetime
    candidate_id: int = Field(foreign_key="candidate.id")
    status: int
    text: str


class PromiseCreate(PromiseBase):
    citations: list[Union["int", "CitationCreate"]]  # noqa: F821


class Promise(PromiseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    citations: list["Citation"] = Relationship(back_populates="promise")  # noqa: F821

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")
