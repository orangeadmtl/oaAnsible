# oaAnsible - Infrastructure Automation System

Complete infrastructure automation solution for deploying and managing OrangeAd services across Mac Mini and Ubuntu platforms using Ansible. Provides automated deployment of device monitoring APIs, AI tracking systems, and security configurations.

## 🎯 Overview

**Platform:** Ansible-based infrastructure as code for Mac Mini and Ubuntu devices  
**Primary Services:** `macos-api` device monitoring, `oaTracker` AI tracking system  
**Features:** Multi-environment deployment, security management, service orchestration, idempotent operations

### Key Capabilities
- **Multi-Platform Support**: macOS (Mac Mini) and Ubuntu (OrangePi) deployment
- **Service Management**: Automated deployment of monitoring APIs and AI tracking
- **Security Configuration**: TCC permissions, firewall setup, certificate management
- **Network Setup**: Tailscale VPN configuration and hostname management
- **Environment Management**: Production, preprod, and development environments

## 🚀 Quick Start

### Prerequisites

- **Ansible Controller Machine** (macOS or Linux):
  - Python 3.12+ with `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Ansible Core 2.15+: `pip install ansible-core`
  - SSH client and keys configured
  - Tailscale account and auth keys

- **Target Mac Mini Devices**:
  - macOS 13+ (Ventura or later)
  - SSH enabled with passwordless sudo for deployment user
  - Network connectivity to controller

### Installation

1. **Clone and Setup:**
   ```bash
   git clone https://github.com/oa-device/oaAnsible.git
   cd oaAnsible
   
   # Create Python virtual environment
   uv venv
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

2. **Configure Ansible Vault:**
   ```bash
   # Create vault password file (secure location)
   echo "your-vault-password" > ~/.ansible_vault_pass
   chmod 600 ~/.ansible_vault_pass
   
   # Edit vault variables
   ansible-vault edit inventory/group_vars/all/vault.yml
   ```

3. **Generate SSH Keys:**
   ```bash
   ./scripts/genSSH
   # Follow prompts to generate and distribute SSH keys
   ```

4. **Deploy to Environment:**
   ```bash
   # Deploy API service to preprod environment
   ./scripts/run spectra-preprod -t macos-api
   
   # Deploy AI tracking system
   ./scripts/run spectra-preprod -t tracker
   
   # Full deployment (all components)
   ./scripts/run spectra-preprod
   ```

## ⚙️ Configuration

### Environment Structure

The system supports multiple environments with independent configurations:

```
inventory/
├── environments/
│   ├── spectra-prod/          # Production Spectra devices
│   ├── spectra-preprod/       # Preprod Spectra devices
│   ├── f1-prod/               # Production F1 devices
│   ├── f1-preprod/            # Preprod F1 devices
│   └── alpr-prod/             # Production ALPR devices
├── group_vars/
│   ├── all/                   # Global configuration
│   │   ├── main.yml          # Main variables
│   │   └── vault.yml         # Encrypted secrets
│   ├── macos/                 # macOS-specific variables
│   └── ubuntu/                # Ubuntu-specific variables
└── host_vars/                 # Per-host configuration
```

### Vault Configuration

Configure encrypted secrets in `inventory/group_vars/all/vault.yml`:

```yaml
# Ansible Vault encrypted file
vault_tailscale_auth_key: "tskey-auth-xxxxxxxxxxxxxxxxxxxxxxxxx"
vault_ssh_private_key: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  your-ssh-private-key-content
  -----END OPENSSH PRIVATE KEY-----

vault_api_keys:
  production: "prod-api-key-here"
  preprod: "preprod-api-key-here"

vault_certificates:
  ca_cert: |
    -----BEGIN CERTIFICATE-----
    your-ca-certificate
    -----END CERTIFICATE-----
```

### Host Inventory

Define target hosts in environment-specific inventory files:

```yaml
# inventory/environments/spectra-preprod/hosts.yml
all:
  children:
    macos:
      hosts:
        mac-mini-001:
          ansible_host: 192.168.1.10
          ansible_user: admin
          device_location: "California Office"
          device_series: "ARQ"
        mac-mini-002:
          ansible_host: 192.168.1.11
          ansible_user: admin
          device_location: "California Office"
          device_series: "ARQ"
    ubuntu:
      hosts:
        orangepi-001:
          ansible_host: 192.168.1.20
          ansible_user: ubuntu
          device_location: "Remote Site"
```

## 🏗️ Architecture and Roles

### Platform-Specific Roles

