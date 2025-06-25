# oaAnsible - Infrastructure Automation for OrangeAd Devices

Comprehensive Ansible automation system for deploying and managing OrangeAd infrastructure across macOS and Ubuntu platforms. Part of the `oaPangaea` monorepo
ecosystem.

## 🚀 Overview

oaAnsible provides infrastructure automation for the OrangeAd ecosystem, focusing on:

- **macOS Device Management**: Mac Mini deployment with `macos-api` and `oaTracker`
- **Ubuntu Server Configuration**: Docker environments and system optimization
- **Network Configuration**: Tailscale VPN setup and DNS management
- **Service Deployment**: Automated LaunchAgent/SystemD service management

### Key Features

- **🌐 Multi-Platform Support**: macOS Mac Minis and Ubuntu servers
- **🏷️ Tag-Based Deployment**: Deploy specific components with `--tags`
- **🔒 Security Management**: TCC permissions, firewall, and access control
- **📦 Service Orchestration**: LaunchAgent and SystemD service management
- **🛡️ Idempotent Operations**: Safe to run multiple times
- **⚡ Performance Optimized**: Fast execution with intelligent state detection

## 🏗️ Project Structure

```bash
oaAnsible/
├── 📁 playbooks/           # Deployment playbooks
│   ├── universal.yml       # Main entry point with platform detection
│   ├── macos-full.yml      # Complete macOS setup
│   ├── ubuntu-full.yml     # Complete Ubuntu setup
│   ├── deploy-macos-api.yml # macOS API deployment
│   ├── deploy-macos-tracker.yml # oaTracker deployment
│   └── components/         # Component-specific playbooks
├── 📁 roles/               # Ansible roles organized by platform
│   ├── macos/             # macOS-specific roles
│   │   ├── api/           # macOS API service
│   │   ├── tracker/       # oaTracker deployment
│   │   ├── network/       # Tailscale and networking
│   │   ├── security/      # TCC permissions and firewall
│   │   ├── python/        # Python runtime management
│   │   └── settings/      # System configuration
│   ├── ubuntu/            # Ubuntu-specific roles
│   │   ├── base/          # Base system setup
│   │   ├── docker/        # Docker environment
│   │   └── network/       # Network configuration
│   └── common/            # Shared roles
├── 📁 inventory/          # Environment configurations
│   ├── spectra-prod.yml   # Production Spectra environment
│   ├── spectra-preprod.yml # Pre-production Spectra
│   ├── f1-prod.yml        # F1 production environment
│   └── platforms/         # Platform-specific variables
├── 📁 scripts/            # Management scripts
│   ├── run               # Main deployment script
│   ├── sync              # Sync configurations
│   ├── check             # Health checks
│   └── helpers.sh        # Common functions
├── 📁 macos-api/         # macOS API source code
│   ├── macos_api/        # API implementation
│   ├── requirements.txt  # Python dependencies
│   └── main.py           # Entry point
├── 📁 server/            # Server-side execution (optional)
│   ├── api/              # REST API endpoints
│   ├── jobs/             # Job management
│   └── client/           # Python client
└── 📁 docs/              # Documentation
    ├── server-api.md     # API documentation
    └── PERFORMANCE_AUDIT.md # Performance analysis
```

## 🚀 Quick Start

### Prerequisites

1. **Ansible Installed**: Ensure Ansible Core is installed
2. **Vault Password**: Set up vault password file for encrypted variables
3. **SSH Access**: Configure SSH keys for target devices
4. **Tailscale**: Devices should be connected to Tailscale network

### Essential Commands

```bash
# Deploy to specific environment with tags
./scripts/run spectra-preprod -t macos-api -l hostname

# Full deployment to environment
./scripts/run spectra-preprod

# Dry run to preview changes
./scripts/run spectra-preprod -t tracker --dry-run

# Deploy to production (requires confirmation)
./scripts/run spectra-prod -t player
```

### Component-Based Deployment

Deploy specific components using tags:

```bash
# Deploy macOS API service
./scripts/run spectra-preprod -t macos-api

# Deploy tracking system
./scripts/run spectra-preprod -t tracker

# Deploy video player
./scripts/run spectra-preprod -t player

# Deploy multiple components
./scripts/run spectra-preprod -t "macos-api,tracker"

# Infrastructure only
./scripts/run spectra-preprod -t "base,network,security"
```

