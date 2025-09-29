# Author: Arshan Bhanage (ArshanBhanage)
# Email: bhanagearshan@gmail.com
# Assignment: GitHub Issue Service - Integration Testing Suite
# Date: September 29, 2025
# Description: End-to-end integration tests for webhook processing and API workflows
import pytest
import os
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

# Skip integration tests if no GitHub token is available
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
pytestmark = pytest.mark.skipif(
    not GITHUB_TOKEN, 
    reason="GitHub token not available for integration tests"
)

class TestGitHubAPIIntegration:
    """Integration tests with real GitHub API."""
    
    def test_create_and_retrieve_issue(self):
        """Test creating an issue and then retrieving it."""
        # Create a unique issue title to avoid conflicts
        issue_title = f"Integration Test Issue {int(time.time())}"
        
        # Create issue
        create_response = client.post("/issues", json={
            "title": issue_title,
            "body": "This is an integration test issue",
            "labels": ["test", "integration"]
        })
        
        assert create_response.status_code == 201
        created_issue = create_response.json()
        issue_number = created_issue["number"]
        assert created_issue["title"] == issue_title
        assert created_issue["state"] == "open"
        
        # Retrieve the created issue
        get_response = client.get(f"/issues/{issue_number}")
        assert get_response.status_code == 200
        retrieved_issue = get_response.json()
        assert retrieved_issue["number"] == issue_number
        assert retrieved_issue["title"] == issue_title
    
    def test_update_issue(self):
        """Test updating an issue."""
        # Create issue first
        issue_title = f"Update Test Issue {int(time.time())}"
        create_response = client.post("/issues", json={
            "title": issue_title,
            "body": "Original body"
        })
        assert create_response.status_code == 201
        issue_number = create_response.json()["number"]
        
        # Update the issue
        updated_title = f"Updated {issue_title}"
        update_response = client.patch(f"/issues/{issue_number}", json={
            "title": updated_title,
            "body": "Updated body",
            "state": "closed"
        })
        
        assert update_response.status_code == 200
        updated_issue = update_response.json()
        assert updated_issue["title"] == updated_title
        assert updated_issue["state"] == "closed"
    
    def test_comment_on_issue(self):
        """Test adding a comment to an issue."""
        # Create issue first
        issue_title = f"Comment Test Issue {int(time.time())}"
        create_response = client.post("/issues", json={
            "title": issue_title,
            "body": "Issue for commenting test"
        })
        assert create_response.status_code == 201
        issue_number = create_response.json()["number"]
        
        # Add comment
        comment_body = f"Integration test comment {int(time.time())}"
        comment_response = client.post(f"/issues/{issue_number}/comments", json={
            "body": comment_body
        })
        
        assert comment_response.status_code == 201
        comment = comment_response.json()
        assert comment["body"] == comment_body
        assert "user" in comment
        assert "created_at" in comment
    
    def test_list_issues_with_filters(self):
        """Test listing issues with various filters."""
        # Create a test issue
        issue_title = f"Filter Test Issue {int(time.time())}"
        create_response = client.post("/issues", json={
            "title": issue_title,
            "labels": ["integration-test"]
        })
        assert create_response.status_code == 201
        
        # Test listing open issues
        open_issues_response = client.get("/issues?state=open")
        assert open_issues_response.status_code == 200
        open_issues = open_issues_response.json()
        assert isinstance(open_issues, list)
        
        # Test listing with label filter
        labeled_issues_response = client.get("/issues?labels=integration-test")
        assert labeled_issues_response.status_code == 200
        labeled_issues = labeled_issues_response.json()
        assert isinstance(labeled_issues, list)
        
        # Test pagination
        paginated_response = client.get("/issues?page=1&per_page=5")
        assert paginated_response.status_code == 200
        paginated_issues = paginated_response.json()
        assert isinstance(paginated_issues, list)
        assert len(paginated_issues) <= 5
    
    def test_error_handling_integration(self):
        """Test error handling with real API responses."""
        # Test getting non-existent issue
        get_response = client.get("/issues/999999999")
        assert get_response.status_code == 404
        
        # Test commenting on non-existent issue
        comment_response = client.post("/issues/999999999/comments", json={
            "body": "This should fail"
        })
        assert comment_response.status_code == 404

