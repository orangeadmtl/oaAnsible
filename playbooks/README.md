# OrangeAd Ansible Playbooks

This directory contains the streamlined playbook structure for OrangeAd infrastructure automation.

## 🚀 Primary Playbooks (Active)

### `universal.yml` - **Universal Component Framework**
**The main entry point for 80%+ of deployments**

- **Purpose**: Universal platform-agnostic deployment with intelligent component routing
- **Features**: 
  - Automatic platform detection (macOS/Ubuntu)
  - Tag-based component selection
  - Inventory-driven configuration
  - Performance optimizations for tag-based deployments
- **Usage**:
  ```bash
  # Full deployment (inventory-driven)
  ansible-playbook universal.yml -i inventory/f1-prod.yml
  
  # Component-specific deployment
  ansible-playbook universal.yml -i inventory/f1-prod.yml -t macos-api
  ansible-playbook universal.yml -i inventory/f1-prod.yml -t tracker,security
  ansible-playbook universal.yml -i inventory/ubuntu.yml -t base,network,optimization
  ```

### `ubuntu-onboarding.yml` - **Ubuntu Server Onboarding**
**Comprehensive Ubuntu server setup with profile-based deployment**

- **Purpose**: Full Ubuntu server onboarding with intelligent configuration
- **Profiles**: server, ml, development, minimal
- **Features**: Smart component detection, reboot handling, completion reporting
- **Usage**:
  ```bash
  ansible-playbook ubuntu-onboarding.yml -i inventory/ubuntu-servers.yml
  ansible-playbook ubuntu-onboarding.yml -i inventory/ml-servers.yml -e deployment_mode=ml
  ```

## 🎯 Specialized Playbooks

### `onboard-ml-macos.yml` - **macOS ML Workstation**
**oaSentinel ML development environment setup for macOS**

- **Purpose**: macOS-specific ML workstation configuration
- **Includes**: Python, oaSentinel, development tools, GPU optimization
- **Usage**:
  ```bash
  ansible-playbook onboard-ml-macos.yml -i inventory/ml-macos-dev.yml
  ```

### `onboard-ml-server.yml` - **Ubuntu ML Training Server**
**High-performance ML training server with GPU support**

- **Purpose**: Ubuntu ML server with NVIDIA drivers, CUDA, PyTorch
- **Features**: GPU detection, Docker support, monitoring, remote access
- **Usage**:
  ```bash
  ansible-playbook onboard-ml-server.yml -i inventory/ml-ubuntu-servers.yml
  ```

## 📁 Directory Structure

```
playbooks/
├── universal.yml              # 🌟 PRIMARY: Universal component framework
├── ubuntu-onboarding.yml      # Ubuntu server onboarding
├── onboard-ml-macos.yml      # macOS ML workstation setup  
├── onboard-ml-server.yml     # Ubuntu ML server setup
├── dev/                      # Development & testing playbooks
│   ├── README.md
│   ├── cleanup.yml           # macOS dev environment cleanup
│   ├── debug-vault.yml       # Ansible vault debugging
│   ├── enhance-macos-shell.yml
│   └── test-ml-setup.yml     # Local ML testing
└── legacy/                   # Superseded playbooks (for reference)
    ├── README.md
    ├── macos-full.yml        # → Use universal.yml instead
    ├── ubuntu-full.yml       # → Use universal.yml instead
    ├── server_optimizations.yml # → Use universal.yml -t optimization
    └── ...
```

## 🏷️ Universal.yml Tag System

The universal playbook supports comprehensive tag-based deployment:

### Infrastructure Tags
- `base` - Base system setup
- `network` - Network configuration
- `security` - Security hardening
- `ssh` - SSH configuration
- `optimization` - Performance optimizations

### Application Tags  
- `macos-api` (or `api`) - macOS API service
- `tracker` - Object tracking service
- `player` - Video player service
- `alpr` - ALPR service
- `camguard` - Camera guard service
- `cursorcerer` - Cursor service

### Platform-Specific Tags
- `docker` - Docker installation
- `nvidia` (or `gpu`) - NVIDIA drivers
- `ml` - ML workstation setup
- `health` - Health monitoring

### oaSentinel Tags
- `oasentinel-setup` - Basic oaSentinel setup
- `oasentinel-data` - Data management
- `oasentinel-train` - Training environment
- `oasentinel-full` (or `oasentinel`) - Complete setup

## 📋 Migration Guide

If you're migrating from legacy playbooks:

| Old Command | New Command |
|------------|-------------|
| `ansible-playbook macos-full.yml -i inventory` | `ansible-playbook universal.yml -i inventory` |
| `ansible-playbook ubuntu-full.yml -i inventory` | `ansible-playbook universal.yml -i inventory` |
| `ansible-playbook server_optimizations.yml -i inventory` | `ansible-playbook universal.yml -i inventory -t optimization` |

## ⚡ Performance Tips

1. **Use tags for faster deployments**: `universal.yml -t component` is faster than full deployments
2. **Leverage inventory configuration**: Set `deploy_*` variables in inventory instead of multiple playbook runs
3. **Use specific inventories**: Target only necessary hosts for better performance

## 🔗 Integration

- **Main Entry Point**: `/oaAnsible/main.yml` imports `universal.yml`
- **CLI Integration**: Works with `./scripts/run` wrapper script
- **Component Framework**: Powered by `/tasks/` component system