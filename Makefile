# Makefile for GitHub Issue Service
# Author: Nitish Ratakonda (nitishsjsucs)
# Email: Nitish.ratakonda@sjsu.edu

.PHONY: help install test test-unit test-integration test-coverage run dev clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m "not integration"

test-integration: ## Run integration tests only
	pytest -m integration

test-coverage: ## Run tests with coverage report
	pytest --cov=. --cov-report=html --cov-report=term-missing

run: ## Run the application
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev: ## Run in development mode with auto-reload
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

clean: ## Clean up generated files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf webhook_events.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Run linting
	python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code
	python -m black .
	python -m isort .

docker-build: ## Build Docker image
	docker build -t github-issue-service .

docker-run: ## Run Docker container
	docker run --env-file .env -p 8000:8000 github-issue-service

docker-dev: ## Run in development mode with Docker Compose
	docker-compose up --build

check-env: ## Check environment variables
	@echo "Checking environment variables..."
	@python -c "from config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, WEBHOOK_SECRET; print('✓ All required environment variables are set')" || echo "✗ Missing environment variables"

setup: install check-env ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"