class TestWebhookIntegration:
    """Integration tests for webhook functionality."""
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification with real HMAC."""
        import hmac
        import hashlib
        import json
        
        # Test payload
        payload = {
            "action": "opened",
            "issue": {
                "number": 123,
                "title": "Test Issue"
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Generate valid signature
        secret = "secret"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Mock the webhook secret
        with patch('config.WEBHOOK_SECRET', secret):
            response = client.post("/webhook",
                                 content=payload_bytes,
                                 headers={
                                     "X-Hub-Signature-256": f"sha256={signature}",
                                     "X-GitHub-Event": "issues",
                                     "X-GitHub-Delivery": "test-delivery-123"
                                 })
            
            assert response.status_code == 204
    
    def test_webhook_events_storage(self):
        """Test that webhook events are properly stored."""
        import hmac
        import hashlib
        import json
        
        payload = {
            "action": "opened",
            "issue": {
                "number": 456,
                "title": "Webhook Test Issue"
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        secret = "secret"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        with patch('config.WEBHOOK_SECRET', secret):
            # Send webhook
            webhook_response = client.post("/webhook",
                                         content=payload_bytes,
                                         headers={
                                             "X-Hub-Signature-256": f"sha256={signature}",
                                             "X-GitHub-Event": "issues",
                                             "X-GitHub-Delivery": "test-delivery-456"
                                         })
            assert webhook_response.status_code == 204
            
            # Check if event was stored
            events_response = client.get("/events")
            assert events_response.status_code == 200
            events_data = events_response.json()
            assert "events" in events_data
            # Note: In a real test, you might want to verify the specific event was stored

class TestRateLimitHandling:
    """Test rate limit handling with GitHub API."""
    
    @patch('services.github_api_service.requests.get')
    def test_rate_limit_response_handling(self, mock_get):
        """Test handling of GitHub rate limit responses."""
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "API rate limit exceeded"
        mock_response.headers = {"Retry-After": "60"}
        mock_get.return_value = mock_response
        
        response = client.get("/issues")
        assert response.status_code == 429
    
    @patch('services.github_api_service.requests.post')
    def test_server_error_handling(self, mock_post):
        """Test handling of GitHub server errors."""
        # Mock server error response
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_post.return_value = mock_response
        
        response = client.post("/issues", json={"title": "Test"})
        assert response.status_code == 503

class TestPaginationIntegration:
    """Test pagination functionality with real API."""
    
    def test_pagination_headers_forwarding(self):
        """Test that GitHub pagination headers are properly forwarded."""
        response = client.get("/issues?per_page=5")
        assert response.status_code == 200
        
        # Check if Link header is present (if GitHub provides it)
        # Note: This depends on the actual GitHub API response
        if "Link" in response.headers:
            assert isinstance(response.headers["Link"], str)

class TestDataValidationIntegration:
    """Test data validation with real API responses."""
    
    def test_issue_response_structure(self):
        """Test that issue responses have the expected structure."""
        # Create a test issue
        issue_title = f"Structure Test Issue {int(time.time())}"
        create_response = client.post("/issues", json={
            "title": issue_title,
            "body": "Test body",
            "labels": ["test"]
        })
        
        if create_response.status_code == 201:
            issue = create_response.json()
            
            # Verify required fields
            required_fields = ["number", "html_url", "state", "title", "created_at", "updated_at"]
            for field in required_fields:
                assert field in issue, f"Missing required field: {field}"
            
            # Verify data types
            assert isinstance(issue["number"], int)
            assert isinstance(issue["title"], str)
            assert issue["state"] in ["open", "closed"]
            assert isinstance(issue["labels"], list)
    
    def test_comment_response_structure(self):
        """Test that comment responses have the expected structure."""
        # Create a test issue first
        issue_title = f"Comment Structure Test {int(time.time())}"
        create_response = client.post("/issues", json={"title": issue_title})
        
        if create_response.status_code == 201:
            issue_number = create_response.json()["number"]
            
            # Add a comment
            comment_response = client.post(f"/issues/{issue_number}/comments", json={
                "body": "Test comment"
            })
            
            if comment_response.status_code == 201:
                comment = comment_response.json()
                
                # Verify required fields
                required_fields = ["id", "html_url", "body", "user", "created_at", "updated_at"]
                for field in required_fields:
                    assert field in comment, f"Missing required field: {field}"
                
                # Verify data types
                assert isinstance(comment["id"], int)
                assert isinstance(comment["body"], str)
                assert isinstance(comment["user"], str)
