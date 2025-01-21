# from sqlmodel import SQLModel, Field
#
#
# class SourcePromiseLink(SQLModel, table=True):
#     promise_id: int = Field(foreign_key="promise.id", primary_key=True)
#     source_id: int = Field(foreign_key="source.id", primary_key=True)
#
#
# class SourceCandidateLink(SQLModel, table=True):
#     candidate_id: int = Field(foreign_key="candidate.id", primary_key=True)
#     source_id: int = Field(foreign_key="source.id", primary_key=True)
