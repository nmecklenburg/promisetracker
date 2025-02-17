from sqlmodel import SQLModel, Field


class PromiseActionLink(SQLModel, table=True):
    action_id: int = Field(foreign_key="action.id", primary_key=True)
    promise_id: int = Field(foreign_key="promise.id", primary_key=True)
