# Component System Guide

The oaAnsible component system provides intelligent, dependency-aware deployment of individual services and configurations. This guide covers all available
components, their dependencies, and advanced usage patterns.

## Overview

The component system replaces manual service management with an intelligent framework that:

- **Automatically resolves dependencies** - No need to manually track prerequisites
- **Detects conflicts** - Prevents incompatible components from being deployed together
- **Validates compatibility** - Ensures components work on target platforms
- **Provides execution modes** - Dry-run, check, diff, and force modes
- **Tracks resource requirements** - Memory, disk, CPU, and port usage

## Available Components

### macOS Platform Components

#### `macos-api`

**Purpose**: Device monitoring and management API service **Platform**: macOS **Dependencies**: `python`, `base-system` **Resources**: 512MB RAM, 1GB disk, port
9090 **Service**: LaunchAgent running as ansible_user

```bash
# Deploy with automatic dependency resolution
./scripts/run-component staging macos-api

# Will deploy: base-system → python → macos-api
```

**Features**:

- System health monitoring
- Device information reporting
- Camera enumeration
- Service management endpoints
- Integration with oaTracker

#### `macos-tracker`

**Purpose**: AI tracking and analysis system (oaTracker) **Platform**: macOS **Dependencies**: `python`, `base-system`, `macos-api` **Resources**: 2GB RAM, 5GB
disk, port 8080 **Service**: LaunchAgent running as ansible_user

```bash
# Deploy full tracking system
./scripts/run-component staging macos-tracker

# Will deploy: base-system → python → macos-api → macos-tracker
```

**Features**:

- Real-time object detection and tracking
- MJPEG stream output
- Statistics and analytics API
- Camera access with TCC permissions
- AI model management


### Universal Components

#### `base-system`

**Purpose**: Foundation system configuration **Platform**: Universal (all platforms) **Dependencies**: None (foundation component) **Resources**: Minimal
**Category**: Foundation

```bash
# Deploy base system only
./scripts/run-component staging base-system
```

**Features**:

- System package installation
- User and group configuration
- Basic security settings
- File system structure
- Service user setup

#### `python`

**Purpose**: Python runtime environment with package management **Platform**: Universal **Dependencies**: `base-system` **Resources**: 1GB disk for environments
**Category**: Runtime

```bash
# Deploy Python runtime
./scripts/run-component staging python
```

**Features**:

- pyenv installation and configuration
- Multiple Python version support
- uv package manager integration
- Virtual environment management
- Development tools

#### `node`

**Purpose**: Node.js runtime environment **Platform**: Universal **Dependencies**: `base-system` **Resources**: 1GB disk for packages **Category**: Runtime

```bash
# Deploy Node.js runtime
./scripts/run-component staging node
```

**Features**:

- nvm installation and configuration
- Multiple Node.js version support
- npm and yarn package managers
- Global package management

#### `network-stack`

**Purpose**: Network configuration including VPN **Platform**: Universal **Dependencies**: `base-system` **Resources**: Minimal **Category**: Infrastructure

```bash
# Deploy network configuration
./scripts/run-component staging network-stack
```

**Features**:

- Tailscale VPN setup and configuration
- DNS management
- Firewall configuration
- Network interface optimization
- Connectivity testing

### Ubuntu Platform Components

#### `ubuntu-docker`

**Purpose**: Docker environment for containerized applications **Platform**: Ubuntu **Dependencies**: `base-system` **Resources**: 10GB disk for images
**Category**: Runtime

```bash
# Deploy Docker environment
./scripts/run-component staging ubuntu-docker
```

**Features**:

- Docker CE installation
- Docker Compose setup
- Container registry configuration
- Resource management
- Security hardening

### OrangePi Platform Components

#### `opi-player`

**Purpose**: Media player service for embedded displays **Platform**: OrangePi **Dependencies**: `base-system`, `python` **Resources**: 1GB RAM, 2GB disk, port
9090 **Category**: Service

```bash
# Deploy OrangePi media player
./scripts/run-component staging opi-player
```

**Features**:

- Media playback capabilities
- Display management
- GPIO integration
- Hardware optimization
- opi-setup integration

## Dependency Resolution

### How It Works

The component framework automatically resolves dependencies using a recursive algorithm:

1. **Parse Request**: Analyze requested components
2. **Resolve Dependencies**: Recursively resolve all requirements
3. **Detect Conflicts**: Check for incompatible combinations
4. **Validate Compatibility**: Ensure platform and resource compatibility
5. **Order Execution**: Sort by priority and dependency order

### Example Resolution

```bash
# Request: macos-tracker
./scripts/run-component staging macos-tracker

# Automatic Resolution:
# 1. base-system (priority: 200, foundation)
# 2. python (priority: 180, required by macos-tracker)
# 3. macos-api (priority: 100, required by macos-tracker)
# 4. macos-tracker (priority: 90, requested component)
```

### Dependency Chain Visualization

```bash
macos-tracker
├── macos-api
│   ├── python
│   │   └── base-system
│   └── base-system
├── python
│   └── base-system
└── base-system

Resolved Order: base-system → python → macos-api → macos-tracker
```

## Conflict Detection

### How Conflicts Work

Components can declare conflicts with other components:


### Conflict Examples

```bash
# Example of platform conflict:
./scripts/run-component staging ubuntu-docker macos-api
# ❌ Platform ubuntu not supported by component macos-api
```

## Compatibility Validation

