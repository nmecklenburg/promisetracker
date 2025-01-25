from datetime import datetime
from pydantic import HttpUrl
from sqlmodel import Field, Relationship, SQLModel


class CitationBase(SQLModel):
    date: datetime
    extract: str = Field(max_length=255)
    promise_id: int = Field(foreign_key="promise.id", ondelete="CASCADE")


class CitationCreate(SQLModel):
    date: datetime
    extract: str = Field(max_length=255)
    url: HttpUrl


class Citation(CitationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promise: "Promise" = Relationship(back_populates="citations")  # noqa: F821
    url: str


class CitationPublic(CitationBase):
    id: int
    url: str


class CitationsPublic(SQLModel):
    data: list[CitationPublic] = Field(description="List of citation jsons.")
    count: int = Field(description="Total number of citations associated with this promise.")


class CitationUpdate(CitationCreate):
    pass
