# Author: Yashaswini Dinesh (yashaswinidinesh)
# Email: yashaswini.dinesh@sjsu.edu
# Assignment: GitHub Issue Service - Webhook Processing Service
# Date: September 29, 2025
# Description: Service layer for webhook signature verification and event processing
import hmac
import hashlib
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from config import WEBHOOK_SECRET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLite database for webhook events
def init_webhook_db():
    """Initialize SQLite database for storing webhook events."""
    conn = sqlite3.connect('webhook_events.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id TEXT UNIQUE,
            event_type TEXT,
            action TEXT,
            issue_number INTEGER,
            payload TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA-256.
    
    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret from environment
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False
    
    # Remove 'sha256=' prefix if present
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # Create expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)

def store_webhook_event(delivery_id: str, event_type: str, action: str, 
                       issue_number: Optional[int], payload: Dict[Any, Any]) -> None:
    """
    Store webhook event in SQLite database for debugging and idempotency.
    
    Args:
        delivery_id: GitHub delivery ID
        event_type: Type of event (issues, issue_comment, etc.)
        action: Action performed (opened, closed, created, etc.)
        issue_number: Issue number if applicable
        payload: Full webhook payload
    """
    try:
        conn = sqlite3.connect('webhook_events.db')
        cursor = conn.cursor()
        
        # Use INSERT OR IGNORE to handle duplicate delivery IDs (idempotency)
        cursor.execute('''
            INSERT OR IGNORE INTO webhook_events 
            (delivery_id, event_type, action, issue_number, payload)
            VALUES (?, ?, ?, ?, ?)
        ''', (delivery_id, event_type, action, issue_number, json.dumps(payload)))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored webhook event: {event_type}.{action} for issue {issue_number}")
        
    except Exception as e:
        logger.error(f"Failed to store webhook event: {e}")

def process_webhook_event(payload: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Process and extract relevant information from webhook payload.
    
    Args:
        payload: GitHub webhook payload
        
    Returns:
        dict: Processed event information
    """
    event_type = payload.get('action', 'unknown')
    issue_data = payload.get('issue', {})
    comment_data = payload.get('comment', {})
    
    # Extract issue number from different payload structures
    issue_number = None
    if 'issue' in payload:
        issue_number = issue_data.get('number')
    elif 'issue' in comment_data:
        issue_number = comment_data['issue'].get('number')
    
    return {
        'event_type': event_type,
        'issue_number': issue_number,
        'issue_title': issue_data.get('title', ''),
        'comment_body': comment_data.get('body', '') if comment_data else '',
        'user': payload.get('sender', {}).get('login', 'unknown')
    }

def get_webhook_events(limit: int = 50) -> list:
    """
    Retrieve recent webhook events for debugging.
    
    Args:
        limit: Maximum number of events to return
        
    Returns:
        list: Recent webhook events
    """
    try:
        conn = sqlite3.connect('webhook_events.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT delivery_id, event_type, action, issue_number, timestamp
            FROM webhook_events
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'event': row[1],
                'action': row[2],
                'issue_number': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        return events
        
    except Exception as e:
        logger.error(f"Failed to retrieve webhook events: {e}")
        return []

# Initialize database on module import
init_webhook_db()
