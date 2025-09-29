# Author: Arshan Bhanage (ArshanBhanage)
# Email: bhanagearshan@gmail.com
# Assignment: GitHub Issue Service - Route Testing Suite
# Date: September 29, 2025
# Description: Comprehensive unit tests for API route validation and error handling
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

class TestIssueRoutes:
    """Test issue-related API routes."""
    
    @patch('routers.handle_routes.create_github_issue')
    def test_create_issue_success(self, mock_create):
        """Test successful issue creation via API."""
        mock_create.return_value = {
            "number": 123,
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        response = client.post("/issues", json={
            "title": "Test Issue",
            "body": "Test body",
            "labels": ["bug"]
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["number"] == 123
        assert data["title"] == "Test Issue"
        assert "Location" in response.headers
        assert response.headers["Location"] == "/issues/123"
    
    def test_create_issue_missing_title(self):
        """Test issue creation with missing required title."""
        response = client.post("/issues", json={
            "body": "Test body"
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('routers.handle_routes.create_github_issue')
    def test_create_issue_api_error(self, mock_create):
        """Test issue creation with API error."""
        from fastapi import HTTPException
        mock_create.side_effect = HTTPException(status_code=400, detail="Bad Request")
        
        response = client.post("/issues", json={
            "title": "Test Issue"
        })
        
        assert response.status_code == 400
    
    @patch('routers.handle_routes.get_github_issues')
    def test_get_issues_success(self, mock_get):
        """Test successful issues retrieval via API."""
        mock_get.return_value = ([{
            "number": 123,
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }], "<next>; rel=\"next\"")
        
        response = client.get("/issues?state=open&page=1&per_page=30")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["number"] == 123
        assert "Link" in response.headers
    
    @patch('routers.handle_routes.get_github_issue')
    def test_get_single_issue_success(self, mock_get):
        """Test successful single issue retrieval via API."""
        mock_get.return_value = {
            "number": 123,
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        response = client.get("/issues/123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == 123
        assert data["title"] == "Test Issue"
    
    @patch('routers.handle_routes.update_github_issue')
    def test_update_issue_success(self, mock_update):
        """Test successful issue update via API."""
        mock_update.return_value = {
            "number": 123,
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "closed",
            "title": "Updated Issue",
            "body": "Updated body",
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        response = client.patch("/issues/123", json={
            "title": "Updated Issue",
            "state": "closed"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Issue"
        assert data["state"] == "closed"
    
    @patch('routers.handle_routes.comment_github_issue')
    def test_comment_issue_success(self, mock_comment):
        """Test successful issue commenting via API."""
        mock_comment.return_value = {
            "id": 456,
            "html_url": "https://github.com/owner/repo/issues/123#issuecomment-456",
            "body": "Test comment",
            "user": {"login": "testuser"},
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        response = client.post("/issues/123/comments", json={
            "body": "Test comment"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 456
        assert data["body"] == "Test comment"
        assert data["user"] == "testuser"
    
    def test_comment_issue_missing_body(self):
        """Test issue commenting with missing required body."""
        response = client.post("/issues/123/comments", json={})
        
        assert response.status_code == 422  # Validation error

class TestWebhookRoutes:
    """Test webhook-related API routes."""
    
    def test_webhook_invalid_signature(self):
        """Test webhook with invalid signature."""
        response = client.post("/webhook", 
                             json={"test": "data"},
                             headers={"X-Hub-Signature-256": "invalid"})
        
        assert response.status_code == 401
    
    def test_webhook_unsupported_event_type(self):
        """Test webhook with unsupported event type."""
        import hmac
        import hashlib
        import json
        
        payload = b'{"test": "data"}'
        secret = "secret"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        response = client.post("/webhook",
                             content=payload,
                             headers={
                                 "X-Hub-Signature-256": f"sha256={signature}",
                                 "X-GitHub-Event": "push",
                                 "X-GitHub-Delivery": "test-delivery"
                             })
        
        assert response.status_code == 400
    
    def test_webhook_ping_event(self):
        """Test webhook ping event."""
        import hmac
        import hashlib
        
        payload = b'{"zen": "test"}'
        secret = "secret"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        response = client.post("/webhook",
                             content=payload,
                             headers={
                                 "X-Hub-Signature-256": f"sha256={signature}",
                                 "X-GitHub-Event": "ping",
                                 "X-GitHub-Delivery": "test-delivery"
                             })
        
        assert response.status_code == 204
    
    @patch('routers.webhook_routes.get_webhook_events')
    def test_get_events_success(self, mock_get_events):
        """Test successful events retrieval via API."""
        mock_get_events.return_value = [
            {
                "id": "delivery-123",
                "event": "issues",
                "action": "opened",
                "issue_number": 123,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        ]
        
        response = client.get("/events")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) == 1
        assert data["events"][0]["id"] == "delivery-123"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data

class TestValidationErrors:
    """Test input validation and error handling."""
    
    def test_invalid_issue_number_type(self):
        """Test invalid issue number type."""
        response = client.get("/issues/invalid")
        
        assert response.status_code == 422
    
    def test_invalid_pagination_parameters(self):
        """Test invalid pagination parameters."""
        response = client.get("/issues?page=0&per_page=200")
        
        assert response.status_code == 422
    
    def test_invalid_state_parameter(self):
        """Test invalid state parameter."""
        response = client.get("/issues?state=invalid")
        
        assert response.status_code == 422
    
    def test_invalid_update_state(self):
        """Test invalid update state."""
        response = client.patch("/issues/123", json={"state": "invalid"})
        
        assert response.status_code == 422

class TestErrorResponses:
    """Test error response formatting."""
    
    @patch('routers.handle_routes.get_github_issue')
    def test_404_error_response(self, mock_get):
        """Test 404 error response format."""
        from fastapi import HTTPException
        mock_get.side_effect = HTTPException(status_code=404, detail="Issue not found")
        
        response = client.get("/issues/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @patch('routers.handle_routes.create_github_issue')
    def test_400_error_response(self, mock_create):
        """Test 400 error response format."""
        from fastapi import HTTPException
        mock_create.side_effect = HTTPException(status_code=400, detail="Bad Request")
        
        response = client.post("/issues", json={"title": "Test"})
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
