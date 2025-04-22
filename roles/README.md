# OrangeAd Ansible Roles

This directory contains the Ansible roles used for configuring OrangeAd devices.

## Role Structure

The roles are organized into logical groups:

### macOS Roles

Located in the `macos/` directory, these roles handle various aspects of macOS configuration:

- `macos/api`: Deploys and configures the macOS API service
- `macos/base`: Basic system configuration for macOS
- `macos/network`: Network configuration for macOS
  - `macos/network/tailscale`: Tailscale VPN installation and configuration
- `macos/node`: Node.js installation and configuration
- `macos/python`: Python installation and configuration
- `macos/security`: Security settings for macOS
- `macos/settings`: System preferences and settings

### External Roles

These roles are installed from Ansible Galaxy and are excluded from version control:

- `elliotweiser.osx-command-line-tools`: Installs macOS Command Line Tools
- `geerlingguy.dotfiles`: Manages dotfiles
- `geerlingguy.mac.homebrew`: Manages Homebrew packages (collection)

## Role Dependencies

The main playbook (`main.yml`) defines the order in which roles are applied. Generally:

1. Command Line Tools and Homebrew are installed first
2. Base system configuration is applied
3. Network configuration and Tailscale are set up
4. Development tools (Python, Node.js) are installed
5. Security settings are applied
6. System preferences are configured
7. API service is deployed

## Adding New Roles

When adding new roles, follow these guidelines:

1. Use the appropriate directory structure (`macos/`, `network/`, etc.)
2. Include a `defaults/main.yml` file with default variables
3. Document role variables and dependencies
4. Use tags to allow selective execution
5. Ensure idempotence (roles can be run multiple times without side effects)
