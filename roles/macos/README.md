# macOS Role

Simplified role for configuring macOS devices in the OrangeAd infrastructure.

## Structure

```bash
macos/
├── handlers/
│   └── main.yml        # Service handlers
├── tasks/
│   └── main.yml        # Main tasks file
├── templates/
│   └── com.orangead.macosapi.plist.j2  # Launchd plist template
└── README.md           # This file
```

## Features

1. **Base System Configuration**

   - Shell environment setup
   - Path configuration
   - Homebrew integration

2. **Network Configuration**

   - DNS settings
   - Network interface management
   - Tailscale integration

3. **Security**

   - Firewall configuration
   - Screen lock settings
   - FileVault status check

4. **macOS API**
   - Service deployment
   - Virtual environment setup
   - Systemd/launchd service configuration

## Usage

Include this role in your playbook:

```yaml
- hosts: macos_devices
  roles:
    - role: macos
      vars:
        configure:
          tailscale: true
          pyenv: true
```

## Variables

- `configure.tailscale`: Enable Tailscale configuration (default: false)
- `configure.pyenv`: Enable Pyenv configuration (default: false)
- `dns.tailscale_servers`: List of Tailscale DNS servers

## Tags

- `network`: Network-related tasks
- `security`: Security-related tasks
- `api`: macOS API deployment tasks
- `shell`: Shell configuration tasks