### Platform Compatibility

```yaml
platform_requirements:
  macos:
    minimum_version: "12.0"
    required_features: ["homebrew", "launchd"]
  ubuntu:
    minimum_version: "20.04"
    required_features: ["systemd", "apt"]
```

### Resource Requirements

```yaml
resource_requirements:
  macos-tracker:
    min_memory_mb: 2048
    min_disk_mb: 5120
    cpu_cores: 2
    network_ports: [8080]
    requires_camera: true
```

### Version Compatibility

```yaml
version_compatibility:
  python:
    "3.11": ["macos-api", "macos-tracker"]
    "3.12": ["macos-api", "macos-tracker"]
    "3.13": ["macos-api"] # Limited compatibility
```

## Advanced Usage

### Component Selection Patterns

```bash
# Single component with dependencies
./scripts/run-component staging macos-api

# Multiple compatible components
./scripts/run-component staging macos-api network-stack python

# Platform-specific deployment
./scripts/run-component staging base-system python node  # Universal components

# Environment-specific with execution mode
./scripts/run-component production macos-tracker --force
```

### Execution Modes

#### Dry-Run Mode

Preview what would be deployed:

```bash
./scripts/run-component staging macos-tracker --dry-run

# Output:
# 📋 EXECUTION PLAN
# Components: 4
# Estimated Duration: 12min
#
# 1. BASE-SYSTEM (deploy)
#    Duration: 2-5min
#    Changes:
#    - Create/update application files
#    - Configure virtual environment
#
# 2. PYTHON (deploy)
#    Duration: 2-5min
# ...
```

#### Check Mode

Validate configuration without changes:

```bash
./scripts/run-component staging macos-api --check --verbose

# Output:
# ✅ CHECK MODE COMPLETE
# Configuration validation passed.
# Review the potential changes above and run in normal mode to apply.
```

#### Force Mode

Skip safety checks and confirmations:

```bash
./scripts/run-component production macos-api --force

# Skips:
# - User confirmation prompts
# - Disk space validation
# - Network connectivity checks
# - Configuration backups
```

### Resource Analysis

```bash
# Get resource requirements for deployment
./scripts/run-component staging macos-tracker --dry-run

# Output:
# Resource Requirements:
# - Memory: 3072MB (base + python + api + tracker)
# - Disk: 7680MB
# - CPU Cores: 2
# - Network Ports: 9090, 8080
```

## Component Development

### Adding New Components

1. **Define Component** in `tasks/component-framework.yml`:

```yaml
your-component:
  platform: "macos"
  requires: ["python", "base-system"]
  conflicts: []
  provides: ["your-service"]
  health_port: 8082
  health_endpoint: "/health"
  category: "service"
  priority: 85
```

1. **Add Resource Requirements** in `tasks/component-compatibility.yml`:

```yaml
resource_requirements:
  your-component:
    min_memory_mb: 1024
    min_disk_mb: 2048
    cpu_cores: 1
    network_ports: [8082]
```

1. **Create Deployment Logic** in `tasks/deploy-components.yml`:

```yaml
- name: Deploy your-component
  ansible.builtin.include_role:
    name: your-component-role
  when: "'your-component' in components_to_deploy"
```

### Testing New Components

```bash
# Test with dry-run
./scripts/run-component staging your-component --dry-run

# Validate dependencies
./scripts/run-component staging your-component --check

# Test conflicts
./scripts/run-component staging your-component conflicting-component --dry-run
```

## Best Practices

### Component Selection

1. **Start Small**: Begin with base components and add services incrementally
2. **Use Dry-Run**: Always test with `--dry-run` before production deployment
3. **Check Compatibility**: Verify platform and resource requirements
4. **Monitor Resources**: Ensure sufficient system resources are available

### Deployment Strategies

1. **Staged Deployment**: Deploy foundation components first, then services
2. **Environment Progression**: Test in staging before production
3. **Rollback Planning**: Use backup creation and configuration tracking
4. **Health Monitoring**: Verify service health after deployment

### Performance Optimization

1. **Component Grouping**: Deploy related components together
2. **Resource Monitoring**: Track memory, disk, and CPU usage
3. **Concurrent Deployment**: Use server API for parallel deployments
4. **State Detection**: Leverage intelligent state management for efficiency

## Troubleshooting

### Common Issues

#### Component Not Found

```bash
./scripts/run-component staging invalid-component
# ❌ Component validation failed:
# Invalid components: invalid-component
# Available components: macos-api, macos-tracker, base-system, python, node, network-stack, ubuntu-docker, opi-player
```

#### Platform Mismatch

```bash
./scripts/run-component staging ubuntu-docker  # On macOS
# ❌ Platform conflicts: 1 found
# - ubuntu-docker: requires ubuntu, current: macos
```

#### Resource Constraints

```bash
./scripts/run-component staging macos-tracker  # Low disk space
# ❌ Insufficient disk space!
# Available: 2GB
# Required: 5GB minimum
```

#### Conflict Detection


### Debug Techniques

```bash
# Verbose output
./scripts/run-component staging macos-api --verbose

# Check mode for validation
./scripts/run-component staging macos-api --check

# Dry-run with resource analysis
./scripts/run-component staging macos-tracker --dry-run

# Force mode for testing (staging only)
./scripts/run-component staging macos-api --force
```

---

**Component System** - Intelligent dependency resolution for oaAnsible  
Part of the Advanced Multi-Platform Orchestration System
