# Author: Keerthana (keerthana-25)
# Email: keerthanapm257@gmail.com
# Assignment: GitHub Issue Service - Documentation
# Date: September 29, 2025
# Description: Comprehensive documentation and setup instructions

# GitHub Issue Service

A comprehensive FastAPI-based microservice for interacting with the GitHub Issues API. This service provides CRUD operations for issues and comments, webhook handling with HMAC verification, and comprehensive testing coverage.

## 🚀 Features

- **CRUD Operations**: Create, read, update, and close GitHub issues
- **Comment Management**: Add comments to issues
- **Webhook Handling**: Process GitHub webhooks with HMAC signature verification
- **Event Storage**: Store webhook events for debugging and idempotency
- **OpenAPI 3.1**: Complete API documentation with examples
- **Comprehensive Testing**: Unit and integration tests with 80%+ coverage
- **Docker Support**: Multi-stage Dockerfile with security best practices
- **Rate Limiting**: Respect GitHub API rate limits
- **Pagination**: Forward GitHub pagination headers
- **Health Checks**: Built-in health monitoring endpoints

## 📋 Requirements

- Python 3.11+
- GitHub Personal Access Token with Issues read/write permissions
- Docker (optional)

## 🛠️ Setup

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/keerthana-25/github-service.git
   cd github-service
   ```

2. **Install dependencies:**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file with the following variables:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_OWNER=your_github_username
   GITHUB_REPO=your_repository_name
   WEBHOOK_SECRET=your_webhook_secret
   PORT=8000
   ```

4. **Run the application:**
   ```bash
   make dev
   # or
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

1. **Build and run with Docker:**
   ```bash
   make docker-build
   make docker-run
   # or
   docker build -t github-issue-service .
   docker run --env-file .env -p 8000:8000 github-issue-service
   ```

2. **Using Docker Compose:**
   ```bash
   make docker-dev
   # or
   docker-compose up --build
   ```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Unit Tests Only
```bash
make test-unit
```

### Run Integration Tests Only
```bash
make test-integration
```

### Run Tests with Coverage
```bash
make test-coverage
```

### Test Coverage
The project maintains 80%+ test coverage with comprehensive unit and integration tests.

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### API Endpoints

#### Issues
- `POST /issues` — Create a new issue
- `GET /issues` — List issues with filtering and pagination
- `GET /issues/{issue_number}` — Get a specific issue
- `PATCH /issues/{issue_number}` — Update an issue

#### Comments
- `POST /issues/{issue_number}/comments` — Add a comment to an issue

#### Webhooks
- `POST /webhook` — GitHub webhook endpoint
- `GET /events` — Retrieve webhook events for debugging

#### System
- `GET /healthz` — Health check endpoint

## 🔧 API Examples

### Create an Issue
```bash
curl -X POST "http://localhost:8000/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug report",
    "body": "This is a bug description",
    "labels": ["bug", "high-priority"]
  }'
```

### List Issues with Filters
```bash
curl -X GET "http://localhost:8000/issues?state=open&labels=bug&page=1&per_page=10"
```

### Get a Specific Issue
```bash
curl -X GET "http://localhost:8000/issues/123"
```

### Update an Issue
```bash
curl -X PATCH "http://localhost:8000/issues/123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "state": "closed"
  }'
```

### Add a Comment
```bash
curl -X POST "http://localhost:8000/issues/123/comments" \
  -H "Content-Type: application/json" \
  -d '{"body": "This is a comment on the issue"}'
```

### Health Check
```bash
curl -X GET "http://localhost:8000/healthz"
```

## 🔗 Webhook Setup

### 1. Configure GitHub Webhook
1. Go to your repository settings
2. Navigate to "Webhooks" section
3. Click "Add webhook"
4. Set payload URL: `https://your-domain.com/webhook`
5. Set content type: `application/json`
6. Set secret: Use the same value as `WEBHOOK_SECRET`
7. Select events: "Issues" and "Issue comments"
8. Save the webhook

### 2. Local Testing with ngrok
```bash
# Install ngrok
npm install -g ngrok

# Start the service
make dev

# In another terminal, expose local port
ngrok http 8000

# Use the ngrok URL for webhook payload URL
```

### 3. Webhook Event Debugging
```bash
# View recent webhook events
curl -X GET "http://localhost:8000/events?limit=10"
```

## 🏗️ Architecture

### Project Structure
```
github-service/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── Dockerfile            # Multi-stage Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── openapi.yaml          # OpenAPI 3.1 specification
├── Makefile              # Development commands
├── pytest.ini           # Test configuration
├── models/               # Pydantic models
│   └── models.py
├── routers/              # API route handlers
│   ├── handle_routes.py  # Issue and comment routes
│   └── webhook_routes.py # Webhook routes
├── services/             # Business logic
│   ├── github_api_service.py # GitHub API integration
│   └── webhook_service.py    # Webhook processing
└── tests/                # Test suite
    ├── test_github_api_service.py
    ├── test_webhook_service.py
    ├── test_routes.py
    └── test_integration.py
```

### Key Components

1. **FastAPI Application**: Main application with automatic OpenAPI generation
2. **GitHub API Service**: Handles all GitHub API interactions with error handling
3. **Webhook Service**: Processes GitHub webhooks with HMAC verification
4. **Event Storage**: SQLite database for webhook event persistence
5. **Comprehensive Testing**: Unit and integration tests with mocking

## 🔒 Security Features

- **HMAC Signature Verification**: Validates GitHub webhook signatures
- **Constant-Time Comparison**: Prevents timing attacks
- **Non-Root Container**: Runs as non-privileged user
- **Environment Variables**: Secure configuration management
- **Input Validation**: Pydantic models for request/response validation

## 📊 Monitoring and Observability

- **Health Checks**: Built-in health monitoring
- **Structured Logging**: Comprehensive logging with request IDs
- **Event Storage**: Webhook event persistence for debugging
- **Error Handling**: Proper HTTP status codes and error messages
- **Rate Limit Handling**: Respects GitHub API rate limits

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Ensure all required environment variables are set
2. **Database**: Consider using PostgreSQL for production webhook event storage
3. **Reverse Proxy**: Use nginx or similar for production deployment
4. **SSL/TLS**: Enable HTTPS for webhook endpoints
5. **Monitoring**: Set up application monitoring and alerting
6. **Scaling**: Consider horizontal scaling for high-traffic scenarios

### Docker Production Deployment
```bash
# Build production image
docker build -t github-issue-service:latest .

# Run with production environment
docker run -d \
  --name github-issue-service \
  --env-file .env.production \
  -p 8000:8000 \
  --restart unless-stopped \
  github-issue-service:latest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Keerthana** (keerthana-25) - *Initial work and implementation*

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- GitHub for the comprehensive API
- The open-source community for various tools and libraries

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test cases for usage examples

---

**Note**: This service requires a GitHub Personal Access Token with appropriate permissions. Never commit tokens or secrets to version control.