### Direct Ansible Execution

```bash
# Universal playbook with platform auto-detection
ansible-playbook playbooks/universal.yml -i inventory/spectra-preprod.yml

# Deploy specific components via playbook
ansible-playbook playbooks/deploy-macos-api.yml -i inventory/spectra-preprod.yml

# macOS full deployment
ansible-playbook playbooks/macos-full.yml -i inventory/spectra-preprod.yml
```

## 📦 Available Components

### macOS Platform Tags

- **`macos-api`** / **`api`** - Device monitoring and management API
- **`tracker`** - AI tracking and analysis system (oaTracker)
- **`player`** - Video player for digital signage
- **`alpr`** - Automatic License Plate Recognition

### Infrastructure Tags

- **`base`** - Core system setup, shell configuration, cleanup
- **`network`** - Tailscale VPN, DNS configuration
- **`security`** - Firewall, TCC permissions, system hardening
- **`ssh`** - SSH configuration and key management

### Ubuntu Platform Tags

- **`docker`** - Docker environment setup (Ubuntu only)

## 🛠️ Management Scripts

### Core Scripts

- **`./scripts/run`** - Main deployment script with tag support
- **`./scripts/sync`** - Sync configurations and update remote files
- **`./scripts/check`** - Health checks and validation
- **`./scripts/reboot`** - Controlled device reboot operations
- **`./scripts/genSSH`** - SSH key generation and distribution

### Script Features

- **Interactive Mode**: Select inventory if not specified
- **Safety Checks**: Production confirmation required
- **Verbose Output**: Debug mode with `-v` flag
- **Dry Run Support**: Preview changes with `--dry-run`
- **Host Limiting**: Target specific devices with `-l hostname`

## 🌐 Environment Management

### Available Environments

- **`spectra-prod`** - Production Spectra devices
- **`spectra-preprod`** - Pre-production Spectra testing
- **`f1-prod`** - F1 project production
- **`f1-preprod`** - F1 project staging
- **`alpr-prod`** - ALPR production environment

### Inventory Structure

```yaml
# Example: spectra-preprod.yml
all:
  children:
    macos:
      hosts:
        spectra-ca-001:
          ansible_host: 100.x.x.x
          tailscale_hostname: spectra-ca-001
        spectra-ca-002:
          ansible_host: 100.x.x.x
          tailscale_hostname: spectra-ca-002
      vars:
        ansible_user: admin
        ansible_ssh_private_key_file: ~/.ssh/orangead_rsa
```

## 🔧 Execution Modes

### Dry-Run Mode

Preview changes without execution:

```bash
./scripts/run spectra-preprod -t macos-api --dry-run
```

### Check Mode

Validate configuration and show potential changes:

```bash
./scripts/run spectra-preprod -t tracker --check
```

### Force Mode

Skip safety checks and confirmations:

```bash
./scripts/run spectra-prod -t player --force
```

### Verbose Mode

Detailed output for debugging:

```bash
./scripts/run spectra-preprod -t network -v
```

## 🌐 Platform Support

### macOS (Mac Mini)

**Deployed Services:**

- **macOS API**: Device monitoring and management (`port 9090`)
- **oaTracker**: AI tracking system (`port 8080`)
- **Video Player**: Digital signage player

**System Management:**

- **LaunchAgent Services**: User-level service management
- **Python Runtime**: pyenv-managed Python installations
- **Tailscale**: VPN connectivity and device discovery
- **TCC Permissions**: Camera and automation access
- **Security**: Firewall and system hardening

### Ubuntu (Server)

**Deployed Services:**

- **Docker Environment**: Container runtime setup
- **System Monitoring**: Health checks and performance

**System Management:**

- **SystemD Services**: System-level service management
- **Network Configuration**: Tailscale and firewall (ufw)
- **Runtime Management**: Python and Node.js environments

## 🔒 Security & Configuration

### Security Features

- **Tailscale Network**: All devices connected via secure VPN
- **SSH Key Management**: Automated key distribution and rotation
- **Vault Encryption**: Sensitive data encrypted with Ansible Vault
- **TCC Permissions**: Automated macOS privacy permissions
- **Firewall Configuration**: Platform-specific firewall rules

