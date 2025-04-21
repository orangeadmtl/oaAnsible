# macOS API for OrangeAd

This API provides system health, metrics, screenshots, and status information for macOS devices in the OrangeAd ecosystem. It's designed to be compatible with the dashboard interface and mirrors the functionality of the opi-setup API for OrangePi devices.

## Features

- System metrics (CPU, memory, disk usage)
- Device information
- Service status
- Screenshot capture (when display is available)
- Health scoring and recommendations
- oaTracker status monitoring

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

- `GET /` - API information
- `GET /health` - Comprehensive health status
- `GET /health/summary` - Health summary with recommendations
- `GET /screenshots/capture` - Capture a new screenshot
- `GET /screenshots/latest` - Get the latest screenshot
- `GET /screenshots/history` - Get screenshot history

## Configuration

Configuration settings are in `core/config.py`.
