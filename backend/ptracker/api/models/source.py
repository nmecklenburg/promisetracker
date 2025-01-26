from pydantic import BaseModel, HttpUrl, Field
from typing import Literal


class SourceRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1)


class SourceResponse(BaseModel):
    status: Literal["started", "failed"]