### Configuration Management

```bash
# Vault password file (required)
echo "your-vault-password" > vault_password_file

# Ansible configuration
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_VAULT_PASSWORD_FILE=vault_password_file

# SSH configuration
ssh-keygen -t rsa -b 4096 -f ~/.ssh/orangead_rsa
```

### Environment Variables

```bash
# Deployment configuration
export OA_ANSIBLE_INVENTORY_DIR="./inventory"
export ANSIBLE_CONFIG="./ansible.cfg"

# Tailscale configuration (in vault)
tailscale_auth_key: "tskey-auth-xxxx"
tailscale_hostname: "device-name"
```

## 🛠️ Development & Testing

### Testing Deployments

```bash
# Dry-run deployment to test changes
./scripts/run spectra-preprod -t macos-api --dry-run

# Check mode for validation
./scripts/run spectra-preprod -t tracker --check

# Verbose output for debugging
./scripts/run spectra-preprod -t network -v
```

### Development Workflow

1. **Test Changes**: Use `--dry-run` to preview changes
2. **Validate Configuration**: Use `--check` mode for syntax validation
3. **Target Single Host**: Use `-l hostname` for focused testing
4. **Monitor Output**: Use `-v` for detailed logging

### Common Development Tasks

```bash
# Format Ansible files
./scripts/format

# Check Ansible syntax
./scripts/check

# Generate SSH keys for new environment
./scripts/genSSH

# Sync configuration files
./scripts/sync
```

## 📈 Performance & Best Practices

### Performance Features

- **Idempotent Operations**: Safe to run multiple times without side effects
- **Fact Caching**: Reduced gather time on subsequent runs
- **Tag-Based Deployment**: Deploy only what's needed
- **Parallel Execution**: Multiple hosts deployed simultaneously

### Best Practices

1. **Use Tags**: Deploy specific components instead of full stack
2. **Test First**: Always use `--dry-run` for production changes
3. **Limit Scope**: Use `-l hostname` for targeted deployments
4. **Monitor Progress**: Use verbose mode (`-v`) for troubleshooting
5. **Vault Security**: Keep sensitive data in encrypted vault files

## 🤝 Contributing

### Development Guidelines

1. **Test Changes**: Always use `--dry-run` before applying changes
2. **Role Development**: Follow Ansible best practices for role structure
3. **Idempotency**: Ensure all tasks can be run multiple times safely
4. **Documentation**: Update README and role documentation for changes
5. **Security**: Use Ansible Vault for sensitive data

### Adding New Roles

```bash
# Create new role structure
mkdir -p roles/platform/new-role/{tasks,handlers,templates,defaults}

# Add role to appropriate playbook
# Update universal.yml or create specific playbook
```

### Testing Contributions

```bash
# Test role changes
./scripts/run spectra-preprod -t your-role --dry-run

# Validate syntax
./scripts/check

# Format code
./scripts/format
```

## 📚 Documentation

### Available Documentation

- **[Server API](docs/server-api.md)** - REST API documentation
- **[Performance Audit](docs/PERFORMANCE_AUDIT.md)** - Performance analysis and optimization

### Role Documentation

Each role includes its own README with:

- Purpose and functionality
- Variables and configuration options
- Dependencies and requirements
- Usage examples

### Quick Help

```bash
# Show script usage and examples
./scripts/run --help

# List available inventories and tags
./scripts/run
```

## 🎯 Use Cases

### Common Deployment Scenarios

1. **New Device Setup**: Deploy full stack to new Mac Mini
2. **Service Updates**: Update specific services like `macos-api`
3. **Security Hardening**: Apply security configurations
4. **Network Configuration**: Set up Tailscale and DNS
5. **Troubleshooting**: Deploy with verbose logging

### Integration with oaPangaea

- **oaDashboard**: Monitors deployed services and device health
- **opi-setup**: Complementary system for OrangePi devices
- **oaTracker**: AI tracking system deployed via oaAnsible

---

**oaAnsible** - Infrastructure Automation for OrangeAd Devices  
Part of the OrangeAd Pangaea Project
