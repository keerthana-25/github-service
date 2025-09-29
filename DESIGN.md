# Author: Arshan Bhanage (ArshanBhanage)
# Email: bhanagearshan@gmail.com
# Assignment: GitHub Issue Service - Design Documentation
# Date: September 29, 2025
# Description: System design and architecture documentation

# GitHub Issue Service - Design Document

**Author**: Keerthana (keerthana-25)  
**Date**: January 2024  
**Version**: 1.0.0

## 1. Overview

This document outlines the design decisions, architecture, and implementation details for the GitHub Issue Service, a FastAPI-based microservice that provides CRUD operations for GitHub issues and handles webhook events.

## 2. Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub API    │    │  Issue Service  │    │   Webhook       │
│                 │◄──►│                 │◄───│   Events        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │ (Event Storage) │
                       └─────────────────┘
```

### 2.2 Component Design

#### 2.2.1 FastAPI Application Layer
- **Main Application** (`main.py`): Entry point with route registration
- **Route Handlers** (`routers/`): HTTP endpoint implementations
- **Models** (`models/`): Pydantic models for request/response validation

#### 2.2.2 Service Layer
- **GitHub API Service** (`services/github_api_service.py`): External API integration
- **Webhook Service** (`services/webhook_service.py`): Webhook processing and storage

#### 2.2.3 Data Layer
- **Configuration** (`config.py`): Environment variable management
- **SQLite Database**: Webhook event persistence

## 3. Error Mapping Strategy

### 3.1 GitHub API Error Mapping

| GitHub Status | Service Response | Description |
|---------------|------------------|-------------|
| 200 | 200 OK | Successful operation |
| 201 | 201 Created | Resource created successfully |
| 400 | 400 Bad Request | Invalid request payload |
| 401 | 401 Unauthorized | Invalid or missing GitHub token |
| 403 | 403 Forbidden | Insufficient permissions |
| 404 | 404 Not Found | Resource not found |
| 422 | 422 Unprocessable Entity | Validation error |
| 429 | 429 Too Many Requests | Rate limit exceeded |
| 500 | 503 Service Unavailable | GitHub API server error |

### 3.2 Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3.3 Error Handling Implementation

- **Propagation**: GitHub API errors are mapped to appropriate HTTP status codes
- **Logging**: All errors are logged with request context
- **User-Friendly Messages**: Technical errors are translated to user-friendly messages
- **Retry Logic**: Rate limit errors include retry-after information

## 4. Pagination Strategy

### 4.1 GitHub API Pagination

GitHub uses Link headers for pagination:
```
Link: <https://api.github.com/repositories/123/issues?page=2>; rel="next",
      <https://api.github.com/repositories/123/issues?page=5>; rel="last"
```

### 4.2 Service Implementation

- **Forward Headers**: Link headers are forwarded from GitHub to client
- **Parameter Validation**: Page and per_page parameters are validated (1-100)
- **Default Values**: page=1, per_page=30
- **Error Handling**: Invalid pagination parameters return 422

### 4.3 Pagination Response Format

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 30,
    "total": 100
  }
}
```

## 5. Webhook Deduplication

### 5.1 Idempotency Strategy

- **Delivery ID**: GitHub provides unique delivery ID for each webhook
- **Database Constraint**: UNIQUE constraint on delivery_id column
- **INSERT OR IGNORE**: SQLite INSERT OR IGNORE prevents duplicate processing
- **Event Logging**: All events are logged for debugging

### 5.2 Deduplication Implementation

```sql
CREATE TABLE webhook_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id TEXT UNIQUE,  -- GitHub delivery ID
    event_type TEXT,
    action TEXT,
    issue_number INTEGER,
    payload TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 Event Processing Flow

1. **Signature Verification**: HMAC SHA-256 validation
2. **Event Parsing**: Extract event type and action
3. **Deduplication Check**: Check delivery_id in database
4. **Event Storage**: Store event if not already processed
5. **Response**: Return 204 No Content

## 6. Security Trade-offs

### 6.1 HMAC Signature Verification

**Implementation**:
- SHA-256 HMAC with webhook secret
- Constant-time comparison to prevent timing attacks
- Signature validation before any processing

**Trade-offs**:
- ✅ Prevents unauthorized webhook calls
- ✅ Ensures webhook authenticity
- ❌ Requires secret management
- ❌ Adds processing overhead

### 6.2 Environment Variable Security

**Implementation**:
- All secrets stored in environment variables
- .env file for local development
- Docker secrets for production

**Trade-offs**:
- ✅ No hardcoded secrets in code
- ✅ Easy configuration management
- ❌ Requires secure secret distribution
- ❌ Environment variable exposure risk

### 6.3 Database Security

**Implementation**:
- SQLite for simplicity
- Non-root container user
- File-based permissions

**Trade-offs**:
- ✅ Simple deployment
- ✅ No external dependencies
- ❌ Not suitable for high concurrency
- ❌ Limited security features

### 6.4 Container Security

**Implementation**:
- Multi-stage Docker build
- Non-root user execution
- Minimal base image
- Health checks

**Trade-offs**:
- ✅ Reduced attack surface
- ✅ Principle of least privilege
- ❌ Additional build complexity
- ❌ Potential permission issues

## 7. Performance Considerations

### 7.1 Rate Limiting

- **GitHub Limits**: Respect GitHub API rate limits
- **Header Forwarding**: Forward X-RateLimit-* headers
- **Error Handling**: Proper 429 responses with retry-after
- **Backoff Strategy**: Exponential backoff for retries

### 7.2 Caching Strategy

- **No Caching**: Current implementation doesn't cache
- **Future Enhancement**: ETag-based conditional requests
- **Trade-off**: Simplicity vs. performance

### 7.3 Database Performance

- **SQLite**: Suitable for low-medium traffic
- **Indexing**: Index on delivery_id for fast lookups
- **Connection Pooling**: Not applicable for SQLite
- **Future Enhancement**: PostgreSQL for high traffic

## 8. Monitoring and Observability

### 8.1 Logging Strategy

- **Structured Logging**: JSON format for machine parsing
- **Request IDs**: Unique identifier for request tracing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Sensitive Data**: Never log secrets or tokens

### 8.2 Health Checks

- **Endpoint**: GET /healthz
- **Response**: Service status and timestamp
- **Docker**: Health check configuration
- **Monitoring**: External monitoring integration

### 8.3 Metrics

- **Request Count**: Total requests per endpoint
- **Response Time**: Average response time
- **Error Rate**: Error percentage
- **Webhook Events**: Processed events count

## 9. Testing Strategy

### 9.1 Unit Tests

- **Coverage Target**: 80%+ line coverage
- **Mocking**: External API calls mocked
- **Isolation**: Each test is independent
- **Fast Execution**: Quick feedback loop

### 9.2 Integration Tests

- **Real API**: Tests against actual GitHub API
- **Webhook Testing**: Real webhook delivery testing
- **End-to-End**: Complete request/response cycle
- **Environment**: Requires valid GitHub token

### 9.3 Test Organization

```
tests/
├── test_github_api_service.py  # Service layer tests
├── test_webhook_service.py     # Webhook processing tests
├── test_routes.py              # API endpoint tests
└── test_integration.py         # Integration tests
```

## 10. Deployment Considerations

### 10.1 Environment Configuration

- **Development**: Local with .env file
- **Staging**: Docker with environment variables
- **Production**: Kubernetes with secrets management

### 10.2 Scaling Strategy

- **Horizontal**: Multiple container instances
- **Load Balancer**: nginx or cloud load balancer
- **Database**: PostgreSQL for high availability
- **Caching**: Redis for session storage

### 10.3 Security in Production

- **HTTPS**: SSL/TLS termination
- **Secrets Management**: Kubernetes secrets or HashiCorp Vault
- **Network Security**: Firewall rules and VPC
- **Monitoring**: Security event monitoring

## 11. Future Enhancements

### 11.1 Short Term

- **Conditional GET**: ETag-based caching
- **Rate Limiting**: Client-side rate limiting
- **Metrics**: Prometheus metrics endpoint
- **Documentation**: API versioning

### 11.2 Long Term

- **Microservices**: Split into smaller services
- **Event Streaming**: Kafka for webhook events
- **Machine Learning**: Issue classification
- **Multi-tenancy**: Support multiple repositories

## 12. Conclusion

The GitHub Issue Service is designed with simplicity, security, and maintainability in mind. The architecture balances ease of development with production readiness, making appropriate trade-offs for the current requirements while maintaining flexibility for future enhancements.

Key design principles:
- **Security First**: HMAC verification, environment variables, non-root execution
- **Simplicity**: SQLite database, straightforward architecture
- **Observability**: Comprehensive logging and health checks
- **Testability**: High test coverage with unit and integration tests
- **Scalability**: Container-based deployment with horizontal scaling potential
