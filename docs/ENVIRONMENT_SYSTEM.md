# OrangeAd Ansible Environment System

## Overview

The OrangeAd Ansible setup uses a three-tier environment system with built-in safety controls:

- **Staging**: VM environment for experimental features
- **Pre-prod**: Real Mac Mini for final testing
- **Production**: Field devices requiring maximum safety

## Environment Configuration

Each environment is configured in `inventory/{env}/group_vars/all.yml`:

```yaml
oa_environment:
  name: "staging" # Environment identifier
  allow_experimental: true # Enable experimental features
  allow_server_optimizations: true # Enable UI minimization, auto-login
  allow_destructive_operations: true # Enable daily reboot, etc.
  allow_tailscale_changes: true # Enable Tailscale installation/config
```

## Environment Variables Reference

### `oa_environment.name`

- **Values**: `"staging"`, `"pre-prod"`, `"production"`
- **Usage**: Identifies the current environment for safety checks and logging

### `oa_environment.allow_experimental`

- **Purpose**: Controls access to experimental/unstable features
- **Staging**: `true` (safe to experiment)
- **Pre-prod**: `false` (stable features only)
- **Production**: `false` (stable features only)

### `oa_environment.allow_server_optimizations`

- **Purpose**: Controls the `macos/server_optimizations` role
- **Features Controlled**:
  - Auto-login configuration
  - UI minimization (dock, animations, etc.)
  - System service optimizations
- **Staging**: `true` (test all optimizations)
- **Pre-prod**: `true` (validate optimizations on real hardware)
- **Production**: `false` (keep standard macOS experience)

### `oa_environment.allow_destructive_operations`

- **Purpose**: Controls potentially disruptive operations
- **Features Controlled**:
  - Daily reboot scheduling
  - System-wide configuration changes
- **Staging**: `true` (VM can handle any changes)
- **Pre-prod**: `false` (avoid disrupting testing)
- **Production**: `false` (maximize uptime)

### `oa_environment.allow_tailscale_changes`

- **Purpose**: Controls Tailscale installation and configuration
- **Features Controlled**:
  - Tailscale binary installation
  - Tailscale daemon configuration
  - Network connectivity setup
- **Staging**: `true` (safe for testing)
- **Pre-prod**: `true` (needed for testing)
- **Production**: `false` (extra careful - requires explicit override)

## Using Environment Variables in Roles

### Role-Level Control

In `main.yml`, control entire roles:

```yaml
- role: macos/server_optimizations
  when: oa_environment.allow_server_optimizations | default(false)
```

### Task-Level Control

In role tasks, control specific operations:

```yaml
- name: Configure daily reboot
  block:
    # ... tasks ...
  when: oa_environment.allow_destructive_operations | default(true)
```

### Conditional Logic

Use environment name for specific logic:

```yaml
- name: Production-specific safety check
  debug:
    msg: "Extra careful in production!"
  when: oa_environment.name == "production"
```

## Running Deployments

### Using Helper Scripts

**Staging (VM)**:

```bash
./scripts/run-staging
```

**Pre-prod (Real Mac Mini)**:

```bash
./scripts/run-preprod
```

**Production (Field Devices)**:

```bash
./scripts/run-prod    # Includes safety prompts
./scripts/safe-run-prod  # Extra safety features
```

### Manual Runs

**Staging**:

```bash
ansible-playbook -i inventory/staging/hosts.yml main.yml --vault-password-file vault_password_file
```

**Pre-prod**:

```bash
ansible-playbook -i inventory/pre-prod/hosts.yml main.yml --vault-password-file vault_password_file
```

**Production** (with safety checks):

```bash
ansible-playbook -i inventory/production/hosts.yml main.yml --vault-password-file vault_password_file
# Will prompt for confirmation before proceeding
```

### Skip Safety Checks (Emergency Only)

```bash
ansible-playbook main.yml -i inventory/production/hosts.yml --extra-vars "skip_safety_checks=true"
```

### Production Tailscale Override (Use with Extreme Caution)

```bash
# Allow Tailscale changes in production (dangerous!)
ansible-playbook main.yml -i inventory/production/hosts.yml --tags tailscale --extra-vars "oa_environment.allow_tailscale_changes=true"

# Recommended: Check mode first
ansible-playbook main.yml -i inventory/production/hosts.yml --tags tailscale --extra-vars "oa_environment.allow_tailscale_changes=true" --check
```

## Safety Features

### Automatic Checks

- **Environment validation**: Ensures `oa_environment.name` is set
- **Production warnings**: Interactive prompts before production changes
- **Tailscale safety**: Warns about connectivity risks
- **Feature restrictions**: Prevents dangerous operations in production

### Interactive Prompts

Production deployments will prompt:

```text
⚠️  WARNING: You are about to run playbook on PRODUCTION environment!

Environment: production
Target hosts: f1-ca-001, f1-ca-002

This will affect live devices in the field.
Tailscale connectivity issues could require physical access to recover.

Are you absolutely sure you want to continue? (yes/no)
```

## Environment Summary

| Feature                | Staging | Pre-prod      | Production    |
| ---------------------- | ------- | ------------- | ------------- |
| Hardware               | VM      | Real Mac Mini | Field Devices |
| Experimental Features  | ✅      | ❌            | ❌            |
| Server Optimizations   | ✅      | ✅            | ❌            |
| Destructive Operations | ✅      | ❌            | ❌            |
| Tailscale Changes      | ✅      | ✅            | ❌\*          |
| Safety Prompts         | ❌      | ✅            | ✅            |

\*Production Tailscale requires explicit override

## Adding New Environment Controls

1. **Add new flag** to `oa_environment` in group_vars
2. **Use in role/task** with `when: oa_environment.your_flag | default(false)`
3. **Document** the new control in this file
4. **Test** across all environments

Example:

```yaml
# In group_vars/all.yml
oa_environment:
  allow_network_changes: false

# In role tasks
- name: Modify network settings
  # ... tasks ...
  when: oa_environment.allow_network_changes | default(true)
```
