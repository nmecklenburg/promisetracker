from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Union

from ptracker.api.models._associations import SourcePromiseLink


class PromiseBase(SQLModel):
    candidate_id: int = Field(foreign_key="candidate.id")
    text: str
    _timestamp: datetime


class PromiseCreate(PromiseBase):
    sources: list[Union["int", "SourceCreate"]]  # noqa: F821


class Promise(PromiseBase):
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    sources: list["Source"] = Relationship(back_populates="promises", link_model=SourcePromiseLink)  # noqa: F821

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")