#### macOS Roles (`roles/macos/`)

1. **`macos_base`** - Core system setup
   - Homebrew installation and package management
   - System preferences and optimization
   - User account configuration
   - Directory structure creation

2. **`macos_python`** - Python environment management
   - `pyenv` installation for Python version management
   - Virtual environment setup for applications
   - Package installation via `uv`

3. **`macos_node`** - Node.js environment setup
   - `nvm` installation for Node version management
   - `bun` installation for fast package management
   - Development tool configuration

4. **`macos_network`** - Network and VPN configuration
   - Tailscale installation from source (`go install`)
   - VPN authentication and hostname setup
   - DNS configuration and firewall rules

5. **`macos_security`** - Security and permissions
   - TCC database modifications for camera access
   - Firewall configuration and port management
   - Certificate installation and trust setup

6. **`macos_settings`** - System settings and automation
   - LaunchDaemon configuration for system services
   - Daily reboot scheduling
   - Log rotation and maintenance tasks

7. **`macos_api`** - Device monitoring API deployment
   - FastAPI application deployment
   - Service configuration as LaunchAgent
   - Health monitoring endpoint setup
   - Integration with device hardware APIs

8. **`macos_tracker`** - AI tracking system deployment
   - `oaTracker` application deployment
   - Camera access configuration
   - AI model and configuration management
   - MJPEG streaming service setup

#### Ubuntu Roles (`roles/ubuntu/`)

1. **`ubuntu_base`** - Base system configuration
   - Package management and updates
   - User account and permissions setup
   - System optimization for embedded devices

2. **`ubuntu_network`** - Network configuration
   - Tailscale installation and setup
   - WiFi and ethernet configuration
   - Firewall and security settings

3. **`ubuntu_services`** - Service deployment
   - SystemD service configuration
   - Log management and rotation
   - Health monitoring setup

#### Common Roles (`roles/common/`)

1. **`common_facts`** - System information gathering
2. **`common_logging`** - Centralized logging configuration
3. **`common_monitoring`** - Health check setup

### Deployment Tags

Control deployment scope with Ansible tags:

- **`base`** - Core system setup and dependencies
- **`network`** - Tailscale VPN and network configuration
- **`security`** - Security policies and permissions
- **`python`** - Python environment and dependencies
- **`node`** - Node.js environment setup
- **`macos-api`** - Device monitoring API service
- **`tracker`** - AI tracking system deployment
- **`settings`** - System preferences and automation

## 🛠️ Development and Management

### Script Utilities

The `scripts/` directory provides management utilities:

#### Core Scripts

```bash
# Deployment script
./scripts/run <environment> [options]
  --tags/-t <tags>     # Specific components to deploy
  --dry-run           # Preview changes without execution
  --verbose/-v        # Detailed output
  --check             # Run in check mode
  --diff              # Show configuration differences

# Syntax validation
./scripts/check
  # Validates playbook syntax and inventory

# Configuration synchronization
./scripts/sync
  # Updates inventory from external sources

# SSH key management
./scripts/genSSH
  # Interactive SSH key generation and distribution
```

#### Usage Examples

```bash
# Deploy API service to production
./scripts/run spectra-prod -t macos-api

# Deploy tracker with verbose output
./scripts/run spectra-preprod -t tracker -v

# Preview full deployment
./scripts/run f1-preprod --dry-run

# Deploy only base system and network
./scripts/run spectra-preprod -t base,network

# Check configuration without changes
./scripts/run spectra-preprod --check --diff
```

### Playbook Structure

Main deployment playbooks in `playbooks/`:

- **`site.yml`** - Main entry point for all deployments
- **`macos.yml`** - macOS-specific deployment tasks
- **`ubuntu.yml`** - Ubuntu-specific deployment tasks
- **`common.yml`** - Cross-platform common tasks

### Development Workflow

1. **Local Testing:**
   ```bash
   # Validate syntax
   ansible-playbook --syntax-check playbooks/site.yml
   
   # Test against single host
   ./scripts/run spectra-preprod --limit mac-mini-001 --check
   
   # Deploy to preprod first
   ./scripts/run spectra-preprod -t macos-api
   ```

2. **Production Deployment:**
   ```bash
   # Final validation
   ./scripts/check
   
   # Preview production changes
   ./scripts/run spectra-prod --dry-run
   
   # Deploy to production
   ./scripts/run spectra-prod
   ```

