# Author: Keerthana (keerthana-25)
# Email: keerthanapm257@gmail.com
# Assignment: GitHub Issue Service - Issue CRUD Routes
# Date: September 29, 2025
# Description: FastAPI routes for GitHub issue CRUD operations

from fastapi import APIRouter, Depends, HTTPException, Response
from models.models import CreateBodyModel, GetQueryParamsModel, UpdateBodyModel, CommentBodyModel, IssueResponseModel, CommentResponseModel
from services.github_api_service import create_github_issue, comment_github_issue, get_github_issues, get_github_issue, update_github_issue

router = APIRouter()


@router.post("/issues", response_model=IssueResponseModel, status_code=201)
def create_issue(body: CreateBodyModel, response: Response):
    """
    Create a new GitHub issue with the given title, body, and labels.
    Sets the Location header to the new issue's id.
    """
    data = create_github_issue(body.title, body.body, body.labels)
    response.headers["Location"] = f"/issues/{data['number']}"
    return {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": [label["name"] for label in data.get("labels", [])],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }


@router.get("/issues", response_model=list[IssueResponseModel])
def get_issue(param: GetQueryParamsModel = Depends(), response: Response = None):
    """
    Retrieve a list of GitHub issues, optionally filtered by state, labels, and pagination.
    Forwards the GitHub Link header for pagination if present.
    """
    data, link_header = get_github_issues(param.state, param.labels, param.page, param.per_page)
    issues = []
    for item in data:
        # Extract fields and label names
        issue = {
            "number": item["number"],
            "html_url": item["html_url"],
            "state": item["state"],
            "title": item["title"],
            "body": item["body"],
            "labels": [label["name"] for label in item.get("labels", [])],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        }
        issues.append(issue)
    if link_header:
        # Forward pagination header to client
        response.headers["Link"] = link_header
    return issues


@router.get("/issues/{issue_number}", response_model=IssueResponseModel)
def get_single_issue(issue_number: int):
    """
    Retrieve a GitHub issue by its number.
    """
    data = get_github_issue(issue_number)
    return {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": [label["name"] for label in data.get("labels", [])],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }


@router.patch("/issues/{issue_number}", response_model=IssueResponseModel)
def update_issue(body: UpdateBodyModel, issue_number: int):
    """
    Update an existing GitHub issue's title, body, or state.
    """
    data = update_github_issue(issue_number, body.title, body.body, body.state)
    return {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": [label["name"] for label in data.get("labels", [])],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }


@router.post("/issues/{issue_number}/comments", response_model=CommentResponseModel, status_code=201)
def comment_issue(body: CommentBodyModel, issue_number: int):
    """
    Add a comment to a GitHub issue.
    """
    data = comment_github_issue(issue_number, body.body)
    return {
        "id": data["id"],
        "html_url": data["html_url"],
        "body": data["body"],
        "user": data["user"]["login"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }
