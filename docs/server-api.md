# Server API Documentation

The oaAnsible Server API provides RESTful endpoints for remote Ansible deployment management. This comprehensive guide covers all endpoints, authentication,
client usage, and integration patterns.

## Overview

The Server API enables:

- **Remote Execution**: Deploy components without direct SSH access
- **Job Management**: Queue, track, and monitor deployment jobs
- **Real-time Monitoring**: Live logs and status updates
- **Integration**: Seamless connection with oaDashboard and other services
- **Authentication**: Secure access control with JWT tokens

## Base Configuration

### Server Startup

```bash
# Development mode with auto-reload
./scripts/run-server --dev

# Production mode with custom settings
OAANSIBLE_API_PORT=8001 OAANSIBLE_SECRET_KEY="your-secret" ./scripts/run-server

# With oaDashboard integration
export OADASHBOARD_API_URL="http://localhost:8000"
export OADASHBOARD_API_KEY="your-dashboard-key"
./scripts/run-server
```

### Environment Variables

```bash
# Core Configuration
OAANSIBLE_API_HOST="0.0.0.0"           # Server bind address
OAANSIBLE_API_PORT="8001"              # Server port
OAANSIBLE_DEBUG="false"                # Debug mode
OAANSIBLE_SECRET_KEY="change-this"     # JWT secret key

# oaDashboard Integration
OADASHBOARD_API_URL="http://localhost:8000"
OADASHBOARD_API_KEY="your-api-key"

# Job Management
OAANSIBLE_MAX_CONCURRENT_JOBS="5"      # Max parallel jobs
OAANSIBLE_JOB_TIMEOUT_MINUTES="60"     # Job timeout
OAANSIBLE_DATABASE_URL="/tmp/jobs.db"  # Job database

# Logging
OAANSIBLE_LOG_LEVEL="INFO"             # Log level
OAANSIBLE_LOG_FILE="/tmp/oaansible.log" # Log file
```

## Authentication

### JWT Token Authentication

Most endpoints require a valid JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8001/api/jobs
```

### Token Sources

1. **oaDashboard Integration**: Existing user tokens
2. **Local Token Creation**: For development and testing
3. **API Keys**: For service-to-service communication

### Creating Local Tokens (Development)

```python
from server.auth.auth_manager import AuthManager

auth = AuthManager()
token = await auth.create_local_token(
    user_id="test-user",
    username="developer",
    email="dev@orangead.com",
    is_admin=True
)
print(f"Token: {token}")
```

## API Endpoints

### Health and Status

#### `GET /api/health`

Server health check and component status.

**Authentication**: None required  
**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "job_manager": "ready",
    "ansible_executor": "ready",
    "auth_manager": "ready"
  }
}
```

**Example**:

```bash
curl http://localhost:8001/api/health
```

### Environment and Component Information

#### `GET /api/environments`

List available deployment environments.

**Authentication**: Required  
**Response**:

```json
{
  "environments": [
    {
      "name": "staging",
      "description": "Staging environment",
      "host_count": 3,
      "available": true
    },
    {
      "name": "production",
      "description": "Production environment",
      "host_count": 12,
      "available": true
    }
  ]
}
```

#### `GET /api/components`

List available components with dependencies.

**Authentication**: Required  
**Response**:

```json
{
  "components": {
    "by_platform": {
      "macos": [
        {
          "name": "macos-api",
          "description": "Device monitoring and management API",
          "requires": ["python", "base-system"]
        },
        {
          "name": "macos-tracker",
          "description": "AI tracking and analysis system",
          "requires": ["python", "base-system", "macos-api"]
        }
      ],
      "universal": [
        {
          "name": "base-system",
          "description": "Foundation system configuration",
          "requires": []
        }
      ]
    },
    "all_components": ["macos-api", "macos-tracker", "base-system", "python", "node", "network-stack"]
  }
}
```

### Component Deployment

#### `POST /api/deploy/components`

Deploy selected components to target environment.

**Authentication**: Required  
**Content-Type**: `application/json`

**Request Body**:

```json
{
  "environment": "staging",
  "components": ["macos-api", "macos-tracker"],
  "target_hosts": ["host1", "host2"], // Optional, empty = all hosts
  "execution_mode": "normal", // normal, dry-run, check, force
  "options": {
    "verbose": true,
    "timeout_minutes": 30
  }
}
```

**Response**:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Deployment job queued successfully",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "details": {
    "environment": "staging",
    "components": ["macos-api", "macos-tracker"],
    "execution_mode": "normal"
  }
}
```

**Examples**:

```bash
# Basic deployment
curl -X POST http://localhost:8001/api/deploy/components \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "staging",
    "components": ["macos-api"]
  }'

