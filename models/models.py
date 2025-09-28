from typing_extensions import Literal
from pydantic import BaseModel, Field
from typing import List, Optional


class CreateBodyModel(BaseModel):
    """
    Model for the request body when creating a new GitHub issue.
    """
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = []


class GetQueryParamsModel(BaseModel):
    """
    Model for query parameters when retrieving a list of issues.
    """
    state: Literal["open", "closed", "all"] = "open"
    labels: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=30, ge=1, le=100)


class UpdateBodyModel(BaseModel):
    """
    Model for the request body when updating an existing GitHub issue.
    """
    title: Optional[str] = None  
    body: Optional[str] = None
    state: Optional[Literal["open", "closed"]] = None


class CommentBodyModel(BaseModel):
    """
    Model for the request body when adding a comment to an issue.
    """
    body: str 



class IssueResponseModel(BaseModel):
    """
    Model for the response body of a GitHub issue.
    """
    number: int
    html_url: str
    state: str
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = []
    created_at: str
    updated_at: str

class CommentResponseModel(BaseModel):
    """
    Model for the response body of comment on a GitHub issue.
    """
    id: int
    html_url: str
    body: str
    user: str
    created_at: str
    updated_at: str
    