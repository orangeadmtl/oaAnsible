# OrangeAd Mac Setup Playbook

Ansible playbook for automated setup and configuration of macOS devices for OrangeAd.

## Features

- Automated Homebrew installation and package management
- Python environment setup with pyenv
- Node.js setup with NVM
- Tailscale configuration (compiled from Go source)
- System security configuration
- Automated verification system

## Prerequisites

1. On your control machine:

```sh
pip3 install ansible
ansible-galaxy install -r requirements.yml
```

2. On target machines:

```sh
xcode-select --install
```

## Directory Structure

```tree
oaAnsible/
├── group_vars/        # Global variables and configurations
├── inventory/         # Environment-specific host definitions
├── roles/            # Ansible roles
│   └── local/        # Custom local role for OrangeAd
├── tasks/            # Global tasks
│   ├── pre_checks.yml    # Pre-flight system checks
│   └── verify.yml        # Post-installation verification
├── ansible.cfg       # Ansible configuration
└── main.yml         # Main playbook
```

## Usage

1. Clone and setup:

```sh
git clone https://github.com/oa-device/oaAnsible.git
cd oaAnsible
```

2. Configure your environment:

   - Update inventory files in `inventory/`
   - Modify settings in `group_vars/all.yml`

3. Run the playbook:

```sh
# Full installation
ansible-playbook main.yml -K

# Specific components
ansible-playbook main.yml -K --tags "homebrew,python"
```

## Available Tags

- `setup`: Initial setup tasks
- `cli`: Command Line Tools installation
- `homebrew`: Homebrew configuration
- `python`: Python environment setup
- `node`: Node.js installation
- `tailscale`: Tailscale configuration
- `verify`: Run verification checks
- `development`: All development tools
- `network`: Network-related configurations

## Configuration

Edit `group_vars/all.yml` to customize:

- Homebrew packages
- Python/Node.js versions
- Feature toggles
- System configurations

## Verification

The playbook includes automatic verification:

```sh
ansible-playbook main.yml -K --tags "verify"
```

This checks:

- Homebrew package installation
- Tailscale connectivity
- Python/Node.js setup
- System configurations

## Troubleshooting

1. Debug mode:

```sh
ansible-playbook main.yml -K -vvv
```

2. Check mode:

```sh
ansible-playbook main.yml -K --check
```

3. Common issues:
   - Ensure Xcode CLI tools are installed
   - Check network connectivity
   - Verify sudo permissions
