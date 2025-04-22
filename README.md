# OrangeAd Mac Setup Playbook

Ansible playbook for automated setup and configuration of macOS devices for OrangeAd. This repository is part of the `oaPangaea` monorepo and provides comprehensive macOS device management capabilities.

## Features

- Automated Homebrew installation and package management
- Python environment setup with pyenv
- Node.js setup with NVM
- Tailscale network configuration with DNS management
- macOS API service for device monitoring and management
- Dynamic inventory using Tailscale API
- Enhanced security and system settings configuration
- Environment-specific configurations (staging/production)
- Comprehensive verification system
- Development cleanup tools

## Prerequisites

1. On your control machine:

   ```sh
   # Install Ansible
   pip3 install ansible

   # Clone this repository
   git clone https://github.com/oa-device/macos-setup.git
   cd macos-setup

   # Install required Ansible roles and collections
   ansible-galaxy install -r requirements.yml
   ```

2. On target machines:
   - macOS (Intel or Apple Silicon)
   - SSH access configured
   - Sudo privileges
   - Minimum 8GB RAM

## Directory Structure

```tree
oaAnsible/
├── inventory/                # Environment-specific inventories
│   ├── production/           # Production environment
│   │   ├── hosts.yml         # Production hosts
│   │   └── group_vars/       # Production variables
│   ├── staging/              # Staging environment
│   │   ├── hosts.yml         # Staging hosts
│   │   └── group_vars/       # Staging variables
│   └── dynamic_inventory.py  # Dynamic inventory script using Tailscale API
├── roles/
│   ├── macos/                # macOS-specific roles
│   │   ├── api/              # macOS API service deployment
│   │   ├── base/             # Base system configuration
│   │   ├── network/          # Network configuration
│   │   │   └── tailscale/    # Tailscale VPN setup
│   │   ├── node/             # Node.js setup
│   │   ├── python/           # Python setup
│   │   ├── security/         # Security settings
│   │   └── settings/         # System preferences
│   ├── elliotweiser.osx-command-line-tools/  # External role (from Galaxy)
│   └── geerlingguy.dotfiles/                 # External role (from Galaxy)
├── macos-api/                # FastAPI service for macOS monitoring
│   ├── core/                 # Core functionality
│   ├── models/               # Data models
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic
│   └── main.py               # Entry point
├── tasks/                    # Global tasks
│   ├── pre_checks.yml        # System verification
│   └── verify.yml            # Post-install checks
├── scripts/                  # Convenience scripts
│   ├── run-staging.sh        # Run playbook on staging
│   ├── run-production.sh     # Run playbook on production
│   ├── deploy-macos-api.sh   # Deploy macOS API only
│   └── verify-macos-api.sh   # Verify macOS API deployment
├── group_vars/               # Global variables
│   └── all/                  # Variables for all hosts
│       └── vault.yml         # Encrypted sensitive variables
├── main.yml                  # Main playbook
├── deploy-macos-api.yml      # macOS API deployment playbook
└── dev-cleanup.yml           # Development reset playbook
```

## Usage

### Quick Start

1. For staging environment:

   ```bash
   ./scripts/run-staging.sh
   ```

2. For production environment:

   ```bash
   ./scripts/run-production.sh
   ```

### Environment Differences

| Feature           | Staging  | Production |
| ----------------- | -------- | ---------- |
| Host Key Checking | Disabled | Enabled    |
| Debug Mode        | Enabled  | Disabled   |
| Dev Packages      | Full Set | Minimal    |
| DNS Management    | Optional | Required   |
| Security Checks   | Basic    | Strict     |

### Available Tags

- `setup`: Base system configuration
- `cli`: Command Line Tools installation
- `homebrew`: Package management
- `python`: Python/pyenv setup
- `node`: Node.js/nvm setup
- `tailscale`: Network configuration
- `security`: Security settings
- `settings`: System preferences
- `api`: macOS API service
- `verify`: Verification tasks
- `dev`: Development tools
- `network`: Network settings
- `configuration`: General configuration tasks

## Configuration

### Environment Variables

Each environment (staging/production) has its own configuration in `inventory/[env]/group_vars/all.yml`:

- Runtime versions (Python, Node.js)
- Feature toggles
- System packages
- Network settings

### Feature Toggles

```yaml
configure:
  tailscale: true/false
  pyenv: true/false
  node: true/false
  security: true/false
  settings: true/false
  api: true/false
```

## Verification System

Run verification independently:

```sh
# Full verification
ansible-playbook main.yml --tags "verify" -i inventory/[env]/hosts.yml

# Component-specific verification
ansible-playbook main.yml --tags "verify,python" -i inventory/[env]/hosts.yml

# Verify macOS API specifically
./scripts/verify-macos-api.sh
```

Verifies:

- System requirements
- Package installations
- Runtime environments
- Network connectivity
- macOS API service status
- Security settings
- System preferences

## Development Tools

### Development Cleanup Playbook

⚠️ **STAGING ENVIRONMENT ONLY** ⚠️

Reset your staging environment to a clean state:

```bash
ansible-playbook dev-cleanup.yml -K -i inventory/staging/hosts.yml
```

**Safety Features:**

1. Staging inventory only
2. Interactive confirmation
3. Comprehensive warnings
4. Cannot affect production

### macOS API Deployment

Deploy only the macOS API service to staging:

```bash
./scripts/deploy-macos-api.sh
```

This script:

1. Runs the dedicated `deploy-macos-api.yml` playbook
2. Configures the macOS API service on the target machine
3. Sets up the launchd service to run as the `_orangead` system user

### Dynamic Inventory

The dynamic inventory script (`inventory/dynamic_inventory.py`) uses the Tailscale API to:

1. Discover all devices in your Tailscale network
2. Filter for macOS devices
3. Generate an inventory with appropriate groups and variables

To use dynamic inventory:

```bash
ansible-playbook main.yml -i inventory/dynamic_inventory.py
```

## Troubleshooting

1. Enable debug output:

   ```sh
   ansible-playbook main.yml -vvv -i inventory/[env]/hosts.yml
   ```

2. Run in check mode:

   ```sh
   ansible-playbook main.yml --check -i inventory/[env]/hosts.yml
   ```

3. Common Issues:
   - Insufficient system resources
   - Network connectivity problems
   - Permission issues
   - Shell configuration conflicts
