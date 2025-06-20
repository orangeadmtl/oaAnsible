# oaAnsible Scripts Quick Reference

## 🚀 Most Common Commands

```bash
# Full stack deployment
./scripts/run-staging -l hostname                    # Deploy everything to staging
./scripts/run-prod -l hostname                       # Deploy everything to production

# Component deployment
./scripts/run-component staging macos-api -l hostname        # Deploy API only
./scripts/run-component staging tracker -l hostname          # Deploy tracker only
./scripts/run-component staging macos-api tracker -l hostname # Deploy API + tracker

# Mass deployment
./scripts/run-staging                                 # Deploy to ALL staging devices
./scripts/run-prod                                   # Deploy to ALL production devices

# Check mode (dry run)
./scripts/run-staging -l hostname --check            # See what would be deployed
```

## 📋 Script Reference

| Command         | Purpose                       | Example                                                    |
| --------------- | ----------------------------- | ---------------------------------------------------------- |
| `run-staging`   | Deploy to staging environment | `./scripts/run-staging -l mac-mini-01`                     |
| `run-preprod`   | Deploy to pre-production      | `./scripts/run-preprod -l mac-mini-01`                     |
| `run-prod`      | Deploy to production          | `./scripts/run-prod -l mac-mini-01`                        |
| `run-component` | Deploy specific components    | `./scripts/run-component staging macos-api -l mac-mini-01` |
| `deploy-alpr`   | Deploy ALPR service           | `./scripts/deploy-alpr mac-mini-01`                        |

## 🧩 Available Components

| Component       | Platform | Description                     |
| --------------- | -------- | ------------------------------- |
| `base-system`   | All      | Foundation system configuration |
| `python`        | All      | Python runtime environment      |
| `network-stack` | All      | Tailscale VPN and networking    |
| `macos-api`     | macOS    | Device management API           |
| `tracker`       | macOS    | AI tracking system              |
| `alpr`          | macOS    | License plate recognition       |

## 🏷️ Common Tags

| Tag        | Purpose                 | Example                                         |
| ---------- | ----------------------- | ----------------------------------------------- |
| `wifi`     | WiFi configuration      | `./scripts/run-staging -l hostname -t wifi`     |
| `network`  | Network setup           | `./scripts/run-staging -l hostname -t network`  |
| `security` | Security configurations | `./scripts/run-staging -l hostname -t security` |

## 🎯 Quick Examples

### macOS Deployments

```bash
# Full macOS stack
./scripts/run-staging -l mac-mini-01

# Just the API
./scripts/run-component staging macos-api -l mac-mini-01

# API + Tracker
./scripts/run-component staging macos-api tracker -l mac-mini-01

# ALPR service
./scripts/deploy-alpr mac-mini-01
```

### Ubuntu Server

```bash
# Ubuntu server setup
./scripts/deploy-server -e staging -h 192.168.1.100

# Full Ubuntu stack
./scripts/run-platform staging ubuntu -l ubuntu-server-01
```

### Mass Deployments

```bash
# All staging devices with full stack
./scripts/run-staging

# All production with API only
./scripts/run-component production macos-api

# Multiple specific devices
./scripts/run-staging -l "mac-mini-01,mac-mini-02,mac-mini-03"
```

### Special Configurations

```bash
# WiFi setup (requires enabling in group_vars first)
./scripts/run-staging -l hostname -t wifi

# Base system only
./scripts/run-environment staging base -l hostname

# Force deployment (skip confirmations)
./scripts/run-staging -l hostname --extra-vars "execution_mode=force"
```

## 🔍 Troubleshooting Commands

```bash
# Check what would be deployed
./scripts/run-staging -l hostname --check

# Verbose output for debugging
./scripts/run-staging -l hostname -v

# Test SSH connectivity
./scripts/genSSH --test hostname

# Verify deployment
./scripts/run-verify staging all -l hostname
```

---

💡 **Need more details?** See the full [SCRIPT_USAGE.md](SCRIPT_USAGE.md) guide for comprehensive examples and advanced usage patterns.
