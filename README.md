# github-service

## Description
`github-service` is a FastAPI-based microservice for interacting with the GitHub API. It allows you to create, retrieve, update, and comment on issues in a GitHub repository via a simple REST API.

## Features
- Create new GitHub issues
- List and filter issues
- Get details of a single issue
- Update issue title, body, or state
- Comment on issues

## Requirements
- Python 3.11+
- Docker (optional, for containerized deployment)

## Setup (Local)
1. Clone the repository:
	```sh
	git clone <repo-url>
	cd github-service
	```
2. Install dependencies:
	```sh
	pip install -r requirements.txt
	```
3. Create a `.env` file with your GitHub token and repo info:
	```env
	GITHUB_TOKEN=your_github_token
	GITHUB_OWNER=your_github_username_or_org
	GITHUB_REPO=your_repo_name
	```
4. Run the app:
	```sh
	uvicorn main:app --reload
	```

## Setup (Docker)
1. Build the Docker image:
	```sh
	docker build -t github-service .
	```
2. Run the container (with .env):
	```sh
	docker run --env-file .env -p 8000:8000 github-service
	```

## API Endpoints
- `POST   /issues` — Create a new issue
- `GET    /issues` — List issues (with filters)
- `GET    /issues/{issue_number}` — Get a single issue
- `PATCH  /issues/{issue_number}` — Update an issue
- `POST   /issues/{issue_number}/comments` — Comment on an issue

## Example: Create an Issue
```sh
curl -X POST "http://localhost:8000/issues" \
  -H "Content-Type: application/json" \
  -d '{"title": "Bug report", "body": "Details...", "labels": ["bug"]}'
```

## Environment Variables
- `GITHUB_TOKEN` — GitHub personal access token
- `GITHUB_OWNER` — GitHub username or organization
- `GITHUB_REPO` — Repository name