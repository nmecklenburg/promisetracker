from datetime import datetime
from pydantic import HttpUrl
from sqlmodel import SQLModel, Relationship

from ptracker.api.models._associations import SourceCandidateLink, SourcePromiseLink


class SourceBase(SQLModel):
    creation_date: datetime
    url: HttpUrl
    title: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    promises: list["Promise"] = Relationship(back_populates="sources", link_model=SourcePromiseLink)  # noqa: F821
    candidates: list["Candidate"] = Relationship(back_populates="sources", link_model=SourceCandidateLink)  # noqa: F821
