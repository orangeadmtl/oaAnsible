# oaAnsible - Advanced Multi-Platform Orchestration System

A production-ready, server-integrated Ansible orchestration system for OrangeAd devices. Part of the `oaPangaea` monorepo, providing comprehensive device
management across macOS and Ubuntu platforms with advanced automation capabilities.

## 🚀 Overview

oaAnsible has evolved into a sophisticated orchestration system that combines traditional Ansible automation with modern server-side execution, intelligent
component frameworks, and seamless integration capabilities.

### Key Features

- **🌐 Multi-Platform Support**: macOS and Ubuntu devices
- **🧠 Intelligent Component Framework**: Automatic dependency resolution and conflict detection
- **🔄 Advanced Execution Modes**: Dry-run, check, diff, and force modes with safety checks
- **⚡ Server Integration**: REST API for remote execution and job management
- **📊 Real-time Monitoring**: Job tracking, health checking, and status reporting
- **🔒 Secure Authentication**: JWT-based auth with oaDashboard integration
- **🔧 Comprehensive Tooling**: Enhanced scripts and client libraries

## 🏗️ Architecture

### Phase 1-4 Implementation Complete

**✅ Multi-Platform Foundation** - Universal playbook routing and platform detection  
**✅ Efficiency & Idempotency** - Smart state management and performance optimization  
**✅ Advanced Component Framework** - Dependency resolution and compatibility validation  
**✅ Server Integration** - REST API with job management and authentication

### System Components

```bash
oaAnsible/
├── 📁 playbooks/           # Platform-agnostic and component-specific playbooks
│   ├── universal.yml       # Main entry point with intelligent routing
│   ├── platform-detection.yml # Automatic OS and capability detection
│   └── components/         # Individual component playbooks
├── 📁 tasks/               # Advanced framework tasks
│   ├── component-framework.yml      # Dependency resolution engine
│   ├── component-compatibility.yml  # Compatibility validation matrix
│   ├── execution-modes.yml         # Advanced execution capabilities
│   └── state-detection.yml        # Comprehensive system state analysis
├── 📁 server/              # Server-side execution framework
│   ├── api/               # FastAPI REST endpoints
│   ├── jobs/              # Job queuing and tracking
│   ├── auth/              # Authentication and authorization
│   ├── utils/             # Ansible execution engine
│   ├── config/            # Configuration management
│   └── client/            # Python client library
├── 📁 scripts/            # Enhanced execution scripts
│   ├── run-component      # Component-specific deployment
│   ├── run-server         # Server launcher
│   ├── demo-framework     # Framework demonstration
│   └── demo-server        # Server API demonstration
├── 📁 roles/              # Platform and service-specific roles
├── 📁 inventory/          # Environment-specific configurations
└── 📁 docs/               # Comprehensive documentation
    ├── SCRIPT_USAGE.md      # Complete script usage guide
    ├── QUICK_REFERENCE.md   # Quick command reference
    ├── WIFI_SETUP.md        # WiFi configuration guide
    └── ...
```

## 🚀 Quick Start

> **📖 For comprehensive script usage examples covering all platforms and use cases, see [SCRIPT_USAGE.md](docs/SCRIPT_USAGE.md)**

### Essential Commands

```bash
# Deploy full stack to staging
./scripts/run-staging -l hostname

# Deploy specific components
./scripts/run-component staging macos-api tracker -l hostname

# Deploy to all production devices
./scripts/run-prod

# Check what would be deployed (dry run)
./scripts/run-staging -l hostname --check
```

### 1. Component Deployment (Recommended)

Deploy specific components with automatic dependency resolution:

```bash
# Deploy macOS API with dependencies (base-system → python → macos-api)
./scripts/run-component staging macos-api

# Deploy tracking system with full dependency chain
./scripts/run-component staging macos-tracker

# Deploy video player for digital signage
./scripts/run-component staging player

# Dry-run mode to preview changes
./scripts/run-component staging macos-api --dry-run

# Multiple components with conflict detection
./scripts/run-component staging macos-api network-stack --check

# Deploy Spectra project stack (API + Tracker + Player)
./scripts/run-component staging macos-api macos-tracker player
```

### 2. Server-Side Execution

Start the server for remote execution via oaDashboard:

```bash
# Start development server
./scripts/run-server --dev

# Production server with custom settings
OAANSIBLE_API_PORT=8001 ./scripts/run-server
```

### 3. Traditional Full Deployment

