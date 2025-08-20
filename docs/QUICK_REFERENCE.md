# oaAnsible Quick Reference

Fast reference for common commands, deployment patterns, and operational tasks using the modern oaAnsible system.

## 🚀 Essential Commands

### Primary Deployment

```bash
# Deploy services to project environment
./scripts/run projects/{project}/{env} -t {component}

# Examples
./scripts/run projects/f1/prod -t macos-api
./scripts/run projects/spectra/preprod -t tracker,security
```

### Maintenance Operations

```bash
# Stop services
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api

# Reboot hosts safely
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --extra-vars "confirm_reboot=yes"

# SSH key deployment (bootstrap)
./scripts/genSSH 192.168.1.100 admin
```

## 📁 Inventory Structure Quick Guide

### Project Paths

```bash
projects/f1/prod.yml           # F1 production
projects/f1/preprod.yml        # F1 pre-production
projects/spectra/prod.yml      # Spectra production  
projects/evenko/tracker-prod.yml # Evenko tracker-specific
projects/alpr/staging.yml      # ALPR staging
```

### Inventory File Format

```yaml
all:
  children:
    macos:
      hosts:
        hostname-001:
          ansible_host: 100.64.1.10
          ansible_user: admin
```

## 🏷️ Component Tags Reference

### Infrastructure Tags

| Tag | Purpose | Platforms |
|-----|---------|-----------|
| `base` | Core system setup, Homebrew, user config | macOS, Ubuntu |
| `network` | Tailscale VPN, DNS configuration | macOS, Ubuntu |
| `security` | TCC permissions, firewall, certificates | macOS, Ubuntu |
| `python` | Python environment, pyenv, packages | macOS |
| `node` | Node.js environment, nvm, bun | macOS |

### Service Tags  

| Tag | Purpose | Port | Platforms |
|-----|---------|------|-----------|
| `macos-api` | Device monitoring API | 9090 | macOS |
| `tracker` | AI tracking system | 8080 | macOS |
| `player` | Video player service | 3000 | macOS |
| `alpr` | License plate recognition | 8081 | macOS |
| `camguard` | Camera monitoring | Various | macOS |

### Platform-Specific Tags

| Tag | Purpose | Platforms |
|-----|---------|-----------|
| `ml` | ML workstation setup | Ubuntu |
| `nvidia` | GPU drivers and CUDA | Ubuntu |
| `docker` | Container runtime | Ubuntu |
| `oasentinel-setup` | AI training project setup | Ubuntu |

## 🛠️ Deployment Patterns

```bash
# Single component
./scripts/run projects/{project}/{env} -t {component}

# Multiple components
./scripts/run projects/{project}/{env} -t "component1,component2"

# Host limiting
./scripts/run projects/{project}/{env} -t {component} -l hostname

# Preview changes
./scripts/run projects/{project}/{env} --dry-run
./scripts/run projects/{project}/{env} --check --diff

# Verbose output
./scripts/run projects/{project}/{env} -t {component} -v
```

## 📊 Monitoring & Verification

### Service Health Checks

```bash
# Check all services
ansible all -i projects/f1/prod.yml -m shell -a "launchctl list | grep com.orangead"

# Test API endpoints
ansible macos -i projects/spectra/prod.yml -m uri -a "url=http://localhost:9090/health method=GET"

# Check specific service
curl http://localhost:8080/api/stats  # Tracker stats
curl http://localhost:9090/health     # API health
```

### System Verification

```bash
# Test connectivity
ansible all -i projects/f1/prod.yml -m ping

# Check system resources
ansible all -i projects/spectra/prod.yml -m setup -a "filter=ansible_memory_mb"

# Verify service processes
ansible macos -i projects/f1/prod.yml -m shell -a "pgrep -f 'macos-api|tracker'"
```

## 🔧 Common Operations

### Service Management

```bash
# macOS LaunchAgent services
launchctl list | grep com.orangead           # List all services
launchctl load ~/Library/LaunchAgents/com.orangead.macosapi.plist   # Start service
launchctl unload ~/Library/LaunchAgents/com.orangead.macosapi.plist # Stop service

# Ubuntu SystemD services  
systemctl --user list-units --type=service   # List services
systemctl --user start orangead-api          # Start service
systemctl --user stop orangead-api           # Stop service
```

### Log Management

```bash
# View service logs
tail -f ~/orangead/macos-api/logs/api.log    # API logs
tail -f ~/orangead/tracker/logs/tracker.log  # Tracker logs

# Fetch logs from remote hosts
ansible macos -i projects/f1/prod.yml -m fetch -a "src=~/orangead/macos-api/logs/api.log dest=./logs/"

# Log cleanup
ansible all -m shell -a "find ~/orangead -name '*.log' -mtime +7 -delete"
```