3. **Rollback Procedures:**
   ```bash
   # Service-level rollback
   ansible-playbook playbooks/rollback.yml -e target_service=macos-api
   
   # Full system rollback
   ansible-playbook playbooks/restore.yml -e backup_date=2024-01-15
   ```

## 📡 Service Deployment Details

### macOS API Service (`macos-api`)

**Purpose:** Device health monitoring and management API for Mac Mini devices

**Deployment Details:**
- **Installation Path:** `{{ ansible_user_dir }}/orangead/macos-api/`
- **Service Type:** User LaunchAgent (`com.orangead.macosapi.plist`)
- **Port:** 9090 (configurable)
- **Dependencies:** Python 3.12+, FastAPI, psutil, opencv-python-headless

**Configuration:**
```yaml
# Ansible variables for API deployment
macos_api_config:
  port: 9090
  log_level: "INFO"
  health_check_interval: 30
  api_timeout: 10
  enable_camera_proxy: true
```

**Service Management:**
```bash
# Check service status
launchctl list | grep com.orangead.macosapi

# Start/stop service
launchctl load ~/Library/LaunchAgents/com.orangead.macosapi.plist
launchctl unload ~/Library/LaunchAgents/com.orangead.macosapi.plist

# View logs
tail -f ~/orangead/macos-api/logs/api.log
```

### AI Tracking System (`oaTracker`)

**Purpose:** Real-time object detection and tracking for Mac Mini devices

**Deployment Details:**
- **Installation Path:** `{{ ansible_user_dir }}/orangead/tracker/`
- **Service Type:** User LaunchAgent (`com.orangead.tracker.plist`)
- **Port:** 8080 (configurable)
- **Dependencies:** Python 3.12+, Ultralytics YOLO, OpenCV, FastAPI

**Configuration:**
```yaml
# Ansible variables for tracker deployment
tracker_config:
  port: 8080
  camera_index: 0
  model_version: "yolov8n.pt"
  confidence_threshold: 0.5
  tracking_enabled: true
  stream_fps: 30
```

**Camera Permissions:**
The role automatically configures camera access by modifying the TCC database:
```bash
# Manual TCC database modification (handled by Ansible)
sudo sqlite3 "/Users/$USER/Library/Application Support/com.apple.TCC/TCC.db" \
  "INSERT OR REPLACE INTO access VALUES('kTCCServiceCamera','python3',0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1541440109);"
```

## 🔧 Advanced Configuration

### Custom Variables

Override default configurations in `inventory/group_vars/` or `inventory/host_vars/`:

```yaml
# Custom API configuration
macos_api_custom:
  port: 9091
  workers: 2
  timeout: 15
  custom_endpoints:
    - "/custom/health"
    - "/custom/metrics"

# Custom tracker configuration
tracker_custom:
  camera_resolution: "1920x1080"
  detection_zones:
    - name: "entrance"
      coordinates: [[100,100], [500,100], [500,400], [100,400]]
  alert_webhooks:
    - "https://alerts.example.com/webhook"

# Custom system settings
system_custom:
  daily_reboot_enabled: false
  log_retention_days: 14
  firewall_strict_mode: true
```

### Environment-Specific Overrides

Create environment-specific configurations:

```yaml
# inventory/environments/spectra-prod/group_vars/all/main.yml
environment: "production"
log_level: "WARNING"
debug_mode: false
metrics_collection: true
alert_webhooks_enabled: true

# inventory/environments/spectra-preprod/group_vars/all/main.yml
environment: "preprod"
log_level: "DEBUG"
debug_mode: true
metrics_collection: false
alert_webhooks_enabled: false
```

### Custom Roles Development

Create custom roles in `roles/custom/`:

```yaml
# roles/custom/my_role/tasks/main.yml
---
- name: Custom configuration task
  ansible.builtin.template:
    src: custom_config.j2
    dest: "{{ ansible_user_dir }}/custom/config.yml"
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0644'
  notify: restart custom service

- name: Install custom dependencies
  ansible.builtin.pip:
    name:
      - custom-package-1
      - custom-package-2
    virtualenv: "{{ ansible_user_dir }}/custom/.venv"
```

## 🔒 Security and Compliance

### Vault Management

**Creating Encrypted Variables:**
```bash
# Create new vault file
ansible-vault create inventory/group_vars/production/vault.yml

# Edit existing vault
ansible-vault edit inventory/group_vars/all/vault.yml

# Encrypt string for inline use
ansible-vault encrypt_string 'secret-value' --name 'vault_variable_name'

# Decrypt for viewing
ansible-vault decrypt inventory/group_vars/all/vault.yml --output=-
```

