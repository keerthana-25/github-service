# Author: Arshan Bhanage (ArshanBhanage)
# Email: bhanagearshan@gmail.com
# Assignment: GitHub Issue Service - Webhook Service Testing
# Date: September 29, 2025
# Description: Unit tests for webhook signature verification and event processing
import pytest
import hmac
import hashlib
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from services.webhook_service import (
    verify_webhook_signature,
    store_webhook_event,
    process_webhook_event,
    get_webhook_events
)

class TestWebhookSignatureVerification:
    """Test webhook signature verification functionality."""
    
    def test_verify_valid_signature(self):
        """Test verification of valid HMAC signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        result = verify_webhook_signature(payload, signature, secret)
        assert result is True
    
    def test_verify_invalid_signature(self):
        """Test verification of invalid HMAC signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        invalid_signature = "invalid_signature"
        
        result = verify_webhook_signature(payload, invalid_signature, secret)
        assert result is False
    
    def test_verify_signature_with_sha256_prefix(self):
        """Test verification with 'sha256=' prefix in signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        
        # Generate signature with prefix
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        signature_with_prefix = f"sha256={signature}"
        
        result = verify_webhook_signature(payload, signature_with_prefix, secret)
        assert result is True
    
    def test_verify_signature_empty_secret(self):
        """Test verification with empty secret."""
        payload = b'{"test": "data"}'
        secret = ""
        signature = "some_signature"
        
        result = verify_webhook_signature(payload, signature, secret)
        assert result is False
    
    def test_verify_signature_empty_signature(self):
        """Test verification with empty signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        signature = ""
        
        result = verify_webhook_signature(payload, signature, secret)
        assert result is False

class TestWebhookEventProcessing:
    """Test webhook event processing functionality."""
    
    def test_process_issues_event(self):
        """Test processing of issues webhook event."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 123,
                "title": "Test Issue",
                "state": "open"
            },
            "sender": {
                "login": "testuser"
            }
        }
        
        result = process_webhook_event(payload)
        
        assert result["event_type"] == "opened"
        assert result["issue_number"] == 123
        assert result["issue_title"] == "Test Issue"
        assert result["user"] == "testuser"
    
    def test_process_issue_comment_event(self):
        """Test processing of issue_comment webhook event."""
        payload = {
            "action": "created",
            "comment": {
                "body": "This is a comment",
                "issue": {
                    "number": 456
                }
            },
            "sender": {
                "login": "commenter"
            }
        }
        
        result = process_webhook_event(payload)
        
        assert result["event_type"] == "created"
        assert result["issue_number"] == 456
        assert result["comment_body"] == "This is a comment"
        assert result["user"] == "commenter"
    
    def test_process_event_without_issue(self):
        """Test processing event without issue data."""
        payload = {
            "action": "ping",
            "sender": {
                "login": "github"
            }
        }
        
        result = process_webhook_event(payload)
        
        assert result["event_type"] == "ping"
        assert result["issue_number"] is None
        assert result["user"] == "github"

class TestWebhookEventStorage:
    """Test webhook event storage functionality."""
    
    @patch('services.webhook_service.sqlite3.connect')
    def test_store_webhook_event_success(self, mock_connect):
        """Test successful storage of webhook event."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        delivery_id = "test-delivery-123"
        event_type = "issues"
        action = "opened"
        issue_number = 123
        payload = {"test": "data"}
        
        store_webhook_event(delivery_id, event_type, action, issue_number, payload)
        
        # Verify database operations
        mock_connect.assert_called_once_with('webhook_events.db')
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('services.webhook_service.sqlite3.connect')
    def test_store_webhook_event_database_error(self, mock_connect):
        """Test handling of database errors during storage."""
        mock_connect.side_effect = Exception("Database error")
        
        # Should not raise exception, just log error
        store_webhook_event("test-id", "issues", "opened", 123, {})
        
        mock_connect.assert_called_once()

class TestWebhookEventRetrieval:
    """Test webhook event retrieval functionality."""
    
    @patch('services.webhook_service.sqlite3.connect')
    def test_get_webhook_events_success(self, mock_connect):
        """Test successful retrieval of webhook events."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database response
        mock_cursor.fetchall.return_value = [
            ("delivery-123", "issues", "opened", 123, "2024-01-15T10:30:00Z"),
            ("delivery-124", "issue_comment", "created", 123, "2024-01-15T10:35:00Z")
        ]
        
        events = get_webhook_events(limit=10)
        
        # Verify database operations
        mock_connect.assert_called_once_with('webhook_events.db')
        mock_cursor.execute.assert_called_once()
        
        # Verify returned data
        assert len(events) == 2
        assert events[0]["id"] == "delivery-123"
        assert events[0]["event"] == "issues"
        assert events[0]["action"] == "opened"
        assert events[0]["issue_number"] == 123
    
    @patch('services.webhook_service.sqlite3.connect')
    def test_get_webhook_events_database_error(self, mock_connect):
        """Test handling of database errors during retrieval."""
        mock_connect.side_effect = Exception("Database error")
        
        events = get_webhook_events()
        
        # Should return empty list on error
        assert events == []
        mock_connect.assert_called_once()

class TestWebhookEventIdempotency:
    """Test webhook event idempotency functionality."""
    
    @patch('services.webhook_service.sqlite3.connect')
    def test_duplicate_delivery_id_handling(self, mock_connect):
        """Test that duplicate delivery IDs are handled gracefully."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # First call
        store_webhook_event("duplicate-id", "issues", "opened", 123, {})
        
        # Second call with same delivery ID
        store_webhook_event("duplicate-id", "issues", "opened", 123, {})
        
        # Should be called twice (no exception raised)
        assert mock_connect.call_count == 2