```bash
# Universal playbook with platform auto-detection
ansible-playbook playbooks/universal.yml -i inventory/staging/hosts.yml

# Platform-specific full deployment
ansible-playbook playbooks/universal.yml -i inventory/production/hosts.yml \
  --extra-vars "execution_mode=full"
```

## 📦 Component System

### Available Components

**macOS Platform:**

- `macos-api` - Device monitoring and management API
- `macos-tracker` - AI tracking and analysis system
- `player` - Flexible video player for digital signage and content display
- `alpr` - License plate recognition (conflicts with tracker)

**Universal Components:**

- `base-system` - Foundation system configuration
- `python` - Python runtime with pyenv management
- `node` - Node.js runtime with nvm management
- `network-stack` - Tailscale VPN and network configuration

**Ubuntu Platform:**

- `ubuntu-docker` - Docker environment setup

### Intelligent Features

**Dependency Resolution:**

```bash
# Requesting 'macos-tracker' automatically resolves and deploys:
# 1. base-system (foundation)
# 2. python (runtime requirement)
# 3. macos-api (service dependency)
# 4. macos-tracker (requested component)
./scripts/run-component staging macos-tracker
```

**Conflict Detection:**

```bash
# This will fail with clear error - camera access conflict
./scripts/run-component staging macos-tracker alpr
```

**Compatibility Validation:**

```bash
# This will fail - platform mismatch
./scripts/run-component staging ubuntu-docker macos-api
```

## 🖥️ Server API

### REST Endpoints

**Authentication Required:**

- `POST /api/deploy/components` - Deploy selected components
- `GET /api/jobs` - List deployment jobs with pagination
- `GET /api/jobs/{job_id}` - Get job details and status
- `GET /api/jobs/{job_id}/logs` - Stream job execution logs
- `DELETE /api/jobs/{job_id}` - Cancel running job

**Public Endpoints:**

- `GET /api/health` - Server health and component status
- `GET /api/environments` - Available deployment environments
- `GET /api/components` - Component definitions and requirements
- `GET /api/docs` - Interactive API documentation

### Client Library Usage

```python
from server.client import create_client

# Async client
async with create_client("http://localhost:8001", token) as client:
    # Deploy components
    job = await client.deploy_components("staging", ["macos-api"])

    # Monitor progress
    async for log_entry in client.stream_job_logs(job["job_id"]):
        print(f"[{job['job_id']}] {log_entry}")

    # Wait for completion
    result = await client.wait_for_job(job["job_id"])
    print(f"Deployment {'✅ succeeded' if result['status'] == 'completed' else '❌ failed'}")

# Sync client for simple operations
from server.client import create_sync_client
client = create_sync_client("http://localhost:8001", token)
health = client.health_check()
```

## 🔧 Advanced Execution Modes

### Dry-Run Mode

Preview changes without execution:

```bash
./scripts/run-component staging macos-api --dry-run
```

### Check Mode

Validate configuration and show potential changes:

```bash
./scripts/run-component staging macos-tracker --check --verbose
```

### Force Mode

Skip safety checks and confirmations:

```bash
./scripts/run-component production macos-api --force
```

### Diff Mode

Show detailed differences for all changes:

```bash
./scripts/run-component staging network-stack --diff
```

## 🌐 Multi-Platform Support

### macOS (Production Ready)

- **Services**: macOS API, oaTracker, ALPR
- **Runtimes**: Python (pyenv), Node.js (nvm)
- **Network**: Tailscale VPN with DNS management
- **Security**: TCC permissions, firewall configuration
- **Management**: LaunchAgent services, automatic startup

### Ubuntu (Server Focus)

- **Services**: Docker environment, system monitoring
- **Runtimes**: Python, Node.js, system packages
- **Network**: Tailscale, firewall (ufw)
- **Management**: SystemD services

## 📊 Monitoring & Observability

### Job Management

- **Real-time Status**: Track deployment progress and logs
- **Job Queuing**: Handle multiple concurrent deployments
- **History Tracking**: Complete audit trail of all deployments
- **Performance Metrics**: Execution times and resource usage

### Health Monitoring

- **Component Health**: Service status and endpoint availability
- **System State**: Resource usage and platform capabilities
- **Network Status**: Connectivity and Tailscale integration
- **Security Status**: TCC permissions and firewall configuration

### Logging & Debugging

```bash
# Enhanced logging with job tracking
OAANSIBLE_LOG_LEVEL=DEBUG ./scripts/run-server

# Component deployment with verbose output
./scripts/run-component staging macos-api --verbose

# Server logs for troubleshooting
tail -f /tmp/oaansible.log
```

## 🔒 Security & Authentication

### Authentication Methods