**Vault Password Management:**
```bash
# Store vault password securely
echo "your-vault-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass

# Use in ansible commands
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
```

### SSH Key Security

**Key Generation and Distribution:**
```bash
# Generate deployment key pair
ssh-keygen -t ed25519 -f ~/.ssh/orangead_deploy -C "orangead-deploy@$(hostname)"

# Distribute public key to targets
ssh-copy-id -i ~/.ssh/orangead_deploy.pub admin@mac-mini-001

# Configure SSH client
cat >> ~/.ssh/config << EOF
Host mac-mini-*
    User admin
    IdentityFile ~/.ssh/orangead_deploy
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
```

### TCC Database Security

The system automatically configures macOS privacy permissions:

```yaml
# Roles handle TCC permissions for camera access
- name: Grant camera access to tracker
  ansible.builtin.shell: |
    sqlite3 "{{ ansible_user_dir }}/Library/Application Support/com.apple.TCC/TCC.db" \
    "INSERT OR REPLACE INTO access VALUES(
      'kTCCServiceCamera',
      '{{ tracker_python_path }}',
      0, 1, 1, NULL, NULL, NULL, 'UNUSED', NULL, 0, 1541440109
    );"
  become: true
  become_user: "{{ ansible_user }}"
```

## 📊 Monitoring and Observability

### Deployment Monitoring

**Ansible Logging:**
```bash
# Enable detailed logging
export ANSIBLE_LOG_PATH=./ansible.log
export ANSIBLE_DEBUG=1

# Custom log format
export ANSIBLE_STDOUT_CALLBACK=yaml
export ANSIBLE_DISPLAY_SKIPPED_HOSTS=false
```

**Service Health Monitoring:**
```bash
# Check deployed services
ansible all -m shell -a "launchctl list | grep com.orangead"

# Test API endpoints
ansible macos -m uri -a "url=http://localhost:9090/health method=GET"

# Check system resources
ansible all -m setup -a "filter=ansible_memory_mb"
```

### Performance Metrics

**Deployment Performance:**
```bash
# Time deployment execution
time ./scripts/run spectra-preprod -t macos-api

# Profile ansible execution
ansible-playbook playbooks/site.yml --profile

# Check task timing
ansible-playbook playbooks/site.yml -vvv | grep "TASK\|PLAY RECAP"
```

**System Resource Monitoring:**
```yaml
# Add to playbook for resource monitoring
- name: Collect system metrics
  ansible.builtin.setup:
    filter:
      - ansible_memory_mb
      - ansible_processor_count
      - ansible_mounts
  register: system_metrics

- name: Log resource usage
  ansible.builtin.debug:
    msg: |
      Memory: {{ system_metrics.ansible_facts.ansible_memory_mb.real.total }}MB
      CPU: {{ system_metrics.ansible_facts.ansible_processor_count }} cores
      Disk: {{ system_metrics.ansible_facts.ansible_mounts[0].size_available }}
```

## 🚨 Troubleshooting

### Common Deployment Issues

#### Connection Problems
```bash
# Test SSH connectivity
ansible all -m ping

# Check SSH configuration
ssh -vvv admin@mac-mini-001

# Verify inventory syntax
ansible-inventory --list

# Test with specific user
ansible all -m ping -u admin --ask-pass
```

#### Permission Issues
```bash
# Check sudo access
ansible all -m shell -a "sudo -l" --ask-become-pass

# Verify file permissions
ansible all -m file -a "path=/Users/admin/orangead state=directory" --check

# Test privilege escalation
ansible all -m setup --become --ask-become-pass
```

#### Service Deployment Failures
```bash
# Check service status
ansible macos -m shell -a "launchctl list | grep com.orangead"

# View service logs
ansible macos -m fetch -a "src=~/orangead/macos-api/logs/api.log dest=./logs/"

# Restart failed services
ansible macos -m shell -a "launchctl kickstart -k gui/$(id -u)/com.orangead.macosapi"
```

### Debugging Playbooks

**Verbose Execution:**
```bash
# Increasing verbosity levels
./scripts/run spectra-preprod -v      # Basic verbose
./scripts/run spectra-preprod -vv     # More verbose
./scripts/run spectra-preprod -vvv    # Connection debugging
./scripts/run spectra-preprod -vvvv   # Everything
```

