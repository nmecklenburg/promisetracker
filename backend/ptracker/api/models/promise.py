from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Union

from ptracker.api.models._associations import SourcePromiseLink


class PromiseBase(SQLModel):
    _timestamp: datetime
    candidate_id: int = Field(foreign_key="candidate.id")
    status: int
    text: str


class PromiseCreate(PromiseBase):
    sources: list[Union["int", "SourceCreate"]]  # noqa: F821


class Promise(PromiseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    sources: list["Source"] = Relationship(back_populates="promises", link_model=SourcePromiseLink)  # noqa: F821

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")
