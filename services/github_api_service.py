import requests
from config import BASE_URL, HEADERS
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def create_github_issue(title, body, labels):
    api_url = BASE_URL + "/issues"

    payload = {}
    if title is None:
        raise ValueError("The required field Title is missing.")
    if body is not None:
        payload["body"] = body
    if labels is not None:
        payload["labels"] = labels

    headers = HEADERS | {"Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        return data
    else:
        raise HTTPException(status_code=response.status_code, Messsage=response.text)

def get_github_issues(state, labels, page, per_page):
    api_url = BASE_URL + "/issues"
    params = {
        "state": state,
        "labels": labels,
        "page": page,
        "per_page": per_page
    }
    response = requests.get(api_url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json(), response.headers.get("Link")
    else:
        raise HTTPException(status_code=response.status_code, Messsage=response.text)

def get_github_issue(issue_number):
    api_url = BASE_URL + f"/issues/{issue_number}"
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, Messsage=response.text)
    
def update_github_issue(issue_number, title, body, state):
    api_url = BASE_URL + f"/issues/{issue_number}"
    payload = {}

    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state

    headers = HEADERS | {"Content-Type": "application/json"}
    response = requests.patch(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def comment_github_issue(issue_number, comment_body):
    api_url = BASE_URL + f"/issues/{issue_number}/comments"
    headers = HEADERS | {"Content-Type": "application/json"}

    if comment_body is None:
        raise ValueError("The required field Body is missing.")
    
    response = requests.post(api_url, json={"body": comment_body}, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, Messsage=response.text)
