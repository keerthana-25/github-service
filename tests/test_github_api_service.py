# Author: Arshan Bhanage (ArshanBhanage)
# Email: bhanagearshan@gmail.com
# Assignment: GitHub Issue Service - GitHub API Service Testing
# Date: September 29, 2025
# Description: Unit tests for GitHub API service functions and error handling
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from services.github_api_service import (
    create_github_issue,
    get_github_issues,
    get_github_issue,
    update_github_issue,
    comment_github_issue
)

class TestCreateGitHubIssue:
    """Test GitHub issue creation functionality."""
    
    @patch('services.github_api_service.requests.post')
    def test_create_issue_success(self, mock_post):
        """Test successful issue creation."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 123,
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        mock_post.return_value = mock_response
        
        result = create_github_issue("Test Issue", "Test body", ["bug"])
        
        assert result["number"] == 123
        assert result["title"] == "Test Issue"
        assert result["state"] == "open"
        mock_post.assert_called_once()
    
    def test_create_issue_missing_title(self):
        """Test issue creation with missing title."""
        with pytest.raises(ValueError, match="The required field Title is missing"):
            create_github_issue(None, "Test body", ["bug"])
    
    @patch('services.github_api_service.requests.post')
    def test_create_issue_api_error(self, mock_post):
        """Test issue creation with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            create_github_issue("Test Issue", "Test body", ["bug"])
        
        assert exc_info.value.status_code == 400
    
    @patch('services.github_api_service.requests.post')
    def test_create_issue_minimal_payload(self, mock_post):
        """Test issue creation with minimal payload."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"number": 123}
        mock_post.return_value = mock_response
        
        create_github_issue("Test Issue", None, None)
        
        # Verify minimal payload was sent
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["title"] == "Test Issue"
        assert "body" not in payload
        assert "labels" not in payload

class TestGetGitHubIssues:
    """Test GitHub issues retrieval functionality."""
    
    @patch('services.github_api_service.requests.get')
    def test_get_issues_success(self, mock_get):
        """Test successful issues retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 123,
                "title": "Issue 1",
                "state": "open",
                "labels": [{"name": "bug"}]
            }
        ]
        mock_response.headers = {"Link": "<next>; rel=\"next\""}
        mock_get.return_value = mock_response
        
        issues, link_header = get_github_issues("open", "bug", 1, 30)
        
        assert len(issues) == 1
        assert issues[0]["number"] == 123
        assert link_header == "<next>; rel=\"next\""
        mock_get.assert_called_once()
    
    @patch('services.github_api_service.requests.get')
    def test_get_issues_api_error(self, mock_get):
        """Test issues retrieval with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            get_github_issues("open", None, 1, 30)
        
        assert exc_info.value.status_code == 401
    
    @patch('services.github_api_service.requests.get')
    def test_get_issues_with_pagination(self, mock_get):
        """Test issues retrieval with pagination parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        get_github_issues("closed", "enhancement", 2, 50)
        
        # Verify pagination parameters were passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["state"] == "closed"
        assert call_args[1]["params"]["labels"] == "enhancement"
        assert call_args[1]["params"]["page"] == 2
        assert call_args[1]["params"]["per_page"] == 50

class TestGetGitHubIssue:
    """Test single GitHub issue retrieval functionality."""
    
    @patch('services.github_api_service.requests.get')
    def test_get_single_issue_success(self, mock_get):
        """Test successful single issue retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "number": 123,
            "title": "Test Issue",
            "state": "open"
        }
        mock_get.return_value = mock_response
        
        result = get_github_issue(123)
        
        assert result["number"] == 123
        assert result["title"] == "Test Issue"
        mock_get.assert_called_once()
    
    @patch('services.github_api_service.requests.get')
    def test_get_single_issue_not_found(self, mock_get):
        """Test single issue retrieval with 404 error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            get_github_issue(999)
        
        assert exc_info.value.status_code == 404

class TestUpdateGitHubIssue:
    """Test GitHub issue update functionality."""
    
    @patch('services.github_api_service.requests.patch')
    def test_update_issue_success(self, mock_patch):
        """Test successful issue update."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "number": 123,
            "title": "Updated Issue",
            "state": "closed"
        }
        mock_patch.return_value = mock_response
        
        result = update_github_issue(123, "Updated Issue", "Updated body", "closed")
        
        assert result["title"] == "Updated Issue"
        assert result["state"] == "closed"
        mock_patch.assert_called_once()
    
    @patch('services.github_api_service.requests.patch')
    def test_update_issue_partial_update(self, mock_patch):
        """Test partial issue update (only title)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"number": 123}
        mock_patch.return_value = mock_response
        
        update_github_issue(123, "New Title", None, None)
        
        # Verify only title was included in payload
        call_args = mock_patch.call_args
        payload = call_args[1]["json"]
        assert payload["title"] == "New Title"
        assert "body" not in payload
        assert "state" not in payload
    
    @patch('services.github_api_service.requests.patch')
    def test_update_issue_api_error(self, mock_patch):
        """Test issue update with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_patch.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            update_github_issue(123, "New Title", None, None)
        
        assert exc_info.value.status_code == 403

class TestCommentGitHubIssue:
    """Test GitHub issue commenting functionality."""
    
    @patch('services.github_api_service.requests.post')
    def test_comment_issue_success(self, mock_post):
        """Test successful issue commenting."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 456,
            "html_url": "https://github.com/owner/repo/issues/123#issuecomment-456",
            "body": "Test comment",
            "user": {"login": "testuser"},
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        mock_post.return_value = mock_response
        
        result = comment_github_issue(123, "Test comment")
        
        assert result["id"] == 456
        assert result["body"] == "Test comment"
        assert result["user"]["login"] == "testuser"
        mock_post.assert_called_once()
    
    def test_comment_issue_missing_body(self):
        """Test issue commenting with missing body."""
        with pytest.raises(ValueError, match="The required field Body is missing"):
            comment_github_issue(123, None)
    
    @patch('services.github_api_service.requests.post')
    def test_comment_issue_api_error(self, mock_post):
        """Test issue commenting with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Issue not found"
        mock_post.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            comment_github_issue(999, "Test comment")
        
        assert exc_info.value.status_code == 404

class TestErrorHandling:
    """Test error handling in GitHub API service."""
    
    @patch('services.github_api_service.requests.post')
    def test_network_error_handling(self, mock_post):
        """Test handling of network errors."""
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            create_github_issue("Test", "Body", [])
    
    @patch('services.github_api_service.requests.get')
    def test_rate_limit_handling(self, mock_get):
        """Test handling of rate limit errors."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            get_github_issues("open", None, 1, 30)
        
        assert exc_info.value.status_code == 429
