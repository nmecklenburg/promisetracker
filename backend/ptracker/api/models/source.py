from pydantic import HttpUrl, Field
from sqlmodel import SQLModel


class SourceRequest(SQLModel):
    urls: list[HttpUrl] = Field(min_length=1)