# Dry-run deployment
curl -X POST http://localhost:8001/api/deploy/components \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "staging",
    "components": ["macos-tracker"],
    "execution_mode": "dry-run"
  }'

# Targeted deployment with options
curl -X POST http://localhost:8001/api/deploy/components \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "production",
    "components": ["macos-api", "network-stack"],
    "target_hosts": ["mac-mini-01", "mac-mini-02"],
    "execution_mode": "force",
    "options": {
      "verbose": true,
      "timeout_minutes": 45
    }
  }'
```

### Job Management

#### `GET /api/jobs`

List deployment jobs with pagination and filtering.

**Authentication**: Required  
**Query Parameters**:

- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20)
- `status_filter` (string): Filter by status (queued, running, completed, failed, cancelled)

**Response**:

```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "message": "Deployment completed successfully",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z",
      "details": {
        "environment": "staging",
        "components": ["macos-api"],
        "execution_mode": "normal",
        "user": "developer"
      }
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

**Examples**:

```bash
# List all jobs
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/api/jobs

# Filter by status
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8001/api/jobs?status_filter=running"

# Pagination
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8001/api/jobs?page=2&page_size=10"
```

#### `GET /api/jobs/{job_id}`

Get specific job details and status.

**Authentication**: Required  
**Response**:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Deploying macos-api component",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:00Z",
  "details": {
    "environment": "staging",
    "components": ["macos-api"],
    "execution_mode": "normal",
    "user": "developer",
    "progress": "Installing Python dependencies..."
  }
}
```

#### `GET /api/jobs/{job_id}/logs`

Get job execution logs.

**Authentication**: Required  
**Response**:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "logs": [
    "[2024-01-15T10:30:15Z] Starting component deployment...",
    "[2024-01-15T10:30:16Z] Validating component selection...",
    "[2024-01-15T10:30:17Z] ✅ Component validation passed",
    "[2024-01-15T10:30:18Z] Resolving dependencies: base-system → python → macos-api",
    "[2024-01-15T10:30:20Z] TASK [Deploy base-system] **********************",
    "[2024-01-15T10:30:25Z] ok: [mac-mini-01] => Base system already configured",
    "[2024-01-15T10:30:26Z] TASK [Deploy python] ***************************",
    "[2024-01-15T10:31:45Z] changed: [mac-mini-01] => Python environment updated"
  ]
}
```

#### `DELETE /api/jobs/{job_id}`

Cancel a running job.

**Authentication**: Required  
**Response**:

```json
{
  "message": "Job cancelled successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example**:

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/jobs/550e8400-e29b-41d4-a716-446655440000
```

## Client Library Usage

### Python Async Client

```python
from server.client import create_client

async def deploy_components():
    async with create_client("http://localhost:8001", token) as client:
        # Check server health
        health = await client.health_check()
        print(f"Server status: {health['status']}")

        # Get available components
        components = await client.get_components()
        print(f"Available components: {components['all_components']}")

        # Deploy components
        job = await client.deploy_components(
            environment="staging",
            components=["macos-api"],
            execution_mode="dry-run"
        )
        print(f"Job started: {job['job_id']}")

        # Monitor progress with real-time logs
        async for log_entry in client.stream_job_logs(job["job_id"]):
            print(f"[{job['job_id']}] {log_entry}")

        # Wait for completion
        result = await client.wait_for_job(job["job_id"])
        print(f"Job {result['status']}: {result['message']}")

# Run the deployment
import asyncio
asyncio.run(deploy_components())
```

### Python Sync Client

```python
from server.client import create_sync_client

# Create sync client
client = create_sync_client("http://localhost:8001", token)

# Simple operations
health = client.health_check()
print(f"Server healthy: {health['status'] == 'healthy'}")

# Deploy and get job info
job = client.deploy_components("staging", ["macos-api"])
print(f"Job ID: {job['job_id']}")

# Check job status
status = client.get_job(job["job_id"])
print(f"Job status: {status['status']}")
```

### Advanced Client Usage

```python
async def advanced_deployment():
    async with create_client("http://localhost:8001", token) as client:
        # Deploy with wait and error handling
        try:
            result = await client.deploy_and_wait(
                environment="staging",
                components=["macos-tracker"],
                timeout=1800  # 30 minutes
            )

            if result["success"]:
                print("✅ Deployment successful!")
                print(f"Duration: {result['job']['duration']}s")
            else:
                print("❌ Deployment failed!")
                logs = await client.get_job_logs(result["job"]["job_id"])
                print("Last 10 log entries:")
                for log in logs[-10:]:
                    print(f"  {log}")

        except Exception as e:
            print(f"Deployment error: {e}")

        # Get deployment status for environment
        status = await client.get_deployment_status("staging")
        print(f"Environment status: {status['status']}")
        print(f"Active deployments: {status['active_deployments']}")
```

