# macOS API

FastAPI service providing system health monitoring, metrics collection, and device management for macOS devices in the OrangeAd ecosystem.

## Overview

**Service:** LaunchAgent running on Mac Mini devices (port 9090)  
**Purpose:** Raw health data collection, oaTracker integration, device actions  
**Deployment:** Automated via oaAnsible to `{{ ansible_user_dir }}/orangead/macos-api/`

📚 **[Complete Documentation](../../docs/README.md)**

## Key Features

- **Health Monitoring:** Raw system metrics (CPU, memory, disk, network)
- **oaTracker Integration:** Status monitoring and MJPEG stream proxying
- **Camera Management:** List cameras and provide streaming endpoints
- **Device Actions:** Reboot device, restart services
- **Security Status:** macOS firewall, FileVault, Gatekeeper monitoring

## Quick Start

```bash
# Development (from oaPangaea root with shared venv)
source .venv/bin/activate
pip install -r oaAnsibe/macos-api/requirements.txt

# Code formatting
./format.sh    # Format and lint code
./check.sh     # Check only (CI-friendly)

# Manual run (on Mac Mini)
uvicorn main:app --host 0.0.0.0 --port 9090
```

## API Endpoints

**Health & Status:**
- `GET /health` - Comprehensive device health status
- `GET /` - API information and version

**Camera & Streaming:**
- `GET /cameras` - List available cameras
- `GET /cameras/{id}/stream` - MJPEG camera stream
- `GET /tracker/stream` - Proxied oaTracker stream

**Device Actions:**
- `GET /actions/reboot` - Reboot device
- `GET /actions/restart-tracker` - Restart oaTracker service

## Key Documentation

- 🏗️ **[System Architecture](../../docs/architecture/system_overview.md)** - Component overview
- 📊 **[Health Scoring](../../docs/monitoring/health_scoring.md)** - Metrics details
- 🚀 **[Infrastructure Guide](../../docs/infrastructure/deployment.md)** - Deployment via Ansible
- ⚡ **[Getting Started](../../docs/development/getting_started.md)** - Development workflow

## Service Configuration

**LaunchAgent:** `com.orangead.macosapi`  
**Port:** 9090 (HTTP)  
**User:** `ansible_user` (typically `admin`)  
**Logs:** `~/orangead/macos-api/logs/`  
**Security:** Tailscale network access only
