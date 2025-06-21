# oaAnsible Scripts Usage Guide

Complete guide for using the oaAnsible deployment scripts across all platforms and use cases.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Script Overview](#-script-overview)
- [Platform Deployments](#-platform-deployments)
- [Component Deployments](#-component-deployments)
- [Environment Management](#-environment-management)
- [Environment Configuration](#-environment-configuration)
- [Mass Deployments](#-mass-deployments)
- [Advanced Usage](#-advanced-usage)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

```bash
# Basic full deployment to staging
./scripts/run-staging -l hostname

# Check mode (dry run) before deploying
./scripts/run-staging -l hostname --check

# Deploy specific components
./scripts/run-component staging macos-api tracker -l hostname

# Mass deployment to all production devices
./scripts/run-prod
```

## 📂 Script Overview

### Core Deployment Scripts

| Script            | Purpose                          | Usage                                     |
| ----------------- | -------------------------------- | ----------------------------------------- |
| `run-staging`     | Deploy to staging environment    | Development and testing                   |
| `run-preprod`     | Deploy to pre-production         | Final testing before production           |
| `run-prod`        | Deploy to production             | Production deployments with safety checks |
| `run-component`   | Deploy specific components       | Granular control over what gets deployed  |
| `run-environment` | Environment-specific deployments | Custom deployment modes                   |
| `run-platform`    | Platform-specific deployments    | Force platform-specific behavior          |
| `run-verify`      | Post-deployment verification     | Validate deployments                      |

### Specialized Scripts

| Script          | Purpose                                     |
| --------------- | ------------------------------------------- |
| `deploy-server` | Ubuntu server onboarding                    |
| `genSSH`        | SSH key management and connectivity testing |
| `oassh`         | Enhanced SSH access to managed devices      |

## 🖥️ Platform Deployments

### macOS Deployments

#### Full macOS Stack

```bash
# Deploy complete macOS stack (base system + macos-api + tracker)
./scripts/run-staging -l mac-mini-01

# Production deployment with confirmation
./scripts/run-prod -l mac-mini-01

# Check what would be deployed
./scripts/run-staging -l mac-mini-01 --check
```

#### Base macOS Only

```bash
# Deploy base system configuration only
./scripts/run-environment staging base -l mac-mini-01

# Or using run-component
./scripts/run-component staging base-system -l mac-mini-01
```

#### macOS API Only

```bash
# Deploy just the macOS API service
./scripts/run-component staging macos-api -l mac-mini-01

# With verbose output
./scripts/run-component staging macos-api -l mac-mini-01 -v
```

#### Tracker Only

```bash
# Deploy just the tracker service
./scripts/run-component staging tracker -l mac-mini-01

# Force deployment (skip confirmations)
./scripts/run-component staging tracker -l mac-mini-01 --extra-vars "execution_mode=force"
```

### Ubuntu Server Deployments

#### Ubuntu Server Onboarding

```bash
# Deploy complete Ubuntu server stack
./scripts/deploy-server -e staging -h 192.168.1.100

# With specific user and tags
./scripts/deploy-server -e staging -h 192.168.1.100 -u admin -t base,security

# Check mode
./scripts/deploy-server -e staging -h 192.168.1.100 -c
```

#### Ubuntu Full Stack

```bash
# Using run-platform for Ubuntu
./scripts/run-platform staging ubuntu -l ubuntu-server-01

# Using run-environment
./scripts/run-environment staging full -l ubuntu-server-01
```

## 🧩 Component Deployments

### Single Components

```bash
# Deploy individual components
./scripts/run-component staging base-system -l hostname
./scripts/run-component staging python -l hostname
./scripts/run-component staging network-stack -l hostname
./scripts/run-component staging macos-api -l hostname
./scripts/run-component staging tracker -l hostname
```

### Component Combinations

#### API + Tracker Stack

```bash
# Deploy both API and tracker services
./scripts/run-component staging macos-api tracker -l mac-mini-01

# With dependencies automatically resolved
./scripts/run-component staging macos-api tracker -l mac-mini-01 -v
```

#### Complete Development Stack

```bash
# Base system + Python + API + Tracker
./scripts/run-component staging base-system python macos-api tracker -l mac-mini-01
```

#### Network + WiFi Configuration

```bash
# First enable WiFi in group_vars (see WiFi section below)
./scripts/run-component staging network-stack -l mac-mini-01 -t wifi

# Or deploy network configuration only
./scripts/run-environment staging network -l mac-mini-01
```

## 🌐 Environment Management

### Staging Environment

```bash
# Full staging deployment
./scripts/run-staging

# Specific hosts in staging
./scripts/run-staging -l "mac-mini-01,mac-mini-02"

# Staging with specific tags
./scripts/run-staging -t network,security
```

### Pre-Production Environment

```bash
# Pre-prod safety features enabled
./scripts/run-preprod -l mac-mini-staging

# Pre-prod with component selection
./scripts/run-environment preprod components macos-api tracker -l mac-mini-staging
```

### Production Environment

```bash
# Production with safety confirmation
./scripts/run-prod -l mac-mini-prod

# Production with specific components
./scripts/run-component production macos-api -l mac-mini-prod

# Force production deployment (skip confirmations)
./scripts/run-prod -l mac-mini-prod --extra-vars "execution_mode=force"
```

## ⚙️ Environment Configuration

### Environment Safety System

oaAnsible uses a three-tier environment system with built-in safety controls:

- **Staging**: VM environment for experimental features
- **Pre-prod**: Real Mac Mini for final testing
- **Production**: Field devices requiring maximum safety

### Environment Variables

Each environment is configured in `inventory/{env}/group_vars/all.yml`:

```yaml
oa_environment:
  name: "staging" # Environment identifier
  allow_experimental: true # Enable experimental features
  allow_server_optimizations: true # Enable UI minimization, auto-login
  allow_destructive_operations: true # Enable daily reboot, etc.
  allow_tailscale_changes: true # Enable Tailscale installation/config
```

### Environment-Specific Controls

| Feature                | Staging | Pre-prod      | Production    |
| ---------------------- | ------- | ------------- | ------------- |
| Hardware               | VM      | Real Mac Mini | Field Devices |
| Experimental Features  | ✅      | ❌            | ❌            |
| Server Optimizations   | ✅      | ✅            | ❌            |
| Destructive Operations | ✅      | ❌            | ❌            |
| Tailscale Changes      | ✅      | ✅            | ❌\*          |
| Safety Prompts         | ❌      | ✅            | ✅            |

\*Production Tailscale requires explicit override

### Using Environment Controls in Playbooks

```yaml
# Role-level control
- role: macos/server_optimizations
  when: oa_environment.allow_server_optimizations | default(false)

# Task-level control
- name: Configure daily reboot
  block:
    # ... tasks ...
  when: oa_environment.allow_destructive_operations | default(true)
```

### Emergency Production Overrides

```bash
# Skip safety checks (emergency only)
ansible-playbook main.yml -i inventory/production/hosts.yml --extra-vars "skip_safety_checks=true"

# Allow Tailscale changes in production (dangerous!)
ansible-playbook main.yml -i inventory/production/hosts.yml --tags tailscale --extra-vars "oa_environment.allow_tailscale_changes=true"
```

## 📡 Mass Deployments

### Deploy to All Devices in Environment

```bash
# Deploy to ALL staging devices
./scripts/run-staging

# Deploy to ALL production devices (with confirmation)
./scripts/run-prod

# Deploy to ALL pre-production devices
./scripts/run-preprod
```

### Deploy to All Devices with Specific Stack

```bash
# Deploy API + Tracker to all staging devices
./scripts/run-component staging macos-api tracker

# Deploy full stack to all production devices
./scripts/run-environment production full

# Deploy base configuration to all devices
./scripts/run-environment staging base
```

### Deploy to Device Groups

```bash
# Deploy to specific group of devices
./scripts/run-staging -l "mac-mini-01,mac-mini-02,mac-mini-03"

# Deploy to pattern-matched devices
./scripts/run-staging -l "mac-mini-*"

# Deploy components to multiple devices
./scripts/run-component staging macos-api -l "kampus-rig,m4-ca-001"
```

## 🔧 Advanced Usage

### WiFi Configuration

#### Enable WiFi Configuration

```bash
# 1. Enable WiFi in group_vars
# Edit inventory/platforms/macos/group_vars/all.yml:
# network:
#   configure_wifi: true

# 2. Add WiFi credentials to vault
ansible-vault edit group_vars/all/vault.yml
# Add:
# vault_wifi_networks:
#   - ssid: "Kampus"
#     password: "Kampus94"
#     security_type: "WPA2"

# 3. Deploy WiFi configuration
./scripts/run-staging -l mac-mini-01 -t wifi
```

### ZSH Shell Enhancement

```bash
# Deploy enhanced shell configuration
./scripts/run-component staging base-system -l mac-mini-01 -t shell

# Or as part of base system deployment
./scripts/run-environment staging base -l mac-mini-01
```

### Execution Modes

#### Check Mode (Dry Run)

```bash
# See what would be deployed without making changes
./scripts/run-staging -l hostname --check
./scripts/run-component staging macos-api -l hostname --check
```

#### Diff Mode

```bash
# Show detailed differences
./scripts/run-staging -l hostname --diff
```

#### Force Mode

```bash
# Skip safety checks and confirmations
./scripts/run-staging -l hostname --extra-vars "execution_mode=force"
```

#### Verbose Mode

```bash
# Enable verbose output
./scripts/run-staging -l hostname -v
./scripts/run-staging -l hostname -vv  # Even more verbose
```

### Tag-Based Deployments

```bash
# Deploy only network-related tasks
./scripts/run-staging -l hostname -t network

# Deploy only security configurations
./scripts/run-staging -l hostname -t security

# Deploy WiFi and network together
./scripts/run-staging -l hostname -t "wifi,network"

# Skip specific tags
./scripts/run-staging -l hostname --skip-tags "backup,cleanup"
```

### Custom Variable Overrides

```bash
# Override default variables
./scripts/run-staging -l hostname --extra-vars "tracker_enabled=false"

# Multiple variable overrides
./scripts/run-staging -l hostname --extra-vars "execution_mode=force api_port=9091"

# Use variable files
./scripts/run-staging -l hostname --extra-vars "@custom_vars.yml"
```

## 🔍 Verification and Monitoring

### Post-Deployment Verification

```bash
# Verify all components
./scripts/run-verify staging all -l hostname

# Verify specific components
./scripts/run-verify staging macos_api -l hostname
./scripts/run-verify staging tracker -l hostname

# Verify services status
./scripts/run-verify staging services -l hostname
```

### SSH Access and Management

```bash
# Generate and distribute SSH keys
./scripts/genSSH

# Enhanced SSH access
./scripts/oassh hostname

# Test SSH connectivity
./scripts/genSSH --test hostname
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Vault Password Issues

```bash
# Ensure vault password file exists
ls -la vault_password_file

# Test vault access
ansible-vault view group_vars/all/vault.yml --vault-password-file vault_password_file
```

#### SSH Key Issues

```bash
# Load SSH keys
./scripts/genSSH

# Test SSH connectivity
ssh-add -l
ssh hostname "echo 'Connection test'"
```

#### Platform Detection Issues

```bash
# Run with verbose platform detection
./scripts/run-staging -l hostname --extra-vars "platform_detection_debug=true"
```

#### Component Dependency Issues

```bash
# Use component framework to show dependencies
./scripts/run-component staging macos-api --check -v
```

### Debug Mode

```bash
# Enable debug logging
./scripts/run-staging -l hostname -vvv

# Check what tasks would run
./scripts/run-staging -l hostname --list-tasks

# Check variable values
./scripts/run-staging -l hostname --extra-vars "debug_mode=true"
```

### Performance Measurement

```bash
# Measure deployment performance
./scripts/measure-performance staging hostname

# Compare different deployment methods
./scripts/measure-performance staging hostname --components macos-api
```

## 📝 Best Practices

### Development Workflow

1. Always test in staging first: `./scripts/run-staging -l hostname --check`
2. Use component deployments for faster iterations: `./scripts/run-component staging macos-api -l hostname`
3. Verify deployments: `./scripts/run-verify staging all -l hostname`

### Production Workflow

1. Test in pre-prod: `./scripts/run-preprod -l hostname`
2. Deploy with confirmation: `./scripts/run-prod -l hostname`
3. Verify critical components: `./scripts/run-verify production services -l hostname`

### Mass Deployment Workflow

1. Start with check mode: `./scripts/run-prod --check`
2. Deploy to small batch first: `./scripts/run-prod -l "critical-device-01"`
3. Deploy to remaining devices: `./scripts/run-prod`

---

## 📚 Additional Resources

- [Environment Configuration](SCRIPT_USAGE.md#-environment-configuration)
- [Component Framework](components.md)
- [Server API Documentation](server-api.md)

For questions or issues, check the troubleshooting section above or consult the main project documentation.
