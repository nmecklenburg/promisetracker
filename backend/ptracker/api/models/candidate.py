from sqlmodel import SQLModel, Relationship
from typing import Union


class CandidateBase(SQLModel):
    name: str
    description: str


class CandidateCreate(CandidateBase):
    sources: list[Union["int", "SourceCreate"]]  # noqa: F821


class Candidate(CandidateBase):
    promises: list["Promise"] = Relationship(back_populates="candidate")  # noqa: F821
    sources: list["Source"] = Relationship(back_populates="candidates", link_model="SourceCandidateLink")  # noqa: F821
