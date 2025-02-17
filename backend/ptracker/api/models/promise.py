from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel
from typing import Any, Optional

from ptracker.api.models._associations import PromiseActionLink
from ptracker.core.settings import settings


class PromiseBase(SQLModel):
    _timestamp: datetime
    status: int
    text: str


class PromiseCreate(PromiseBase):
    # Forbid the creation of a promise without citations.
    citations: list["CitationCreate"] = Field(min_items=1)  # noqa: F821
    actions: Optional[list[int]] = Field(default=None,
                                         description="List of existing action_ids matched to this promise.")


class PromiseUpdate(SQLModel):
    _timestamp: Optional[datetime] = None
    status: Optional[int] = None
    text: Optional[str] = Field(default=None, min_length=1)


class Promise(PromiseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidate.id", ondelete="CASCADE")
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    actions: list["Action"] = Relationship(back_populates="promises", link_model=PromiseActionLink)  # noqa: F821
    citations: list["Citation"] = Relationship(back_populates="promise", cascade_delete=True)  # noqa: F821
    embedding: Any = Field(default=None, sa_column=Column(Vector(settings.PROMISE_EMBEDDING_DIM)))

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")


class PromisePublic(PromiseBase):
    id: int
    candidate_id: int
    citations: int = Field(description="Number of citations backing this promise.")
    actions: int = Field(description="Number of actions associated with this promise.")


class PromisesPublic(SQLModel):
    data: list[PromisePublic] = Field(description="List of promise jsons.")
    count: int = Field(description="Total number of promises tracked for this candidate.")