- **JWT Tokens**: For programmatic access and integration
- **oaDashboard Integration**: SSO with existing user accounts
- **API Keys**: For service-to-service authentication
- **Role-Based Access**: Admin and user permission levels

### Security Features

- **Network Security**: Tailscale-based access control
- **Input Validation**: Comprehensive request validation
- **Audit Logging**: Complete deployment and access logs
- **Resource Limits**: Job timeout and concurrency controls

### Configuration

```bash
# Environment variables for security
export OAANSIBLE_SECRET_KEY="your-secure-secret-key"
export OADASHBOARD_API_URL="http://localhost:8000"
export OADASHBOARD_API_KEY="your-dashboard-api-key"
```

## 🛠️ Development & Testing

### Framework Testing

```bash
# Test component framework
./scripts/demo-framework

# Test server API
./scripts/demo-server

# Dry-run all components
./scripts/run-component staging macos-api macos-tracker --dry-run
```

### Development Server

```bash
# Start with auto-reload
./scripts/run-server --dev --port 8001

# Test API endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api/components
```

### Performance Measurement

```bash
# Measure deployment performance
./scripts/measure-performance staging baseline
./scripts/measure-performance staging improved
./scripts/measure-performance staging comparison
```

## 🔄 Migration & Upgrade

### From Legacy oaAnsible

The new system maintains backward compatibility while providing enhanced capabilities:

1. **Existing Scripts**: Legacy scripts continue to work
2. **Inventory Compatibility**: Existing inventory files are supported
3. **Gradual Migration**: Adopt new features incrementally
4. **Enhanced Performance**: 50% reduction in repeated deployment time

### Recommended Migration Path

1. **Start with Components**: Use `./scripts/run-component` for new deployments
2. **Test Server Integration**: Deploy server API for remote execution
3. **Enable Advanced Features**: Adopt dry-run, check, and diff modes
4. **Integrate with Dashboard**: Connect to oaDashboard for centralized management

## 📈 Performance & Scalability

### Achieved Improvements

- **⚡ 50% Faster**: Reduced deployment time through intelligent state detection
- **🧠 Smarter Execution**: Skip unnecessary tasks with comprehensive idempotency
- **🔄 Concurrent Jobs**: Handle multiple deployments simultaneously
- **📊 Real-time Monitoring**: Live progress tracking and logging

### Scalability Features

- **Job Queuing**: SQLite-based job management with concurrent execution
- **Resource Management**: CPU, memory, and disk space monitoring
- **Performance Metrics**: Execution time tracking and optimization
- **Caching**: Fact caching and state detection optimization

## 🤝 Contributing

oaAnsible follows a comprehensive development framework:

1. **Component Development**: Add new components to the framework
2. **Platform Support**: Extend to additional platforms
3. **Server Features**: Enhance API capabilities and integrations
4. **Documentation**: Maintain comprehensive guides and examples

### Development Workflow

```bash
# Test changes with dry-run
./scripts/run-component staging your-component --dry-run

# Validate with check mode
./scripts/run-component staging your-component --check

# Run server tests
./scripts/demo-server
```

## 📚 Documentation

### Essential Guides

| Guide                                          | Description                                       | Use Case                           |
| ---------------------------------------------- | ------------------------------------------------- | ---------------------------------- |
| **[Script Usage Guide](docs/SCRIPT_USAGE.md)** | Complete examples for all platforms and scenarios | New users, comprehensive reference |
| **[Quick Reference](docs/QUICK_REFERENCE.md)** | Common commands and quick examples                | Daily operations, quick lookup     |
| **[WiFi Setup Guide](docs/WIFI_SETUP.md)**     | Complete WiFi configuration walkthrough           | Network configuration              |

### Additional Documentation

- [Environment System](docs/ENVIRONMENT_SYSTEM.md) - Environment and inventory management
- [Component Framework](docs/components.md) - Component system architecture
- [Server API](docs/server-api.md) - REST API documentation
- [ALPR Integration](docs/alpr-integration.md) - License plate recognition setup
- [System Architecture](docs/SYSTEM.md) - Overall system design
- [Workflow Guide](docs/WORKFLOW.md) - Development and deployment workflows

### Quick Links

```bash
# 📖 Complete script examples
cat docs/SCRIPT_USAGE.md

# ⚡ Quick command reference
cat docs/QUICK_REFERENCE.md

# 📡 WiFi configuration guide
cat docs/WIFI_SETUP.md
```

---

**oaAnsible** - Advanced Multi-Platform Orchestration System  
Part of the OrangeAd Pangaea Project | Phase 4 Complete ✅
