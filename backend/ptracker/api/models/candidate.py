from sqlmodel import Field, Relationship, SQLModel


class CandidateBase(SQLModel):
    name: str = Field(min_length=2, max_length=128)
    description: str = Field(max_length=500)


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(SQLModel):
    name: str = Field(default=None, min_length=2, max_length=128)
    description: str = Field(default=None, max_length=500)


class Candidate(CandidateBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promises: list["Promise"] = Relationship(back_populates="candidate", cascade_delete=True)  # noqa: F821
    actions: list["Action"] = Relationship(back_populates="candidate", cascade_delete=True)  # noqa: F821


class CandidatePublic(CandidateBase):
    id: int
    promises: int = Field(description="Number of promises tracked for this candidate.")
    actions: int = Field(description="Number of actions associated with this candidate.")


class CandidatesPublic(SQLModel):
    data: list[CandidatePublic] = Field(description="List of candidate jsons.")
    count: int = Field(description="Total number of candidates in the database.")
