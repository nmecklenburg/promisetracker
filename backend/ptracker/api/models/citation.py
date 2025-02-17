from datetime import datetime
from pydantic import HttpUrl, model_validator
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from ptracker.core.settings import settings


class CitationBase(SQLModel):
    date: datetime
    extract: str = Field(max_length=settings.CITATION_EXTRACT_LENGTH)
    promise_id: Optional[int] = Field(default=None, foreign_key="promise.id", ondelete="CASCADE")
    action_id: Optional[int] = Field(default=None, foreign_key="action.id", ondelete="CASCADE")

    @model_validator(mode='after')
    def ensure_parent_xor(self):
        null_promise = self.promise_id is None
        null_action = self.action_id is None
        # One is null but not both.
        assert (null_promise or null_action) and not (null_promise and null_action)

        return self


class CitationCreate(SQLModel):
    date: datetime
    extract: str = Field(max_length=settings.CITATION_EXTRACT_LENGTH)
    url: HttpUrl


class Citation(CitationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promise: Optional["Promise"] = Relationship(back_populates="citations")  # noqa: F821
    action: Optional["Action"] = Relationship(back_populates="citations")  # noqa: F821
    url: str


class CitationPublic(CitationBase):
    id: int
    url: str


class CitationsPublic(SQLModel):
    data: list[CitationPublic] = Field(description="List of citation jsons.")
    count: int = Field(description="Total number of citations associated with this promise.")


class CitationUpdate(SQLModel):
    date: Optional[datetime] = None
    extract: Optional[str] = None
    url: Optional[HttpUrl] = None