**Step-by-Step Debugging:**
```bash
# Start at specific task
ansible-playbook playbooks/site.yml --start-at-task="Install Python dependencies"

# Step through tasks
ansible-playbook playbooks/site.yml --step

# Run specific tags only
ansible-playbook playbooks/site.yml --tags="debug,logging"
```

**Variable Debugging:**
```yaml
# Add debug tasks to playbooks
- name: Debug all variables
  ansible.builtin.debug:
    var: hostvars[inventory_hostname]

- name: Debug specific variable
  ansible.builtin.debug:
    msg: "API port is {{ macos_api_port }}"
```

### Recovery Procedures

#### Service Recovery
```bash
# Stop all services
ansible macos -m shell -a "launchctl unload ~/Library/LaunchAgents/com.orangead.*.plist"

# Clear application data
ansible macos -m file -a "path=~/orangead state=absent"

# Redeploy from scratch
./scripts/run spectra-preprod --tags=macos-api,tracker
```

#### System Recovery
```bash
# Reset TCC permissions
ansible macos -m shell -a "tccutil reset Camera" --become

# Restore from backup
ansible-playbook playbooks/restore.yml -e backup_date=2024-01-15

# Emergency system reset
ansible macos -m shell -a "sudo shutdown -r now" --become
```

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks

**Weekly Maintenance:**
```bash
#!/bin/bash
# scripts/weekly_maintenance.sh

# Update system packages
ansible all -m package -a "name=* state=latest" --become

# Check service health
ansible all -m service_facts

# Rotate logs
ansible all -m shell -a "find ~/orangead -name '*.log' -mtime +7 -delete"

# Update dependency versions
ansible-playbook playbooks/update_dependencies.yml
```

**Monthly Security Updates:**
```bash
# Update vault passwords
ansible-vault rekey inventory/group_vars/all/vault.yml

# Rotate SSH keys
./scripts/genSSH --rotate

# Update TLS certificates
ansible-playbook playbooks/update_certificates.yml
```

### Version Management

**Track Deployed Versions:**
```yaml
# Store version information
- name: Record deployment version
  ansible.builtin.lineinfile:
    path: "{{ ansible_user_dir }}/orangead/.version"
    line: "{{ ansible_date_time.iso8601 }}: {{ macos_api_version }}"
    create: yes

- name: Create deployment manifest
  ansible.builtin.template:
    src: deployment_manifest.j2
    dest: "{{ ansible_user_dir }}/orangead/manifest.json"
```

**Rollback Procedures:**
```bash
# List available versions
ansible macos -m shell -a "cat ~/orangead/.version"

# Rollback to previous version
ansible-playbook playbooks/rollback.yml -e "target_version=v2.1.0"

# Emergency rollback
ansible-playbook playbooks/emergency_rollback.yml
```

## 📚 Advanced Topics

### Multi-Environment Management

**Environment Switching:**
```bash
# Deploy to multiple environments
for env in spectra-prod spectra-preprod f1-prod; do
    ./scripts/run $env --tags=macos-api --check
done

# Parallel deployment
ansible-playbook playbooks/site.yml -f 10  # 10 parallel connections
```

**Configuration Drift Detection:**
```bash
# Check for configuration drift
ansible-playbook playbooks/site.yml --check --diff

# Generate drift report
ansible all -m setup --tree ./reports/

# Compare configurations
diff -r inventory/environments/spectra-prod/ inventory/environments/spectra-preprod/
```

### Custom Module Development

Create custom Ansible modules in `library/`:

```python
#!/usr/bin/env python3
# library/orangead_health.py

from ansible.module_utils.basic import AnsibleModule
import requests

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            port=dict(required=False, type='int', default=9090),
            timeout=dict(required=False, type='int', default=10)
        )
    )
    
    try:
        response = requests.get(
            f"http://{module.params['host']}:{module.params['port']}/health",
            timeout=module.params['timeout']
        )
        
        module.exit_json(
            changed=False,
            health_data=response.json(),
            status_code=response.status_code
        )
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
```

### Integration Patterns

**CI/CD Integration:**
```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure
on:
  push:
    branches: [main]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Ansible
        run: |
          pip install ansible-core
          echo "${{ secrets.VAULT_PASSWORD }}" > .vault_pass
      - name: Deploy to preprod
        run: ./scripts/run spectra-preprod --vault-password-file .vault_pass
      - name: Run tests
        run: ansible-playbook playbooks/test.yml
```

This comprehensive infrastructure automation system provides robust, scalable deployment capabilities for the OrangeAd device ecosystem with full security, monitoring, and maintenance features.
