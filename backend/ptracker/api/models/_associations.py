from sqlmodel import SQLModel, Field


class SourcePromiseLink(SQLModel):
    promise_id: int = Field(foreign_key="promise.id", primary_key=True)
    source_id: int = Field(foreign_key="source.id", primary_key=True)


class SourceCandidateLink(SQLModel):
    candidate_id: int = Field(foreign_key="candidate.id", primary_key=True)
    source_id: int = Field(foreign_key="source.id", primary_key=True)