### Configuration Management  

```bash
# Edit vault secrets
ansible-vault edit inventory/group_vars/all/vault.yml

# View vault content (decrypt)
ansible-vault view inventory/group_vars/all/vault.yml

# Encrypt new secret
ansible-vault encrypt_string 'secret-value' --name 'vault_variable_name'
```

## 🛠️ Maintenance Playbooks

### Service Management

```bash
# Stop all services
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml

# Stop specific services
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags "api,tracker"

# Stop services on specific hosts
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --limit f1-ca-001
```

### Host Management

```bash
# Standard reboot with graceful shutdown
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --extra-vars "confirm_reboot=yes"

# Emergency reboot (skip graceful shutdown)
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --tags immediate --extra-vars "confirm_reboot=yes"

# Custom reboot timing
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --extra-vars "confirm_reboot=yes reboot_delay=120"
```

## 🔍 Troubleshooting Quick Commands

### Connection Issues

```bash
# Test SSH access
ssh admin@f1-ca-001

# Debug SSH issues
ssh -vvv admin@f1-ca-001

# Test with different user
ansible all -i projects/f1/prod.yml -m ping -u admin --ask-pass
```

### Permission Issues

```bash
# Check sudo access
ansible all -i projects/f1/prod.yml -m shell -a "sudo -l" --ask-become-pass

# Test privilege escalation
ansible all -i projects/f1/prod.yml -m setup --become --ask-become-pass

# Fix file permissions
ansible macos -i projects/f1/prod.yml -m file -a "path=~/orangead owner=admin mode=0755"
```

### Service Issues

```bash
# Restart failed services
ansible macos -i projects/f1/prod.yml -m shell -a "launchctl kickstart -k gui/\$(id -u)/com.orangead.macosapi"

# Check service status
ansible macos -i projects/f1/prod.yml -m shell -a "launchctl print gui/\$(id -u)/com.orangead.macosapi"

# Clear and restart
ansible macos -m shell -a "launchctl unload ~/Library/LaunchAgents/com.orangead.*.plist"
```

## 📝 Script Migration Reference

### Deprecated Scripts

| Old Command | Status | New Alternative |
|-------------|--------|-----------------|
| `./scripts/check` | ⚠️ Deprecated | `./scripts/run --check` |
| `./scripts/sync` | ⚠️ Deprecated | `./scripts/run` (interactive) |
| `./scripts/stop` | ⚠️ Deprecated | `playbooks/maintenance/stop_services.yml` |
| `./scripts/reboot` | ⚠️ Deprecated | `playbooks/maintenance/reboot_hosts.yml` |
| `./scripts/format` | ⚠️ Deprecated | `./pangaea.sh format oaAnsible` |

### Active Scripts

| Command | Purpose | Status |
|---------|---------|--------|
| `./scripts/run` | Primary deployment | ✅ Active |
| `./scripts/genSSH` | SSH key bootstrap | ✅ Active |

## 🔑 Vault Quick Reference

### Common Vault Operations

```bash
# Create new vault file
ansible-vault create new_vault.yml

# Edit existing vault  
ansible-vault edit inventory/group_vars/all/vault.yml

# Change vault password
ansible-vault rekey inventory/group_vars/all/vault.yml

# Decrypt file temporarily
ansible-vault decrypt vault.yml --output=-
```

### Vault Variables

```yaml
# Common vault variables
vault_tailscale_auth_key: "tskey-auth-xxxxx"
vault_ssh_private_key: "-----BEGIN OPENSSH PRIVATE KEY-----"
vault_api_keys:
  production: "prod-key"
  preprod: "preprod-key"
vault_sudo_passwords:
  default: "default-password"
  host-specific: "host-password"
```

## 🚨 Emergency Procedures

```bash
# Complete service restart
ansible-playbook -i projects/{project}/{env}.yml playbooks/maintenance/stop_services.yml
sleep 30
./scripts/run projects/{project}/{env} -t "macos-api,tracker"

# System recovery
ansible macos -i projects/{project}/{env}.yml -m file -a "path=~/orangead state=absent"
./scripts/run projects/{project}/{env} -t "base,macos-api,tracker"
```

### Emergency Host Access

```bash
# Direct SSH and emergency procedures
ssh admin@{host_ip}
launchctl unload ~/Library/LaunchAgents/com.orangead.*.plist
sudo shutdown -r now
```

---

💡 **Tips**: Always test with `--dry-run` first • Use `projects/` prefix • Production requires `YES` confirmation
