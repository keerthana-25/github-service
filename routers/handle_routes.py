
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.models import CreateBodyModel, GetQueryParamsModel, UpdateBodyModel, CommentBodyModel
from services.github_api_service import create_github_issue, comment_github_issue, get_github_issues, get_github_issue, update_github_issue

router = APIRouter()


@router.post("/issues")
def create_issue(body : CreateBodyModel):
    data = create_github_issue(body.title, body.body, body.labels)
    response = {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": data.get("labels", []),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }
    return JSONResponse(
        content=response,
        status_code=201,
        headers={"Location": f"/issues/{data['number']}"}
    )


@router.get("/issues")
def get_issue(param : GetQueryParamsModel = Depends()):
    data = get_github_issues(param.state, param.labels, param.page, param.per_page)
    response = []
    for item in data:
        issue = {
            "number": item["number"],
            "html_url": item["html_url"],
            "state": item["state"],
            "title": item["title"],
            "body": item["body"],
            "labels": item.get("labels", []),
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        }
        response.append(issue)
    return JSONResponse(content=response, status_code=200)


@router.get("/issues/{issue_number}")
def get_single_issue(issue_number : int):
    data = get_github_issue(issue_number)
    response = {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": data.get("labels", []),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }
    return JSONResponse(content=response, status_code=200)


@router.patch("/issues/{issue_number}")
def update_issue(body:UpdateBodyModel, issue_number:int):
    data = update_github_issue(issue_number, body.title, body.body, body.state)
    response = {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": data.get("labels", []),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }
    return JSONResponse(content=response, status_code=200)


@router.post("/issues/{issue_number}/comments")
def comment_issue(body : CommentBodyModel, issue_number: int):
    data = comment_github_issue(issue_number, body.body)
    response = {
        "id": data["id"],
        "html_url": data["html_url"],
        "body": data["body"],
        "user": data["user"]["login"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }
    return JSONResponse(content=response, status_code=201)
