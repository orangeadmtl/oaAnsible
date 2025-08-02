# Ubuntu One-Command Onboarding

## Overview

The Ubuntu onboarding system provides a streamlined, intelligent way to configure Ubuntu machines for OrangeAd infrastructure. With a single command, you can
transform a fresh Ubuntu installation into a fully configured server ready for production use.

## Features

### 🚀 One-Command Setup

- **Single command execution** - No complex configuration required
- **Intelligent detection** - Automatically skips already configured components
- **Progressive enhancement** - Builds from basic to advanced configurations
- **Safe operations** - Dry-run mode and comprehensive validation

### 📋 Server Profiles

#### Server (Default)

**Best for:** Production servers, web servers, application servers

```bash
Components: base + security + shell + optimization + network + tailscale + monitoring
```

#### ML Workstation

**Best for:** Machine learning training servers, GPU workstations

```bash
Components: server profile + python + nvidia + ml_workstation
```

#### Development

**Best for:** Development servers, CI/CD runners

```bash
Components: server profile + docker + development tools
```

#### Minimal

**Best for:** Lightweight deployments, containers, testing

```bash
Components: base + security only
```

### 🔧 What Gets Configured

#### Base System (All Profiles)

- ✅ Essential packages and utilities
- ✅ User account setup and permissions
- ✅ System updates and security patches
- ✅ Basic monitoring and logging

#### Security Hardening (All Profiles)

- ✅ Passwordless sudo configuration
- ✅ SSH key-based authentication
- ✅ UFW firewall setup and rules
- ✅ Fail2ban intrusion detection
- ✅ Security updates automation

#### Enhanced Shell (Server+)

- ✅ Zsh with Oh My Zsh framework
- ✅ Useful aliases and functions
- ✅ Bash compatibility maintained
- ✅ Enhanced command completion

#### System Optimization (Server+)

- ✅ Performance tuning for servers
- ✅ Ethernet stability fixes (RTL8111/8168)
- ✅ Memory and CPU optimization
- ✅ Network configuration improvements

#### Network & VPN (Server+)

- ✅ Tailscale VPN with subnet routing
- ✅ Dynamic DNS configuration
- ✅ Network monitoring tools
- ✅ Connectivity validation

#### ML Workstation Specific

- ✅ Python environment (PyEnv + UV)
- ✅ NVIDIA drivers and CUDA support
- ✅ ML frameworks (PyTorch, Ultralytics)
- ✅ oaSentinel ML pipeline integration
- ✅ Jupyter Lab for development
- ✅ GPU monitoring tools

## Usage

### Command Line Interface

#### Direct Script Usage

```bash
# Interactive mode - guided setup
./scripts/onboard-ubuntu

# Direct IP onboarding with server profile
./scripts/onboard-ubuntu 192.168.1.100

# ML workstation setup
./scripts/onboard-ubuntu 192.168.1.100 --profile ml

# Development server with preview
./scripts/onboard-ubuntu server-01 --profile development --dry-run

# Automated setup (non-interactive)
./scripts/onboard-ubuntu 192.168.1.100 --profile server --force
```

#### Via Pangaea CLI

```bash
# Interactive mode
./pangaea.sh onboard ubuntu

# Direct setup
./pangaea.sh onboard ubuntu 192.168.1.100 --profile ml

# Preview changes
./pangaea.sh onboard ubuntu --dry-run
```

### Options

| Option             | Description                                       | Example            |
| ------------------ | ------------------------------------------------- | ------------------ |
| `--profile`        | Server profile (server, ml, development, minimal) | `--profile ml`     |
| `--dry-run`        | Preview changes without executing                 | `--dry-run`        |
| `--force`          | Skip confirmations and safety checks              | `--force`          |
| `--no-interactive` | Non-interactive mode (use defaults)               | `--no-interactive` |
| `--skip-preflight` | Skip pre-flight system checks                     | `--skip-preflight` |
| `-v, --verbose`    | Verbose output for debugging                      | `--verbose`        |

## Pre-requisites

### Target System Requirements

- **OS:** Ubuntu 18.04+ (20.04, 22.04, 24.04 tested)
- **Architecture:** x86_64 (amd64)
- **Memory:** Minimum 1GB (2GB+ recommended)
- **Storage:** 20GB+ available space
- **Network:** Internet connectivity for package downloads

### Access Requirements

- **SSH Access:** Key-based authentication preferred
- **Sudo Access:** User must have sudo privileges
- **Connectivity:** SSH port (22) accessible from control machine

### Control Machine Requirements

- **Ansible:** Version 2.9+ installed
- **Python:** 3.8+ with required modules
- **SSH Client:** OpenSSH client
- **Tools:** yq (YAML processor)

## Pre-flight Checks

The onboarding script performs comprehensive pre-flight validation:

### Connectivity Tests

- ✅ SSH connection to target host
- ✅ Authentication verification
- ✅ Sudo access validation
- ✅ Network connectivity check

### System Validation

