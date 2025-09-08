# oaAnsible Complete Architecture Guide

## Table of Contents
1. [Overview and Purpose](#overview-and-purpose)
2. [Architecture and Design](#architecture-and-design)
3. [Directory Structure](#directory-structure)
4. [Inventory System](#inventory-system)
5. [Component Framework](#component-framework)
6. [Roles and Their Functions](#roles-and-their-functions)
7. [Playbook System](#playbook-system)
8. [Deployment Workflow](#deployment-workflow)
9. [Integration with oaDashboard](#integration-with-oadashboard)
10. [Scripts and Tools](#scripts-and-tools)
11. [Configuration Management](#configuration-management)
12. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview and Purpose

### What is oaAnsible?

oaAnsible is the **Infrastructure as Code (IaC) automation system** for OrangeAd's device fleet management. It handles automated deployment, configuration, and management of services across macOS (Mac Mini) and OrangePi devices in the OrangeAd ecosystem.

### Core Purposes

1. **Automated Device Onboarding**: Sets up new Mac Minis and OrangePi devices from scratch
2. **Service Deployment**: Deploys and manages OrangeAd services (Device API, Tracker, Parking Monitor, Player, CamGuard)
3. **Configuration Management**: Ensures consistent configuration across all devices
4. **Platform Abstraction**: Handles platform-specific differences between macOS and Linux
5. **Environment Management**: Manages staging, preprod, and production environments

### Key Design Principles

- **Idempotency**: All operations can be run multiple times safely
- **Component-Based**: Modular architecture with reusable components
- **Platform-Aware**: Intelligent detection and handling of different platforms
- **Web-First**: Primary interface through oaDashboard (CLI deprecated)
- **Git-Driven**: All services deployed from Git repositories
- **Environment-Specific**: Different configurations for staging/preprod/production

---

## Architecture and Design

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│          oaDashboard Web Interface          │
│    (Primary deployment interface)           │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│           Ansible Service API               │
│    (WebSocket logs, job management)         │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│         Universal Playbook Router           │
│    (Platform detection, component routing)   │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│          Component Framework                │
│    (Registry, dependencies, configs)        │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│              Role System                    │
│    (Platform-specific implementations)      │
└─────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Request** → oaDashboard UI
2. **API Processing** → Ansible Service validates and queues
3. **Job Execution** → Universal playbook routes to components
4. **Component Resolution** → Registry determines what to deploy
5. **Role Execution** → Platform-specific roles handle deployment
6. **Service Management** → LaunchAgents (macOS) / systemd (Linux)
7. **Validation** → Health checks and API verification
8. **Reporting** → Real-time logs via WebSocket

---

## Directory Structure

### Root Level Organization

```
oaAnsible/
├── ansible.cfg              # Main Ansible configuration
├── requirements.yml         # External role/collection dependencies
├── main.yml                # Primary entry point playbook
│
├── inventory/              # Hierarchical inventory system
│   ├── 00_foundation/     # Base configurations
│   ├── 10_components/     # Component definitions
│   ├── 20_environments/   # Environment configs
│   ├── 30_projects/       # Project-specific settings
│   └── group_vars/        # Variable hierarchies
│
├── playbooks/             # All playbooks
│   ├── universal.yml      # Main routing playbook
│   ├── ubuntu-onboarding.yml
│   ├── orangepi-onboarding.yml
│   └── onboard-ml-*.yml   # ML workstation setup
│
├── roles/                 # Role definitions
│   ├── common/           # Cross-platform roles
│   ├── macos/            # macOS-specific roles
│   ├── ubuntu/           # Ubuntu-specific roles
│   └── orangepi/         # OrangePi-specific roles
│
├── scripts/              # Utility scripts (deprecated CLI)
│   ├── run              # Main deployment script
│   ├── check            # Health check script
│   ├── format           # YAML formatter
│   └── helpers.sh       # Shared functions
│
├── templates/           # Jinja2 templates
├── server/              # oaDashboard integration
└── docs/                # Documentation
```

### Key Directory Purposes

- **inventory/**: Layered configuration system (foundation → components → environments → projects)
- **roles/**: Actual implementation code for deployments
- **playbooks/**: Entry points and workflow orchestration
- **scripts/**: Legacy CLI tools (emergency use only)
- **server/**: Integration with oaDashboard backend

---

## Inventory System

### Layered Inventory Architecture

The inventory system uses a **hierarchical layering approach**:

```
00_foundation/    # Base layer - fundamental settings
     ↓
10_components/    # Component registry and definitions
     ↓
20_environments/  # Environment-specific configs
     ↓
30_projects/      # Project-specific customizations
```

### Foundation Layer (00_foundation/)

**Purpose**: Defines base configurations that apply to ALL deployments

- `defaults.yml`: Default component stack, deployment settings
- `base_setup.yml`: System foundation configurations
- `network.yml`: Network settings (Tailscale, SSH)
- `security.yml`: Security hardening requirements

### Component Layer (10_components/)

**Purpose**: Central registry of all deployable components

Key file: `_registry.yml` - Defines all components with:
- Service metadata (name, description, ports)
- Repository information (URL, branch, destination)
- Dependencies and platform compatibility
- LaunchAgent/systemd service names

Components defined:
- `device-api`: Unified device management API (mandatory)
- `parking-monitor`: AI parking detection
- `player`: Video player for displays
- `tracker`: Human detection AI
- `camguard`: Camera monitoring
- `alpr`: License plate recognition

### Environment Layer (20_environments/)

**Purpose**: Environment-specific overrides

Files:
- `staging.yml`: Development/testing settings
- `preprod.yml`: Pre-production validation
- `production.yml`: Production configurations

Each defines:
- Log levels
- Debug settings
- Performance tuning
- Environment-specific features

### Project Layer (30_projects/)

**Purpose**: Project-specific customizations

Example: `yhu/` (YUH Airport parking project)
- `project.yml`: Project metadata
- `stack.yml`: Component selection and configs
- `hosts/*.yml`: Host definitions per environment

---

## Component Framework

### Component Definition Structure

Each component in `_registry.yml` contains:

```yaml
component-name:
  name: "Human-readable name"
  description: "What it does"
  mandatory: true/false
  service:
    name: "service.identifier"
    port: 9090
    bind_address: "127.0.0.1"
  repository:
    url: "https://github.com/..."
    branch: "main"
    destination: "~/orangead/service"
  platforms: ["macos", "orangepi"]
  dependencies: ["base", "network"]
  role: "path/to/ansible/role"
  tags: ["tag1", "tag2"]
```

### Component Dependencies

Components have explicit dependencies:
- **device-api**: Requires `base`, `network`, `security`
- **parking-monitor**: Requires `device-api`
- **player**: Requires `device-api`
- **tracker**: Requires `device-api`

Dependencies are automatically resolved during deployment.

### Component Selection Logic

1. **Mandatory Components**: Always deployed (e.g., device-api)
2. **Tag-Based Selection**: Using `-t tag1,tag2`
3. **Project Stack**: Defined in project's `stack.yml`
4. **Environment Overrides**: Per-environment modifications
5. **Host-Specific**: Individual host customizations

---

## Roles and Their Functions

### Common Roles (Cross-Platform)

Located in `roles/common/`:

#### device_api
- **Purpose**: Deploy unified Device API service
- **Features**: Platform detection, automatic router loading
- **Tasks**: Repository setup, Python environment, service installation

#### uv_python
- **Purpose**: Modern Python management using `uv` tool
- **Features**: Fast virtual environment creation, dependency installation
- **Replaces**: Traditional pip/venv approach

#### package_manager
- **Purpose**: Cross-platform package installation
- **Handles**: Homebrew (macOS), apt (Ubuntu), platform detection

#### service_manager
- **Purpose**: Abstract service management
- **Handles**: LaunchAgents (macOS), systemd (Linux)

### macOS-Specific Roles

Located in `roles/macos/`:

#### parking_monitor
- **Purpose**: Deploy parking detection service
- **Key Tasks**:
  - Repository cloning/updating
  - Python environment setup with uv
  - Configuration from templates
  - LaunchAgent installation
  - Health verification

#### player
- **Purpose**: Video player for digital signage
- **Features**: MPV-based, dual-screen support
- **Configuration**: Playlist management, display settings

#### tracker
- **Purpose**: Human detection AI service
- **Features**: YOLOv11 model loading, MJPEG streaming
- **Integration**: Works with models from oaSentinel

#### camguard
- **Purpose**: Camera monitoring and alerts
- **Features**: Motion detection, alert system

### Platform Management Roles

#### macos/base
- System setup, Xcode tools, Homebrew
- User permissions, directory structure

#### macos/network
- Tailscale VPN setup
- SSH configuration
- Network optimization

#### macos/security
- SSH key management
- Firewall configuration
- Service hardening

---

## Playbook System

### Main Entry Points

#### main.yml
- Primary entry point
- Routes to `universal.yml`
- Passes through all variables and tags

#### universal.yml
- **Core routing logic**
- Platform detection
- Component resolution
- Tag processing
- Execution orchestration

Key features:
- Detects platform (macOS/Ubuntu/OrangePi)
- Processes component tags
- Resolves dependencies
- Routes to appropriate roles
- Handles execution modes

### Specialized Playbooks

#### ubuntu-onboarding.yml
- Ubuntu server initial setup
- ML workstation preparation
- Development environment

#### orangepi-onboarding.yml
- OrangePi device setup
- Display configuration
- Kiosk mode setup

#### onboard-ml-*.yml
- ML development setup
- CUDA/GPU configuration
- oaSentinel environment

---

## Deployment Workflow

### Standard Deployment Process

1. **Request Initiation**
   - User selects components in oaDashboard
   - Or emergency CLI: `./scripts/run inventory -t component`

2. **Validation Phase**
   - Inventory resolution
   - Component dependency checking
   - Platform compatibility verification

3. **Pre-Deployment**
   - SSH connectivity test
   - Disk space verification
   - Service status check

4. **Repository Management**
   ```yaml
   - Clone or update repository
   - Force update with --force flag
   - Verify correct branch
   - Clean working directory
   ```

5. **Environment Setup**
   ```yaml
   - Create/update Python virtual environment (using uv)
   - Install dependencies
   - Verify imports
   ```

6. **Configuration Deployment**
   ```yaml
   - Generate configs from templates
   - Set environment variables
   - Update service definitions
   ```

7. **Service Management**
   ```yaml
   - Stop existing service
   - Install LaunchAgent/systemd unit
   - Start new service
   - Verify process running
   ```

8. **Validation**
   ```yaml
   - Test API endpoints
   - Check service logs
   - Verify health status
   ```

### Force Update Mode

When using `--force` flag:
- All git repositories force-pulled
- Services fully restarted
- Caches cleared
- Complete redeployment

---

## Integration with oaDashboard

### Web Interface (Primary)

oaDashboard provides:
- **Deployment UI**: Component selection, host targeting
- **Real-time Logs**: WebSocket streaming of deployment output
- **Job Management**: Queue, status, cancellation
- **Templates**: Pre-configured deployment scenarios
- **RBAC**: Role-based access control
- **Approval Workflows**: Multi-stage deployment approval

### Backend Integration

Located in `oaDashboard/backend/app/routers/ansible.py`:

Key endpoints:
- `POST /api/ansible/deploy`: Initiate deployment
- `GET /api/ansible/jobs`: List deployment jobs
- `GET /api/ansible/jobs/{id}/logs`: Get job logs
- `WS /api/ansible/jobs/{id}/stream`: Real-time log streaming
- `GET /api/ansible/components`: List available components
- `GET /api/ansible/environments`: List environments

### Ansible Service

The backend service:
1. Validates deployment requests
2. Queues Ansible jobs
3. Executes playbooks
4. Streams output via WebSocket
5. Manages job lifecycle

---

## Scripts and Tools

### Legacy CLI Scripts (Deprecated)

Located in `scripts/`:

#### run
- Main deployment script
- Now shows deprecation warning
- Emergency use only
- Wraps ansible-playbook execution

#### check
- Health verification
- Tests deployed services
- Validates configurations

#### format
- YAML formatting
- Ensures consistent style
- Pre-commit hook integration

#### helpers.sh
- Shared bash functions
- Environment detection
- Dependency checking

### Migration from CLI to Web

**Old way** (deprecated):
```bash
./scripts/run yhu/staging -t parking-monitor
```

**New way** (recommended):
```
1. Open http://localhost:3000/deployments
2. Select environment: staging
3. Select project: yhu
4. Choose components: parking-monitor
5. Click Deploy
6. Watch real-time logs
```

---

## Configuration Management

### Configuration Hierarchy

1. **Default Values**: `inventory/group_vars/all/`
2. **Platform Overrides**: `inventory/group_vars/platforms/`
3. **Environment Settings**: `inventory/group_vars/environments/`
4. **Project Configs**: `inventory/30_projects/{project}/`
5. **Host-Specific**: Individual host variables

### Key Configuration Files

#### ansible.cfg
- Hash behavior: merge (enables variable merging)
- Parallel execution: forks=10
- Logging: ./ansible.log
- Vault: ./vault_password_file

#### requirements.yml
- External dependencies
- Collections: geerlingguy.mac, community.general
- Roles: elliotweiser.osx-command-line-tools

### Service Configuration

Each service has:
- **Repository config**: Branch, URL, destination
- **Service config**: Port, bind address, name
- **Environment config**: Log level, debug settings
- **Runtime config**: Python version, dependencies

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Repository Update Failures

**Symptoms**: Old code after deployment

**Solution**:
```bash
# Use force update
./scripts/run inventory -t component --force

# Or manually:
ssh user@host "cd ~/orangead/service && git fetch --all && git reset --hard origin/main"
```

#### 2. Service Won't Start

**Symptoms**: Service not running after deployment

**Check**:
```bash
# macOS
launchctl list | grep servicename
tail -f ~/Library/Logs/servicename.log

# Linux
systemctl status servicename
journalctl -u servicename -f
```

**Solution**:
- Check logs for import errors
- Verify Python environment
- Check port conflicts

#### 3. Python Import Errors

**Symptoms**: Module not found errors

**Solution**:
```bash
# Recreate virtual environment
cd ~/orangead/service
rm -rf .venv
uv venv
uv pip install -r requirements.txt
```

#### 4. Deployment Validation Fails

**Symptoms**: Health check fails after deployment

**Check**:
```bash
curl http://localhost:9090/health
curl http://localhost:9090/
```

**Solution**:
- Increase validation timeout
- Check service actually started
- Verify network configuration

### Performance Optimization

#### Deployment Speed
- Use `uv` instead of pip (10x faster)
- Enable parallel execution
- Cache Python packages locally
- Use --limit to target specific hosts

#### Resource Usage
- Monitor memory during deployment
- Check disk space before deployment
- Limit concurrent deployments

### Monitoring Commands

#### Service Status
```bash
# All services
launchctl list | grep orangead

# Specific service
launchctl list | grep deviceapi
ps aux | grep deviceapi
```

#### Logs
```bash
# Service logs
tail -f ~/orangead/oaDeviceAPI/logs/deviceapi.log

# Ansible logs
tail -f oaAnsible/ansible.log
```

#### Repository Status
```bash
cd ~/orangead/oaDeviceAPI
git status
git log -1 --oneline
git branch -v
```

---

## Best Practices

### Deployment Guidelines

1. **Always use oaDashboard UI** for deployments (not CLI)
2. **Test in staging first** before production
3. **Use force update sparingly** - only when necessary
4. **Monitor logs during deployment** via WebSocket
5. **Verify health after deployment** through API endpoints

### Development Workflow

1. **Create feature branch** in service repository
2. **Update stack.yml** if adding components
3. **Test locally** with manual deployment
4. **Deploy to staging** via oaDashboard
5. **Validate thoroughly** before production

### Maintenance

1. **Regular updates**: Keep repositories current
2. **Log rotation**: Prevent disk fill
3. **Health monitoring**: Regular health checks
4. **Backup configurations**: Before major changes
5. **Document changes**: Update this guide

---

## Conclusion

oaAnsible is a comprehensive infrastructure automation system that manages the entire lifecycle of OrangeAd's device fleet. Its layered architecture, component-based design, and web-first approach make it scalable and maintainable. The integration with oaDashboard provides a modern deployment experience with real-time feedback and comprehensive management capabilities.

For emergency situations where the web interface is unavailable, the CLI scripts remain functional but should be used with caution. Always prefer the web interface for standard operations to benefit from its validation, logging, and management features.

This architecture supports the deployment of various AI services (parking detection, human tracking), media players, and device management APIs across a heterogeneous fleet of macOS and Linux devices, with environment-specific configurations and robust error handling.