## Integration Patterns

### oaDashboard Integration

```python
# In oaDashboard backend service
from server.client import create_client

class AnsibleService:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token

    async def deploy_to_device(self, device_id: str, components: list):
        async with create_client(self.api_url, self.api_token) as client:
            # Deploy components to specific device
            job = await client.deploy_components(
                environment="production",
                components=components,
                target_hosts=[device_id]
            )

            # Return job ID for tracking
            return job["job_id"]

    async def get_deployment_progress(self, job_id: str):
        async with create_client(self.api_url, self.api_token) as client:
            job = await client.get_job(job_id)
            logs = await client.get_job_logs(job_id)

            return {
                "status": job["status"],
                "progress": job.get("details", {}).get("progress"),
                "recent_logs": logs[-5:]  # Last 5 log entries
            }
```

### WebSocket Integration (Future)

```python
# Real-time job monitoring with WebSocket
import websockets
import json

async def monitor_job_realtime(job_id: str):
    uri = f"ws://localhost:8002/ws/jobs/{job_id}"

    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "log":
                print(f"[LOG] {data['message']}")
            elif data["type"] == "status":
                print(f"[STATUS] {data['status']}")
            elif data["type"] == "completed":
                print(f"[DONE] Job completed: {data['status']}")
                break
```

### REST API Testing

```bash
#!/bin/bash
# Test script for API endpoints

BASE_URL="http://localhost:8001"
TOKEN="your-jwt-token"
AUTH_HEADER="Authorization: Bearer $TOKEN"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$BASE_URL/api/health" | jq .

# Test authentication
echo "Testing authenticated endpoint..."
curl -s -H "$AUTH_HEADER" "$BASE_URL/api/environments" | jq .

# Test component deployment
echo "Testing component deployment..."
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/deploy/components" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "staging",
    "components": ["macos-api"],
    "execution_mode": "dry-run"
  }')

echo "Job response: $JOB_RESPONSE"
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id')

# Monitor job progress
echo "Monitoring job: $JOB_ID"
while true; do
  STATUS=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/api/jobs/$JOB_ID" | jq -r '.status')
  echo "Job status: $STATUS"

  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" || "$STATUS" == "cancelled" ]]; then
    break
  fi

  sleep 2
done

# Get final logs
echo "Final job logs:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/api/jobs/$JOB_ID/logs" | jq -r '.logs[]'
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (job/resource not found)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "detail": "Component validation failed: Invalid components: invalid-component",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Scenarios

#### Authentication Errors

```bash
# Missing token
curl http://localhost:8001/api/jobs
# Response: 401 Unauthorized

# Invalid token
curl -H "Authorization: Bearer invalid-token" http://localhost:8001/api/jobs
# Response: 401 Unauthorized - Invalid authentication token
```

#### Validation Errors

```bash
# Invalid component
curl -X POST http://localhost:8001/api/deploy/components \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"environment": "staging", "components": ["invalid-component"]}'
# Response: 400 Bad Request - Invalid components: invalid-component

# Platform conflict
curl -X POST http://localhost:8001/api/deploy/components \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"environment": "staging", "components": ["ubuntu-docker", "macos-api"]}'
# Response: 400 Bad Request - Platform conflicts detected
```

## Performance and Scaling

### Concurrent Job Limits

```bash
# Configure maximum concurrent jobs
export OAANSIBLE_MAX_CONCURRENT_JOBS=10

# Monitor active jobs
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/jobs?status_filter=running"
```

### Database Management

```python
# Job cleanup (automatic)
# Old completed jobs are automatically cleaned up after 7 days

# Manual cleanup
from server.jobs.job_manager import JobManager

job_manager = JobManager()
deleted_count = await job_manager.cleanup_old_jobs(days_old=3)
print(f"Cleaned up {deleted_count} old jobs")

# Job statistics
stats = await job_manager.get_job_statistics()
print(f"Total jobs: {stats['total_jobs']}")
print(f"Jobs last 24h: {stats['jobs_last_24h']}")
```

### Performance Monitoring

```bash
# Server metrics (if enabled)
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8001/api/metrics

# Job performance analysis
./scripts/measure-performance staging server-api
```

---

**Server API** - REST endpoints for remote Ansible execution  
Part of the Advanced Multi-Platform Orchestration System
