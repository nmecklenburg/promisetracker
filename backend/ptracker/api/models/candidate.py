from pydantic import HttpUrl, field_validator
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional


def _validate_image_url(url: HttpUrl) -> HttpUrl:
    valid_extensions = ('.jpg', '.jpeg', '.png', '.svg')
    if not url.path.endswith(valid_extensions):
        raise ValueError(f"URL must end with one of the following valid file formats: {valid_extensions}")
    return url


class CandidateBase(SQLModel):
    name: str = Field(min_length=2, max_length=128)
    description: str = Field(max_length=500)


class CandidateCreate(CandidateBase):
    profile_image_url: Optional[HttpUrl]

    @field_validator("profile_image_url")
    @classmethod
    def check_extensions(cls, v: HttpUrl) -> HttpUrl:
        if v is not None:
            return _validate_image_url(v)


class CandidateUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=128)
    description: Optional[str] = Field(default=None, max_length=500)
    profile_image_url: Optional[HttpUrl] = None

    @field_validator("profile_image_url")
    @classmethod
    def check_extensions(cls, v: HttpUrl) -> HttpUrl:
        if v is not None:
            return _validate_image_url(v)


class Candidate(CandidateBase, table=True):
    id: int = Field(default=None, primary_key=True)
    promises: list["Promise"] = Relationship(back_populates="candidate", cascade_delete=True)  # noqa: F821
    actions: list["Action"] = Relationship(back_populates="candidate", cascade_delete=True)  # noqa: F821
    profile_image_url: Optional[str] = None


class CandidatePublic(CandidateBase):
    id: int
    promises: int = Field(description="Number of promises tracked for this candidate.")
    actions: int = Field(description="Number of actions associated with this candidate.")
    profile_image_url: Optional[str] = None


class CandidatesPublic(SQLModel):
    data: list[CandidatePublic] = Field(description="List of candidate jsons.")
    count: int = Field(description="Total number of candidates in the database.")
