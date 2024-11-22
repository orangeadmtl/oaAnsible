# OrangeAd Mac Setup Playbook

Ansible playbook for automated setup and configuration of macOS devices for OrangeAd.

## Features

- Automated Homebrew installation and package management
- Python environment setup with pyenv
- Node.js setup with NVM
- Tailscale network configuration with DNS management
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
macos-setup/
├── inventory/            # Environment-specific inventories
│   ├── production/      # Production environment
│   │   ├── hosts.yml    # Production hosts
│   │   └── group_vars/  # Production variables
│   └── staging/        # Staging environment
│       ├── hosts.yml    # Staging hosts
│       └── group_vars/  # Staging variables
├── roles/
│   └── local/          # Custom local role
│       ├── tasks/      # Role-specific tasks
│       └── defaults/   # Default variables
├── tasks/              # Global tasks
│   ├── pre_checks.yml  # System verification
│   └── verify.yml      # Post-install checks
├── scripts/            # Convenience scripts
│   ├── run-staging.sh
│   └── run-production.sh
├── main.yml            # Main playbook
└── dev-cleanup.yml     # Development reset playbook
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
- `verify`: Verification tasks
- `dev`: Development tools
- `network`: Network settings

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
```

## Verification System

Run verification independently:

```sh
# Full verification
ansible-playbook main.yml --tags "verify" -i inventory/[env]/hosts.yml

# Component-specific verification
ansible-playbook main.yml --tags "verify,python" -i inventory/[env]/hosts.yml
```

Verifies:

- System requirements
- Package installations
- Runtime environments
- Network connectivity
- Service status

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
