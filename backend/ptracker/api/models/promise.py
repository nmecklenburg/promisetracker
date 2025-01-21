from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class PromiseBase(SQLModel):
    _timestamp: datetime
    candidate_id: int = Field(foreign_key="candidate.id", ondelete="CASCADE")
    status: int
    text: str


class PromiseCreate(SQLModel):
    _timestamp: datetime
    # Forbid the creation of a promise without citations.
    citations: list["CitationCreate"] = Field(min_items=1)  # noqa: F821
    status: int
    text: str


class PromiseUpdate(SQLModel):
    _timestamp: datetime
    status: int
    text: str


class Promise(PromiseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    candidate: "Candidate" = Relationship(back_populates="promises")  # noqa: F821
    citations: list["Citation"] = Relationship(back_populates="promise", cascade_delete=True)  # noqa: F821

    def timestamp(self) -> str:
        return self._timestamp.strftime("%Y-%m-%d")


class PromisePublic(PromiseBase):
    id: int
    citations: list[int] = Field(description="Integer list of citation IDs associated with this promise.")


class PromisesPublic(SQLModel):
    data: list[PromisePublic] = Field(description="List of promise jsons.")
    count: int = Field(description="Total number of promises associated with this candidate.")
