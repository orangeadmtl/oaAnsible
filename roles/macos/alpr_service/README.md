# macOS ALPR Service Role

This Ansible role deploys Docker Desktop and the PlateRecognizer ALPR (Automatic License Plate Recognition) service on macOS targets.

## Prerequisites

- macOS target system
- Homebrew installed (handled by previous roles)
- Valid PlateRecognizer API token and license key

## Features

- ✅ Docker Desktop installation via Homebrew Cask
- ✅ Docker daemon startup and verification
- ✅ Firewall configuration for Docker and API access
- ✅ PlateRecognizer ALPR Docker image deployment
- ✅ LaunchAgent service configuration
- ✅ Service health monitoring and verification
- ✅ Comprehensive logging and error handling

## Variables

### Required Vault Variables

Add these to your `group_vars/all/vault.yml`:

```yaml
vault_alpr_token: "your-platerecognizer-api-token"
vault_alpr_license_key: "your-platerecognizer-license-key"
```

### Role Variables (defaults/main.yml)

- `alpr_image_name`: Docker image for ALPR service (default: `platerecognizer/alpr`)
- `alpr_container_name`: Container name (default: `orangead_alpr`)
- `alpr_host_port`: Host port mapping (default: `8081`)
- `alpr_container_port`: Container port (default: `8080`)
- `docker_install_timeout`: Timeout for Docker installation (default: `300` seconds)

## Usage

### Enable ALPR Service

Set the environment variable to enable ALPR deployment:

```yaml
oa_environment:
  deploy_alpr_service: true
```

### Run with Tags

```bash
# Deploy only ALPR service
ansible-playbook main.yml --tags "alpr"

# Deploy Docker and ALPR
ansible-playbook main.yml --tags "docker,alpr"
```

## Service Management

### LaunchAgent Control

```bash
# Start service
launchctl load -w ~/Library/LaunchAgents/com.orangead.alpr.plist

# Stop service
launchctl unload ~/Library/LaunchAgents/com.orangead.alpr.plist

# Check status
launchctl list | grep com.orangead.alpr
```

### Docker Container Control

```bash
# Check container status
docker ps | grep orangead_alpr

# View logs
docker logs orangead_alpr

# Manual container run
docker run --name orangead_alpr --rm -p 8081:8080 \
  -v alpr_license_data:/license \
  -e TOKEN=your-token \
  -e LICENSE_KEY=your-license-key \
  platerecognizer/alpr
```

## Testing

### Basic Connectivity Test

```bash
# Should return HTTP 405 (Method Not Allowed) - expected for GET requests
curl -I http://localhost:8081/v1/plate-reader/
```

### ALPR Detection Test

```bash
export IMAGE=~/Downloads/p3.jpg
curl -F "upload=@${IMAGE}" \
     -F regions='ca' \
     -F mmc=true \
     -F 'config={"mode":"fast", "detection_mode":"vehicle"}' \
     http://localhost:8081/v1/plate-reader/
```

Expected response format:

```json
{
  "results": [
    {
      "plate": "ABC123",
      "confidence": 0.95,
      "region": {...},
      "vehicle": {...}
    }
  ]
}
```

## Troubleshooting

### Docker Issues

1. **Docker Desktop not starting**:

   ```bash
   # Manually start Docker Desktop
   open -a Docker

   # Check if daemon is running
   docker info
   ```

2. **Port conflicts**:

   - Default port 8081 to avoid conflict with oaTracker (8080)
   - Check for port usage: `lsof -i :8081`

3. **Container startup failures**:

   ```bash
   # Check container logs
   docker logs orangead_alpr

   # Check LaunchAgent logs
   tail -f ~/orangead/alpr/logs/alpr.err.log
   ```

### API Access Issues

1. **Invalid credentials**:

   - Verify `vault_alpr_token` and `vault_alpr_license_key`
   - Check PlateRecognizer account status

2. **Network connectivity**:
   - Ensure outbound HTTPS access to api.platerecognizer.com
   - Check firewall rules

### Service Management Issues

1. **LaunchAgent not loading**:

   ```bash
   # Check plist syntax
   plutil ~/Library/LaunchAgents/com.orangead.alpr.plist

   # Manual load with verbose output
   launchctl load -w ~/Library/LaunchAgents/com.orangead.alpr.plist
   ```

## Security Considerations

- API token and license key are stored in Ansible Vault
- Service runs as the configured ansible_user
- Firewall rules allow Docker Desktop through macOS Application Firewall
- Container has access to license volume for persistent licensing

## Dependencies

- `community.general.homebrew_cask` collection
- `community.docker.docker_image` collection
- `community.docker.docker_container` collection
- Docker Desktop for Mac
- Valid PlateRecognizer subscription

## Notes

- The ALPR service requires internet connectivity for API calls
- License volume persists between container restarts
- Service logs are stored in `~/orangead/alpr/logs/`
- Container is configured with `--restart=unless-stopped` for reliability
