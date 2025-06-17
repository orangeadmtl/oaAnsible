# ALPR Integration Guide

This guide covers the integrated ALPR (Automatic License Plate Recognition) stack within the oaAnsible deployment system.

## 📁 Integration Status

✅ **FULLY INTEGRATED** - The ALPR stack is now completely embedded within oaAnsible:

- **Source Files**: Located in `roles/macos/alpr_service/files/`
- **Configuration**: Managed via Ansible templates and variables
- **Deployment**: No external dependencies required
- **Management**: Full LaunchAgent and service integration

## 🎥 ALPR Stack Components

The ALPR integration provides a complete vehicle detection and license plate recognition solution:

### Components Deployed

1. **PlateRecognizer Docker Service**

   - Commercial ALPR API service running in Docker
   - Provides high-accuracy plate recognition
   - Supports vehicle make/model/color detection
   - Accessible on port 8081

2. **Python ALPR Monitor**

   - Real-time camera monitoring using YOLO and OpenCV
   - Detects vehicles in camera feed
   - Captures best quality images for recognition
   - Automatically sends images to PlateRecognizer service

3. **Supporting Infrastructure**
   - OrbStack for macOS Docker support
   - Python environment with required packages
   - Camera permissions and security setup
   - LaunchAgent services for auto-start

## 📋 Prerequisites

### PlateRecognizer Account

- Valid PlateRecognizer subscription
- API token and license key
- 50,000 recognitions/month typical plan

### Hardware Requirements

- macOS system (Physical hardware recommended)
- Camera access (built-in or USB camera)
- Minimum 4GB RAM for Docker containers
- Internet connectivity for API validation

### oaAnsible Setup

- Configured Ansible environment
- Vault credentials properly encrypted
- Target macOS system accessible via SSH

## 📋 Integration Files

The ALPR integration consists of the following embedded files:

```bash
roles/macos/alpr_service/
├── files/
│   ├── detect.py              # Python ALPR monitor (integrated from alpr/)
│   ├── requirements.txt       # Python dependencies
│   └── alpr-reference.md      # Original ALPR documentation
├── templates/
│   ├── com.orangead.alpr.plist.j2         # Docker service LaunchAgent
│   ├── com.orangead.alpr-monitor.plist.j2 # Python monitor LaunchAgent
│   └── alpr.env.j2                        # Environment configuration
├── tasks/
│   ├── main.yml              # Original Docker-only deployment
│   └── main-enhanced.yml     # Full stack deployment (Docker + Python)
├── defaults/main.yml         # Configuration variables
└── handlers/main.yml         # Service management handlers
```

## 🚀 Quick Start

### 1. Configure Vault Credentials

Add your PlateRecognizer credentials to the vault:

```bash
ansible-vault edit group_vars/all/vault.yml
```

Add the following:

```yaml
# PlateRecognizer API Credentials
vault_alpr_token: "your-platerecognizer-api-token"
vault_alpr_license_key: "your-platerecognizer-license-key"
```

### 2. Deploy ALPR Stack

Deploy to staging environment:

```bash
# Deploy complete ALPR stack
./scripts/deploy-alpr

# Deploy to specific host
./scripts/deploy-alpr mac-mini-01

# Dry run to test configuration
./scripts/deploy-alpr --dry-run
```

Deploy using component framework:

```bash
# Deploy ALPR as component
./scripts/run-component alpr --staging

# Deploy with universal playbook
ansible-playbook playbooks/universal.yml \
  --extra-vars 'execution_mode=components selected_components=["alpr"]' \
  -i inventory/staging/hosts.yml
```

### 3. Verify Deployment

SSH to target host and check services:

```bash
# Check LaunchAgent services
launchctl list | grep orangead

# Verify Docker container
docker ps | grep orangead_alpr

# Test ALPR API
curl -I http://localhost:8081/v1/plate-reader/
```

## 📁 Directory Structure

After deployment, the following structure is created on the target:

```bash
~/orangead/alpr/
├── detect.py              # Python monitor application
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── detections/            # Captured vehicle images and JSON results
├── logs/                  # Service logs
│   ├── alpr.out.log      # Docker service stdout
│   ├── alpr.err.log      # Docker service stderr
│   ├── monitor.out.log   # Python monitor stdout
│   └── monitor.err.log   # Python monitor stderr
└── config/               # Additional configuration files
```

## 🔧 Configuration

### Environment Variables

The ALPR monitor is configured via `.env` file:

```bash
# Camera configuration
CAMERA_ID=0                    # Camera device ID (0 for built-in)
MAX_IMAGES_PER_CAR=5          # Images captured per vehicle
FRAME_SKIP=5                  # Process every Nth frame
CONFIDENCE_THRESHOLD=0.5      # YOLO detection confidence

# API configuration
ALPR_SERVICE_URL=http://localhost:8081/v1/plate-reader/
ALPR_REGION=ca                # Recognition region
ALPR_COUNTRY=ca               # Country code

# Paths
DETECTIONS_DIR=~/orangead/alpr/detections
```

### Ansible Variables

Customize deployment in inventory or playbook:

```yaml
# ALPR configuration
alpr_camera_id: 0 # Camera device ID
alpr_region: "ca" # Recognition region (ca, us, eu)
alpr_confidence_threshold: 0.5 # YOLO detection threshold
alpr_max_images_per_car: 5 # Images per vehicle detection

# Service configuration
macos_alpr_host_port: 8081 # API port
alpr_python_version: "3.12" # Python version for monitor
```

## 🎛️ Service Management

### LaunchAgent Services

Two services are created:

1. **com.orangead.alpr** - Docker PlateRecognizer service
2. **com.orangead.alpr-monitor** - Python monitor

