from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel
from typing import Any, Optional

from ptracker.api.models._associations import PromiseActionLink
from ptracker.core.settings import settings


class ActionBase(SQLModel):
    date: datetime
    text: str


class ActionCreate(ActionBase):
    # Just like promises, do not create an action without a citation.
    citations: list["CitationCreate"] = Field(min_items=1)  # noqa: F821
    promises: Optional[list[int]] = Field(default=None,
                                          description="List of existing promise_ids matched to this action.")


class ActionUpdate(SQLModel):
    date: Optional[datetime] = None
    text: Optional[str] = None


class Action(ActionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidate.id", ondelete="CASCADE")
    candidate: "Candidate" = Relationship(back_populates="actions")  # noqa: F821
    citations: list["Citation"] = Relationship(back_populates="action", cascade_delete=True)  # noqa: F821
    promises: list["Promise"] = Relationship(back_populates="actions", link_model=PromiseActionLink)  # noqa: F821
    embedding: Any = Field(default=None, sa_column=Column(Vector(settings.ACTION_EMBEDDING_DIM)))


class ActionPublic(ActionBase):
    id: int
    candidate_id: int
    citations: int = Field(description="Number of citations backing this action.")
    promises: int = Field(description="Number of promises this action is associated with.")


class ActionsPublic(SQLModel):
    data: list[ActionPublic] = Field(description="List of action jsons.")
    count: int = Field(description="Total number of actions tracked for this candidate.")
