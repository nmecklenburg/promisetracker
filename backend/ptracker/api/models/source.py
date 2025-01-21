# from datetime import datetime
# from pydantic import HttpUrl
# from sqlmodel import Field, Relationship, SQLModel
#
# from ptracker.api.models._associations import SourceCandidateLink, SourcePromiseLink
#
#
# class SourceBase(SQLModel):
#     creation_date: datetime
#     title: str
#
#
# class SourceCreate(SourceBase):
#     url: HttpUrl
#
#
# class Source(SourceBase, table=True):
#     id: int = Field(default=None, primary_key=True)
#     candidates: list["Candidate"] = Relationship(back_populates="sources", link_model=SourceCandidateLink)  # noqa: F821
#     promises: list["Promise"] = Relationship(back_populates="sources", link_model=SourcePromiseLink)  # noqa: F821
#     url: str
