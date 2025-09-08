# oaAnsible Roles Reference

Consolidated reference for all Ansible roles in the oaPangaea project.

## 🏗️ Platform Organization

### Common Roles (`roles/common/`)
Shared components that work across all platforms:

- **`device_api`** - Unified device API deployment (replaces platform-specific APIs)
- **`ml_workstation`** - ML development environment setup
- **`monitoring`** - System monitoring and health checks
- **`package_manager`** - Package management abstraction
- **`service_manager`** - Service lifecycle management
- **`shell_manager`** - Shell configuration and optimization
- **`uv_python`** - Modern Python environment with uv package manager

### macOS Roles (`roles/macos/`)
macOS-specific components and services:

**Base System:**
- **`base`** - Core system configuration, display, audio, kiosk mode
- **`common`** - Shared macOS utilities and directory management
- **`network`** - Network configuration including WiFi and Tailscale
- **`node`** - Node.js environment setup
- **`python`** - Python environment configuration
- **`security`** - Camera permissions and automation access
- **`server_optimizations`** - Performance tuning for headless operation
- **`ssh`** - SSH configuration and key management

**Applications & Services:**
- **`alpr_service`** - License plate recognition system
- **`camguard`** - Camera monitoring and MediaMTX streaming
- **`cursorcerer`** - Cursor visibility management
- **`mediamtx_demo`** - MediaMTX streaming demonstration
- **`parking_monitor`** - Specialized parking detection service
- **`player`** - Video player service
- **`staging_video_feed`** - Video feed management for staging environments
- **`tracker`** - AI object tracking runtime

### Ubuntu Roles (`roles/ubuntu/`)
Ubuntu server and ML workstation components:

**Base System:**
- **`base`** - Core Ubuntu system setup
- **`docker`** - Docker containerization platform
- **`monitoring`** - System health monitoring
- **`network/tailscale`** - Tailscale VPN setup
- **`python`** - Python development environment
- **`security`** - Security hardening and access control
- **`shell`** - Shell configuration (zsh, fish)
- **`storage_server`** - Storage management for data servers

**Specialized:**
- **`ml_workstation`** - GPU-enabled ML training environment
- **`nvidia`** - NVIDIA GPU drivers and CUDA setup
- **`server_optimization`** - Performance tuning including ethernet optimization

### OrangePi Roles (`roles/orangepi/`)
OrangePi-specific configuration:

- **`base`** - Base system configuration
- **`network/tailscale`** - Tailscale setup for OrangePi
- **`shell`** - Shell configuration for embedded systems

## 🎯 Component Tags

Use these tags with `universal.yml` for targeted deployments:

| Tag | Description | Roles Included |
|-----|-------------|----------------|
| `base` | Core system setup | Platform base roles |
| `network` | Network configuration | Tailscale, WiFi setup |
| `security` | Security hardening | Permissions, access control |
| `device-api` | Device API deployment | Unified device API |
| `tracker` | AI tracking system | Object tracking runtime |
| `player` | Video player | Media playback service |
| `camguard` | Camera monitoring | MediaMTX streaming |
| `parking-monitor` | Parking detection | Vehicle detection service |
| `ml-workstation` | ML development | GPU, training environment |
| `optimization` | Performance tuning | Server optimizations |

## 🚀 Deployment Examples

### Full Platform Deployment
```bash
# Deploy all components for macOS device
ansible-playbook universal.yml -i inventory/production.yml

# Deploy specific components
ansible-playbook universal.yml -i inventory/staging.yml -t device-api,tracker
```

### ML Workstation Setup
```bash
# Ubuntu ML workstation
ansible-playbook universal.yml -i inventory/ml-servers.yml -t ml-workstation

# macOS ML development
ansible-playbook onboard-ml-macos.yml -i inventory/dev-macs.yml
```

### Platform-Specific Playbooks
```bash
# Platform-specific onboarding
ansible-playbook macos-onboarding.yml -i inventory/new-macs.yml
ansible-playbook ubuntu-onboarding.yml -i inventory/new-servers.yml
ansible-playbook orangepi-onboarding.yml -i inventory/new-pis.yml
```

## 📝 Role Development Guidelines

### Common Patterns
- Use `defaults/main.yml` for role variables
- Implement handlers for service management
- Use templates for configuration files
- Follow idempotency principles

### Dependencies
- Platform detection is automatic in `universal.yml`
- Use `meta/main.yml` for role dependencies
- Common roles can be used by platform-specific roles

### Testing
- Test roles with `ansible-playbook --check` (dry run)
- Use `ansible-playbook --diff` to see changes
- Test on staging environment before production

For specific role configuration and advanced usage, see the individual role directories.