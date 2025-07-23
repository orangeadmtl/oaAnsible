# oaAnsible

Infrastructure automation system for deploying and managing OrangeAd services across macOS and Ubuntu platforms using Ansible.

## Overview

**Purpose:** Automated deployment of `macos-api` and `oaTracker` to Mac Mini devices  
**Technology:** Ansible playbooks with tag-based component deployment  
**Features:** Multi-platform support, security management, service orchestration, idempotent operations

📚 **[Complete Documentation](../docs/README.md)**

## Quick Start

> **🏗️ Monorepo Development**: See [Development Guide](../docs/development/getting_started.md) for standardized workflow.

**Prerequisites:** Python 3.12+, Ansible Core, SSH keys, vault password, Tailscale network

```bash
# Basic deployment commands
./scripts/run spectra-preprod -t macos-api    # Deploy API service
./scripts/run spectra-preprod -t tracker      # Deploy AI tracking
./scripts/run spectra-preprod --dry-run       # Preview changes

# Common operations
./scripts/check     # Syntax validation
./scripts/sync      # Sync configurations
./scripts/genSSH    # Generate SSH keys
```

## Key Components

**Available Tags:**
- `macos-api` - Device monitoring API (port 9090)
- `tracker` - AI tracking system (port 8080) 
- `base` - Core system setup
- `network` - Tailscale VPN configuration
- `security` - TCC permissions & firewall

**Environments:** `spectra-prod`, `spectra-preprod`, `f1-prod`, `f1-preprod`, `alpr-prod`

## Key Documentation

- 🏗️ **[System Architecture](../docs/architecture/system_overview.md)** - Component relationships
- 🚀 **[Infrastructure Guide](../docs/infrastructure/deployment.md)** - Deployment procedures
- 📊 **[Performance Audit](../docs/infrastructure/performance_audit.md)** - Optimization analysis
- 🔧 **[Server API](../docs/infrastructure/server_api.md)** - API documentation
- ⚡ **[Getting Started](../docs/development/getting_started.md)** - Development workflow

## Project Structure

```
oaAnsible/
├── playbooks/     # Deployment playbooks
├── roles/         # Platform-specific roles (macos/, ubuntu/, common/)
├── inventory/     # Environment configurations
├── scripts/       # Management scripts
├── macos-api/     # macOS API source code
└── server/        # Optional server-side execution
```
