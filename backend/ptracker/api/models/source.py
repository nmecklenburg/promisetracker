from datetime import datetime
from pydantic import HttpUrl
from sqlmodel import AutoString, Field, Relationship, SQLModel

from ptracker.api.models._associations import SourceCandidateLink, SourcePromiseLink


class SourceBase(SQLModel):
    creation_date: datetime
    url: HttpUrl = Field(sa_type=AutoString)
    title: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promises: list["Promise"] = Relationship(back_populates="sources", link_model=SourcePromiseLink)  # noqa: F821
    candidates: list["Candidate"] = Relationship(back_populates="sources", link_model=SourceCandidateLink)  # noqa: F821
