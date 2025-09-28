from typing_extensions import Literal
from pydantic import BaseModel, Field
from typing import List, Optional

class CreateBodyModel(BaseModel):
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = []


class GetQueryParamsModel(BaseModel):
    state: Literal["open", "closed", "all"] = "open"
    labels: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=30, ge=1, le=100)


class UpdateBodyModel(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[Literal["open", "closed"]] = None


class CommentBodyModel(BaseModel):
    body: str


class IssueResponseModel(BaseModel):
    number: int
    html_url: str
    state: str
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = []
    created_at: str
    updated_at: str

class CommentResponseModel(BaseModel):
    id: int
    html_url: str
    body: str
    user: str
    created_at: str
    updated_at: str
    