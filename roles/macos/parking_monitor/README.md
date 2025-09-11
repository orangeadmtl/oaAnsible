# Parking Monitor Role

Ansible role for deploying the oaParkingMonitor service on macOS systems. This role handles the complete deployment pipeline from repository cloning to service activation.

## Overview

The Parking Monitor role deploys a YOLOv11-based intelligent parking space detection system optimized for Mac Mini M1. It provides real-time parking occupancy monitoring with vehicle classification capabilities.

## Features

- **YOLOv11m Detection Engine**: Optimized for Mac M1 with CoreML acceleration
- **Real-time Processing**: 30+ FPS parking space detection
- **Vehicle Classification**: Car type and attribute detection  
- **Display Integration**: Ad display with detection overlay
- **Health Monitoring**: Comprehensive service health tracking
- **API Service**: FastAPI endpoints for oaDashboard integration

## Requirements

### System Requirements
- macOS 12.0+ (Monterey or later for M1 support)
- Mac Mini M1/M2 or MacBook with Apple Silicon
- Minimum 8GB RAM (16GB recommended)
- Camera access permissions
- Python 3.12+

### Dependencies
- `common/device_api` role (for health proxy)
- `macos/python` role (for Python environment)
- `macos/security` role (for camera permissions)

## Role Variables

### Required Variables
```yaml
# Repository configuration
parking_monitor_repository_url: "https://github.com/oa-device/oaParkingMonitor.git"
parking_monitor_branch: "main"

# Service configuration
parking_monitor_port: 9091
parking_monitor_python_version: "3.12"
```

### Optional Variables
```yaml
# Detection configuration
parking_monitor_detection:
  model: "yolo11m"
  confidence_threshold: 0.5
  target_fps: 30
  device: "mps"

# Camera configuration  
parking_monitor_camera:
  source: 0
  resolution: [1920, 1080]
  fps: 30

# Display configuration
parking_monitor_display:
  overlay_enabled: true
  overlay_opacity: 0.7
  show_vehicle_info: true
```

## Example Playbook

```yaml
- hosts: mac_devices
  become: false
  roles:
    - role: macos/parking_monitor
      vars:
        parking_monitor_branch: "main"
        parking_monitor_detection:
          confidence_threshold: 0.6
          target_fps: 30
        parking_monitor_camera:
          source: 0
        parking_monitor_display:
          overlay_enabled: true
```

## Service Management

The role creates a LaunchAgent service that:
- Automatically starts on user login
- Restarts on failure
- Provides structured logging
- Exposes health check endpoints

### Service Control
```bash
# Start service
launchctl load ~/Library/LaunchAgents/com.orangead.parking-monitor.plist

# Stop service  
launchctl unload ~/Library/LaunchAgents/com.orangead.parking-monitor.plist

# Check status
launchctl list | grep parking-monitor
```

## API Endpoints

The deployed service exposes these endpoints:

- `GET /health` - Service health check
- `GET /api/parking/status` - Current parking occupancy
- `GET /api/parking/metrics` - Performance metrics
- `GET /api/parking/stream` - Real-time detection stream (WebSocket)

## Integration

### oaDashboard Integration
The service integrates with oaDashboard for:
- Real-time parking space monitoring
- Performance metrics collection
- Health status reporting
- Remote service management

### Other Services Compatibility
- **Player**: Compatible with display overlay integration
- **Device API**: Proxies health and metrics data
- **Tracker**: Parallel AI processing (no conflicts)
- **CamGuard**: May require camera coordination

## Troubleshooting

### Common Issues

1. **Camera Access Denied**
   ```bash
   # Grant camera permissions via System Preferences
   # Or run: tccutil reset Camera
   ```

2. **Model Download Fails**
   ```bash
   # Check network connectivity
   # Verify Python environment
   ```

3. **Service Won't Start**
   ```bash
   # Check logs: tail -f /tmp/oaParkingMonitor.err
   # Verify Python environment: cd ~/orangead/oaParkingMonitor && uv run python --version
   ```

### Log Locations
- Service logs: `~/orangead/oaParkingMonitor/logs/`
- System logs: `/tmp/oaParkingMonitor.out|err`
- Health logs: Available via `/api/parking/metrics` endpoint

## Development

### Testing the Role
```bash
# Run role in check mode
ansible-playbook -i inventory/test.yml playbook.yml --check --diff

# Deploy to staging
ansible-playbook -i inventory/staging.yml playbook.yml -t parking-monitor
```

### Model Optimization
The role automatically:
1. Downloads YOLOv11 base models
2. Exports to CoreML format for M1 optimization
3. Validates model performance
4. Falls back to lighter models if needed

## License

MIT License - See LICENSE file for details

## Maintenance

### Regular Tasks
- Monitor model accuracy and performance
- Update models as needed
- Review and rotate logs
- Validate camera positioning and coverage

### Updates
The role supports:
- Rolling updates with health checks
- Model updates without service restart
- Configuration updates with automatic reload