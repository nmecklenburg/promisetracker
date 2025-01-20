from sqlmodel import Field, Relationship, SQLModel
from typing import Union

from ptracker.api.models._associations import SourceCandidateLink


class CandidateBase(SQLModel):
    name: str = Field(min_length=2, max_length=128)
    description: str = Field(max_length=500)


class CandidateCreate(CandidateBase):
    sources: list[Union["int", "SourceCreate"]]  # noqa: F821


class Candidate(CandidateBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promises: list["Promise"] = Relationship(back_populates="candidate")  # noqa: F821
    sources: list["Source"] = Relationship(back_populates="candidates", link_model=SourceCandidateLink)  # noqa: F821


class CandidatePublic(CandidateBase):
    id: int
    promises: list[int] = Field(description="Integer list of promise IDs associated with this candidate.")
    sources: list[int] = Field(description="Integer list of source IDs that cover this candidate.")


class CandidatesPublic(SQLModel):
    data: list[CandidatePublic] = Field(description="List of candidate jsons.")
    count: int = Field(description="Total number of candidates in the database.")