### Control Commands

```bash
# Start services
launchctl load -w ~/Library/LaunchAgents/com.orangead.alpr.plist
launchctl load -w ~/Library/LaunchAgents/com.orangead.alpr-monitor.plist

# Stop services
launchctl unload ~/Library/LaunchAgents/com.orangead.alpr.plist
launchctl unload ~/Library/LaunchAgents/com.orangead.alpr-monitor.plist

# Check status
launchctl list | grep orangead

# View logs in real-time
tail -f ~/orangead/alpr/logs/monitor.out.log
tail -f ~/orangead/alpr/logs/alpr.out.log
```

### Docker Management

```bash
# Check container status
docker ps --filter "name=orangead_alpr"

# View container logs
docker logs orangead_alpr

# Restart container
docker restart orangead_alpr
```

## 🧪 Testing

### API Test

Test the PlateRecognizer API directly:

```bash
# Basic connectivity test (should return 405 Method Not Allowed)
curl -I http://localhost:8081/v1/plate-reader/

# Full recognition test with image
curl -F "upload=@/path/to/vehicle-image.jpg" \
     -F regions='ca' \
     -F mmc=true \
     -F 'config={"mode":"fast", "detection_mode":"vehicle"}' \
     http://localhost:8081/v1/plate-reader/
```

### Monitor Test

Check real-time detection:

```bash
# Monitor detection logs
tail -f ~/orangead/alpr/logs/monitor.out.log

# Check detection directory
ls -la ~/orangead/alpr/detections/

# View recent detections
find ~/orangead/alpr/detections/ -name "*.json" -mtime -1
```

## 📊 Integration with oaDashboard

The ALPR service integrates with oaDashboard for monitoring:

### Health Endpoints

- **Docker Service**: `http://localhost:8081/v1/plate-reader/` (returns 405 for GET)
- **Monitor Status**: Check LaunchAgent via `launchctl list`

### Metrics Available

- Detection count and frequency
- Processing time per image
- Service uptime and status
- Error rates and failures

### Dashboard Integration

Add ALPR monitoring to oaDashboard backend:

```python
# Check ALPR services status
docker_status = check_docker_container("orangead_alpr")
monitor_status = check_launchctl_service("com.orangead.alpr-monitor")

# Collect metrics
detections_count = count_files("~/orangead/alpr/detections/*.json")
recent_activity = get_recent_detections(hours=24)
```

## 🔍 Troubleshooting

### Common Issues

1. **Docker not starting**

   - Ensure OrbStack is installed and running
   - Check if running in VM (may not support virtualization)
   - Verify Docker daemon: `docker info`

2. **Camera access denied**

   - Grant camera permissions manually in System Preferences
   - Check TCC database permissions
   - Verify Python executable has camera access

3. **API authentication errors**

   - Verify PlateRecognizer credentials in vault
   - Check internet connectivity for license validation
   - Ensure firewall allows outbound HTTPS

4. **Python monitor not starting**
   - Check Python virtual environment exists
   - Verify all dependencies installed
   - Check camera device availability

### Log Analysis

```bash
# Check all ALPR logs
ls -la ~/orangead/alpr/logs/

# Monitor live activity
tail -f ~/orangead/alpr/logs/*.log

# Check Docker logs
docker logs orangead_alpr

# System logs for LaunchAgent
log show --predicate 'subsystem == "com.apple.launchd"' --info --last 1h | grep orangead
```

### Debug Mode

Run monitor manually for debugging:

```bash
cd ~/orangead/alpr
source ~/.pyenv/versions/3.12/envs/alpr/bin/activate
python detect.py
```

## 🚀 Advanced Usage

### Custom Camera Configuration

For multiple cameras or specific devices:

```yaml
# In inventory/host_vars/hostname.yml
alpr_camera_id: 1 # Use second camera
alpr_confidence_threshold: 0.7 # Higher confidence requirement
alpr_max_images_per_car: 10 # More images per detection
```

### Production Deployment

```bash
# Deploy to production with safety checks
./scripts/deploy-alpr --production

# Deploy with custom configuration
./scripts/deploy-alpr --production \
  -e "alpr_camera_id=1,alpr_region=us"
```

### Integration Testing

```bash
# Test component framework
./scripts/run-component alpr --dry-run --verbose

# Verify dependencies
ansible-playbook playbooks/universal.yml \
  --extra-vars 'execution_mode=components selected_components=["alpr"]' \
  --check --diff
```

## 📈 Performance Optimization

### Resource Usage

- Docker container: ~512MB RAM
- Python monitor: ~200MB RAM
- CPU usage varies with camera resolution and frame rate

### Optimization Tips

1. Adjust `FRAME_SKIP` to reduce CPU usage
2. Lower camera resolution if needed
3. Tune `CONFIDENCE_THRESHOLD` for accuracy vs. speed
4. Monitor disk usage in detections directory

## 🔗 Related Components

### Component Dependencies

- **python**: Python runtime environment
- **base-system**: macOS system foundation
- **docker**: Container runtime (OrbStack)

### Compatible Components

- **macos-api**: Can run alongside for system monitoring
- **macos-tracker**: Alternative vision service (can coexist)
- **network-stack**: Provides Tailscale connectivity

## 📞 Support

For issues and support:

1. Check logs in `~/orangead/alpr/logs/`
2. Verify service status with `launchctl list | grep orangead`
3. Test API connectivity with curl commands
4. Review PlateRecognizer account usage and limits
5. Consult oaAnsible documentation for component framework issues

---

**ALPR Integration Status**: ✅ Production Ready

The ALPR integration provides a complete, automated vehicle detection and license plate recognition solution, fully integrated with the oaAnsible orchestration
system and ready for production deployment.
