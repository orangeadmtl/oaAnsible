# OrangePi Embedded Platform Roles

This directory contains Ansible roles for deploying and managing OrangePi 5B devices in the OrangeAd infrastructure.

## Roles

### `orangepi/base`
- Optimizes system for embedded hardware
- Configures GPIO and hardware-specific settings
- Sets up power management and thermal control
- Configures display and video output management

### `orangepi/opi_setup`
- Deploys the opi-setup FastAPI service
- Configures Python virtual environment with required packages
- Sets up systemd service for the API
- Configures health monitoring and screenshot capabilities

### `orangepi/network`
- Installs and configures Tailscale for secure connectivity
- Optimizes network settings for embedded device
- Manages WiFi and Ethernet configurations
- Sets up firewall rules optimized for OrangePi

### `orangepi/optimization`
- Boot time optimization for fast startup
- Memory and CPU tuning for embedded performance
- Storage optimization and wear leveling
- Thermal management and monitoring
- Watchdog configuration for reliability

## Usage

Use the `orangepi-full.yml` playbook to deploy the complete OrangePi stack:

```bash
# Deploy full OrangePi stack
./scripts/run-platform orangepi -i inventory/platforms/orangepi/hosts.yml

# Deploy specific components
./scripts/run-component opi-setup -i inventory/platforms/orangepi/hosts.yml

# Dry run
ansible-playbook playbooks/orangepi-full.yml -i inventory/platforms/orangepi/hosts.yml --check
```

## Prerequisites

1. **Target Device Requirements:**
   - OrangePi 5B with Ubuntu/Debian ARM64
   - SSH access configured
   - User with sudo privileges
   - Stable network connection

2. **Hardware Integration:**
   - Display connected (HDMI/DSI) or headless configuration
   - Storage: microSD card (Class 10+) or eMMC
   - Power: Reliable 5V/4A power supply

3. **Software Dependencies:**
   - Python 3.8+ available on target
   - systemd for service management
   - Network connectivity for package installation

## OrangePi-Specific Considerations

- **ARM64 Architecture**: All software must be ARM64 compatible
- **GPIO Access**: Proper permissions for hardware access
- **Thermal Management**: Active cooling and temperature monitoring
- **Power Efficiency**: Optimized for 24/7 operation
- **Display Output**: Support for both HDMI and headless operation
- **Storage Optimization**: SSD/eMMC optimization for longevity

## Integration with opi-setup Project

This deployment integrates with the existing `opi-setup` project:
- Deploys the FastAPI service from the opi-setup codebase
- Configures the API to provide device health metrics
- Sets up screenshot capture capabilities
- Integrates with oaDashboard for remote monitoring

## Post-Deployment Verification

After deployment, verify:

1. **OPI-Setup Service**: `systemctl status opi-setup`
2. **API Health**: `curl http://localhost:9090/health`
3. **Tailscale**: `sudo tailscale status`
4. **Hardware**: Check GPIO, display, temperature sensors
5. **Network**: Verify connectivity and firewall rules