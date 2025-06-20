# oaAnsible Scripts Directory

Quick guide for using the deployment scripts in this directory.

## 🚀 Quick Start

```bash
# Deploy full stack to staging
./run-staging -l hostname

# Deploy specific components
./run-component staging macos-api tracker -l hostname

# Deploy to all production devices (with confirmation)
./run-prod

# Check what would be deployed (dry run)
./run-staging -l hostname --check
```

## 📋 Available Scripts

### Core Deployment Scripts

- `run-staging` - Deploy to staging environment
- `run-preprod` - Deploy to pre-production environment
- `run-prod` - Deploy to production environment
- `run-component` - Deploy specific components
- `run-environment` - Environment-specific deployments
- `run-platform` - Platform-specific deployments

### Specialized Scripts

- `deploy-alpr` - ALPR service deployment
- `deploy-server` - Ubuntu server onboarding
- `run-verify` - Post-deployment verification
- `genSSH` - SSH key management
- `oassh` - Enhanced SSH access

## 🎯 Common Examples

### macOS Deployments

```bash
# Full macOS stack
./run-staging -l mac-mini-01

# Just the API service
./run-component staging macos-api -l mac-mini-01

# API + Tracker services
./run-component staging macos-api tracker -l mac-mini-01

# ALPR service with license management
./deploy-alpr mac-mini-01
```

### Mass Deployments

```bash
# Deploy to all staging devices
./run-staging

# Deploy specific components to all production devices
./run-component production macos-api

# Deploy to multiple specific devices
./run-staging -l "device1,device2,device3"
```

### Special Configurations

```bash
# WiFi configuration (requires setup in group_vars first)
./run-staging -l hostname -t wifi

# Network configuration only
./run-environment staging network -l hostname

# Base system configuration only
./run-environment staging base -l hostname
```

## 📖 Full Documentation

For comprehensive examples covering all platforms and use cases:

**→ [Complete Script Usage Guide](../docs/SCRIPT_USAGE.md)**

**→ [Quick Reference Card](../docs/QUICK_REFERENCE.md)**

**→ [WiFi Setup Guide](../docs/WIFI_SETUP.md)**

## 🆘 Need Help?

```bash
# Get help for any script
./run-staging --help
./run-component --help
./deploy-alpr --help

# Check script options
./run-staging -h
```

---

💡 **Tip**: Always test with `--check` mode first to see what would be deployed!
