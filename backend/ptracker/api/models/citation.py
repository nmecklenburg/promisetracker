from datetime import datetime
from pydantic import HttpUrl
from sqlmodel import Field, Relationship, SQLModel


class CitationBase(SQLModel):
    date: datetime
    extract: str
    promise_id: int = Field(foreign_key="promise.id")


class CitationCreate(CitationBase):
    url: HttpUrl


class Citation(CitationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promise: "Promise" = Relationship(back_populates="citations")
    url: str
