# Author: Yashaswini Dinesh (yashaswinidinesh)
# Email: yashaswini.dinesh@sjsu.edu
# Assignment: GitHub Issue Service - Webhook Handling Routes
# Date: September 29, 2025
# Description: FastAPI routes for GitHub webhook processing and event handling

import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from services.webhook_service import (
    verify_webhook_signature,
    store_webhook_event,
    process_webhook_event,
    get_webhook_events
)
from config import WEBHOOK_SECRET

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/webhook")
async def webhook_get():
    """
    Handle GET requests to webhook endpoint (GitHub verification).
    """
    return {"message": "GitHub Issue Service Webhook Endpoint", "status": "active"}

@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle GitHub webhook events with HMAC signature verification.
    
    Accepts events: issues, issue_comment, and ping.
    Stores events for debugging and ensures idempotency.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get headers
        signature = request.headers.get('X-Hub-Signature-256')
        event_type = request.headers.get('X-GitHub-Event')
        delivery_id = request.headers.get('X-GitHub-Delivery')
        
        # Verify signature
        if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
            logger.warning(f"Invalid webhook signature for delivery {delivery_id}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Handle ping events (GitHub webhook test)
        if event_type == 'ping':
            logger.info(f"Received ping event: {delivery_id}")
            return Response(status_code=204)
        
        # Only process issues and issue_comment events
        if event_type not in ['issues', 'issue_comment']:
            logger.warning(f"Unsupported event type: {event_type}")
            raise HTTPException(status_code=400, detail=f"Unsupported event type: {event_type}")
        
        # Extract action from payload
        action = payload.get('action', 'unknown')
        
        # Process and store the event
        processed_event = process_webhook_event(payload)
        issue_number = processed_event.get('issue_number')
        
        store_webhook_event(
            delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            issue_number=issue_number,
            payload=payload
        )
        
        # Log the event
        logger.info(f"Processed {event_type}.{action} for issue {issue_number} (delivery: {delivery_id})")
        
        # Return 204 No Content (quick acknowledgment)
        return Response(status_code=204)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/events")
async def get_events(limit: int = 50):
    """
    Retrieve recent webhook events for debugging.
    
    Args:
        limit: Maximum number of events to return (default: 50)
        
    Returns:
        JSON response with recent webhook events
    """
    try:
        events = get_webhook_events(limit)
        return JSONResponse(content={"events": events})
    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve events")

@router.get("/healthz")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with service status
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "github-issue-service",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