- ✅ Ubuntu OS detection and version check
- ✅ Architecture compatibility (x86_64)
- ✅ Available disk space verification
- ✅ Memory and CPU core detection

### Profile-Specific Checks

- ✅ **ML Profile:** NVIDIA GPU detection
- ✅ **Development:** Docker compatibility check
- ✅ **Server:** Network interface validation

## Examples

### Basic Server Setup

```bash
# Set up a production web server
./scripts/onboard-ubuntu web-server-01 --profile server

# What gets configured:
# - Base system with security hardening
# - Enhanced shell (zsh) with useful aliases
# - System optimization and ethernet fixes
# - Tailscale VPN with subnet routing
# - Monitoring and logging tools
```

### ML Workstation Setup

```bash
# Set up an ML training server with GPU support
./scripts/onboard-ubuntu gpu-server-01 --profile ml

# What gets configured:
# - Everything from server profile
# - Python development environment (PyEnv + UV)
# - NVIDIA drivers and CUDA toolkit
# - ML frameworks (PyTorch with GPU support)
# - oaSentinel ML pipeline
# - Jupyter Lab for development
# - GPU monitoring tools
```

### Development Server

```bash
# Set up a development/CI server
./scripts/onboard-ubuntu dev-server-01 --profile development

# What gets configured:
# - Everything from server profile
# - Docker container runtime
# - Development tools and utilities
# - Additional monitoring for containers
```

## Post-Installation

### Verification

After successful onboarding, verify the setup:

```bash
# SSH to the configured server
ssh username@target-host

# Check installed components
systemctl status tailscaled  # Tailscale VPN
sudo ufw status              # Firewall status
docker --version             # Docker (development profile)
nvidia-smi                   # GPU status (ML profile)
```

### Generated Documentation

The script generates a detailed onboarding report:

- **Location:** `/tmp/ubuntu-onboarding-<hostname>-<timestamp>.md`
- **Contents:** Configuration summary, access information, next steps

### Next Steps

1. **Reboot if required** (the script will notify you)
2. **Add to permanent inventory** if not already present
3. **Configure application-specific settings**
4. **Set up monitoring alerts** as needed
5. **Test all configured services**

## Troubleshooting

### Common Issues

#### SSH Connection Failures

```bash
# Check SSH key configuration
ssh-add -l

# Test manual connection
ssh -v username@target-host

# Verify SSH service on target
systemctl status ssh
```

#### Sudo Permission Errors

```bash
# Test sudo access
ssh target-host "sudo -n true"

# Configure passwordless sudo (on target)
echo "username ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/username
```

#### PyEnv Installation Issues (ML Profile)

The script includes fixes for common PyEnv installation problems:

- User environment variable issues
- Permission problems with home directory
- Shell profile configuration conflicts

#### Network Connectivity Problems

```bash
# Check network interfaces
ip addr show

# Test DNS resolution
nslookup google.com

# Verify firewall rules
sudo ufw status verbose
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
./scripts/onboard-ubuntu target-host --verbose
```

### Recovery

If onboarding fails:

1. **Review the error logs** displayed during execution
2. **Check the generated report** for detailed status
3. **Run in dry-run mode** to identify issues
4. **Fix the identified problems** manually if needed
5. **Re-run the script** (it's idempotent and safe)

## Integration

### With oaDashboard

Onboarded Ubuntu machines automatically appear in oaDashboard when:

- Tailscale is configured (server+ profiles)
- Proper tags are applied (`tag:oa-ubuntu`)
- The machine is connected to the OrangeAd network

### With Existing Infrastructure

The onboarding process:

- **Preserves existing configurations** when possible
- **Skips already-configured components** intelligently
- **Integrates with existing Tailscale networks**
- **Maintains compatibility** with manual configurations

### With CI/CD Pipelines

For automated deployments:

```bash
# Non-interactive, automated setup
./scripts/onboard-ubuntu $TARGET_HOST --profile server --force --no-interactive
```

## Security Considerations

### Access Control

- **SSH Key Authentication:** Preferred over passwords
- **Sudo Access:** Minimal necessary permissions
- **Firewall Configuration:** Default-deny with specific allow rules
- **VPN Integration:** All external access via Tailscale

### Network Security

- **Tailscale VPN:** Encrypted mesh networking
- **Subnet Routing:** Secure access to local resources
- **UFW Firewall:** Host-based firewall protection
- **Fail2ban:** Intrusion detection and prevention

### Updates and Patches

- **Automatic Security Updates:** Enabled by default
- **Package Source Verification:** GPG signature checking
- **Minimal Attack Surface:** Only required packages installed

## Contributing

To extend the Ubuntu onboarding system:

1. **Add new profiles** in the `get_profile_components()` function
2. **Create additional roles** in `roles/ubuntu/`
3. **Update the playbook** to include new components
4. **Test thoroughly** with the `--dry-run` option
5. **Update documentation** to reflect changes

---

**🎉 Your Ubuntu machines are now ready for OrangeAd operations!**
