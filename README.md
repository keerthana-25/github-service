# GitHub Issue Service

This project is a FastAPI-based microservice for interacting with the GitHub Issues API. It allows you to perform various GitHub issues operations such as, create, retrieve, update, and comment on issues via a simple REST API.

## Requirements
- Python 3.11+

## Setup (Local)
1. Clone the repository:
	```sh
	git clone https://github.com/keerthana-25/github-service.git
	cd github-service
	```
2. Install dependencies:
	```sh
	pip install -r requirements.txt
	```
3. Create a `.env` file with your GitHub token and repo info:
	```env
	GITHUB_TOKEN=<your_github_token>
	GITHUB_OWNER=keerthana-25
	GITHUB_REPO=github-service
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
	docker run --env-file <path-to-env-file> -p 8000:8000 github-service
	```

## API Endpoints
- `POST   /issues` — Create a new issue
- `GET    /issues` — List issues (with filters)
- `GET    /issues/{issue_number}` — Get a single issue
- `PATCH  /issues/{issue_number}` — Update an issue
- `POST   /issues/{issue_number}/comments` — Comment on an issue

## Testing
To create an issue

```sh
curl -X POST "http://localhost:8000/issues" \
  -H "Content-Type: application/json" \
  -d '{"title": "Bug report", "body": "This is a bug", "labels": ["bug"]}'
```