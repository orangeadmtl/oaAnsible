# macOS API for OrangeAd

This API provides system health, metrics, screenshots, and status information for macOS devices in the OrangeAd ecosystem. It's designed to be compatible with the dashboard interface.

## Features

- System metrics (CPU, memory, disk usage)
- Device information
- Service status
- Screenshot capture (when display is available)
- Health scoring and recommendations
- oaTracker status monitoring

## Development

### Code Formatting & Linting

This project uses Black, isort, flake8, and mypy for code quality. Install dependencies in the shared oaPangaea virtual environment:

```bash
# From oaPangaea root
source .venv/bin/activate
pip install -r oaAnsible/macos-api/requirements.txt
```

#### Format Code (auto-fix style issues)
```bash
# From oaAnsible/macos-api/
./format.sh        # Formats code with black & isort, then runs linting
```

#### Check Code Style (CI-friendly, no modifications)
```bash
# From oaAnsible/macos-api/
./check.sh         # Only checks, reports issues without fixing
```

**Key Difference:**
- `./format.sh` - **Formats** (modifies files) then **lints** (checks)
- `./check.sh` - **Only checks** (read-only, good for CI)

## Installation

The API is deployed via Ansible using the `macos_api` role. It runs as a launchd service.

### Manual Installation

```bash
# Create a Python virtual environment
cd /usr/local/orangead/macos-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the API
uvicorn main:app --host 0.0.0.0 --port 9090
```

## API Endpoints

### Health and System Information

- `GET /` - API information and version
- `GET /health` - Comprehensive health status including system, security, and tracker information
- `GET /health/summary` - Health summary with recommendations

### Screenshots

- `GET /screenshots/capture` - Capture a new screenshot
- `GET /screenshots/latest` - Get the latest screenshot
- `GET /screenshots/history` - Get screenshot history

### Camera Management

- `GET /cameras` - List all available cameras with details
- `GET /cameras/{camera_id}/stream` - Get MJPEG stream from a specific camera
- `GET /cameras/{camera_id}/snapshot` - Capture a single frame from a specific camera

### Tracker Integration

- `GET /tracker/status` - Get oaTracker service status
- `GET /tracker/stats` - Get oaTracker statistics (proxied from oaTracker API)
- `GET /actions/restart-tracker` - Restart the oaTracker service

### Device Actions

- `GET /actions/reboot` - Reboot the macOS device
- `GET /actions/restart-service` - Restart the macOS API service

## Service Details

- **Service Name**: com.orangead.macosapi
- **User**: Runs as the `ansible_user` (typically the `admin` user) for easier management and camera access permissions
- **Port**: 9090 (HTTP)
- **Working Directory**: /usr/local/orangead/macos-api
- **Logs**:
  - Standard output: /usr/local/orangead/macos-api/logs/api.log
  - Standard error: /usr/local/orangead/macos-api/logs/api-error.log
- **Startup**: Automatically starts on system boot via launchd

## Security Considerations

- **Network Security**: The API is only accessible via the Tailscale network, providing network-level isolation
- **IP-Based Access Control**: Access is restricted to devices on the Tailscale network with appropriate ACLs
- **No API Key**: The current implementation relies on Tailscale's network security rather than API keys
- **User Account**: The service runs as the `ansible_user` (typically the `admin` user) for easier management and camera access permissions
- **Filesystem Access**: The service has limited access to the filesystem, primarily its own directory

## Configuration

Configuration settings are in `core/config.py`.
