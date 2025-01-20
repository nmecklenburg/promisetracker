# TODO nmecklenburg - deprecated. Delete once refactored models approach verified.
#
# from datetime import datetime
# from pydantic import HttpUrl
# from sqlmodel import SQLModel, Field, Relationship
#
#
# class CandidateBase(SQLModel):
#     name: str
#     description: str
#
#
# class CandidateCreate(CandidateBase):
#     sources: list[int | "SourceCreate"]
#
#
# class Candidate(CandidateBase):
#     promises: list["Promise"] = Relationship(back_populates="candidate")
#     sources: list["Source"] = Relationship(back_populates="candidates", link_model="SourceCandidateLink")
#
#
# class SourcePromiseLink(SQLModel):
#     promise_id: int = Field(foreign_key="promise.id", primary_key=True)
#     source_id: int = Field(foreign_key="source.id", primary_key=True)
#
#
# class SourceCandidateLink(SQLModel):
#     candidate_id: int = Field(foreign_key="candidate.id", primary_key=True)
#     source_id: int = Field(foreign_key="source.id", primary_key=True)
#
#
# class PromiseBase(SQLModel):
#     candidate_id: int = Field(foreign_key="candidate.id")
#     text: str
#     _timestamp: datetime
#
#
# class PromiseCreate(PromiseBase):
#     sources: list[int | "SourceCreate"]
#
#
# class Promise(PromiseBase):
#     candidate: Candidate = Relationship(back_populates="promises")
#     sources: list["Source"] = Relationship(back_populates="promises", link_model=SourcePromiseLink)
#
#     def timestamp(self) -> str:
#         return self._timestamp.strftime("%Y-%m-%d")
#
#
# class SourceBase(SQLModel):
#     creation_date: datetime
#     url: HttpUrl
#     title: str
#
#
# class SourceCreate(SourceBase):
#     pass
#
#
# class Source(SourceBase):
#     promises: list[Promise] = Relationship(back_populates="sources", link_model=SourcePromiseLink)
#     candidates: list[Candidate] = Relationship(back_populates="sources", link_model=SourceCandidateLink)
