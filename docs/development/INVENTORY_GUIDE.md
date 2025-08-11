# oaAnsible Inventory Guide

Complete guide to the modern project-centric inventory structure and variable hierarchy system.

## 🎯 Overview

The oaAnsible inventory system has been completely refactored to use a **project-centric structure** that eliminates redundancy, centralizes configuration, and provides clear variable inheritance patterns.

## 📁 Directory Structure

```bash
inventory/
├── projects/                           # Project-based organization
│   ├── f1/                            # F1 project inventories
│   │   ├── prod.yml                   # Production environment
│   │   ├── preprod.yml                # Pre-production environment
│   │   └── staging.yml                # Staging environment
│   ├── spectra/                       # Spectra project inventories
│   │   ├── prod.yml, preprod.yml, staging.yml
│   ├── evenko/                        # Evenko project inventories
│   │   ├── prod.yml                   # General production
│   │   ├── tracker-prod.yml           # Tracker-specific production
│   │   ├── camguard-prod.yml          # Camguard-specific production
│   │   └── camguard-all-prod.yml      # All camguard hosts
│   └── alpr/                          # ALPR project inventories
│       ├── prod.yml, preprod.yml, staging.yml
├── group_vars/                        # Hierarchical variable inheritance
│   ├── all/                          # Global defaults
│   │   ├── ansible_connection.yml     # Connection settings
│   │   ├── runtime_versions.yml       # Software versions
│   │   ├── common_packages.yml        # Package lists
│   │   └── vault.yml                 # Encrypted secrets
│   ├── platforms/                     # Platform-specific variables
│   │   ├── macos.yml                 # macOS defaults
│   │   └── ubuntu.yml                # Ubuntu defaults
│   ├── environments/                  # Environment-specific variables
│   │   ├── production.yml            # Production settings
│   │   ├── preprod.yml               # Pre-production settings
│   │   └── staging.yml               # Staging settings
│   ├── f1_base.yml                   # F1 project base configuration
│   ├── spectra_base.yml              # Spectra project base configuration
│   ├── evenko_base.yml               # Evenko project base configuration
│   └── alpr_base.yml                 # ALPR project base configuration
└── components/                        # Component-specific configurations
    ├── macos-api.yml                 # API component settings
    ├── tracker.yml                   # Tracker component settings
    ├── player.yml                    # Player component settings
    ├── camguard.yml                  # Camguard component settings
    └── alpr.yml                      # ALPR component settings
```

## 🏗️ Variable Hierarchy

### Inheritance Chain

Variables are inherited in the following order (later values override earlier ones):

```text
Global (all) → Platform (macos/ubuntu) → Project (f1/spectra) → Environment (prod/preprod) → Host
```

### Detailed Precedence

1. **Global Defaults** (`group_vars/all/`)
   - Connection settings, software versions, common packages
   - Applied to all hosts regardless of project or platform

2. **Platform Defaults** (`group_vars/platforms/`)
   - macOS-specific or Ubuntu-specific configurations
   - Applied based on host platform membership

3. **Project Base** (`group_vars/{project}_base.yml`)
   - Project-wide configurations and component deployments
   - Applied to all hosts in a specific project

4. **Environment Settings** (`group_vars/environments/`)
   - Environment-specific configurations (prod vs staging)
   - Applied based on environment group membership

5. **Host Variables** (defined in inventory files)
   - Host-specific overrides and connection details
   - Highest precedence for specific host configurations

## 📋 Inventory File Format

### Standard Project Inventory

**Example:** `inventory/projects/f1/prod.yml`

```yaml
all:
  children:
    macos:
      hosts:
        f1-ca-001:
          ansible_host: 100.64.1.10
          ansible_user: admin
        f1-ca-002:
          ansible_host: 100.64.1.11
          ansible_user: admin
      vars:
        # Platform-specific overrides if needed
    ubuntu:
      hosts:
        f1-ml-001:
          ansible_host: 100.64.1.20
          ansible_user: ubuntu
      vars:
        # Ubuntu-specific overrides if needed
    # Group assignments for variable inheritance
    production:
      children:
        - macos
        - ubuntu
    f1_base:
      children:
        - macos
        - ubuntu
```

### Specialized Project Inventory

**Example:** `inventory/projects/evenko/tracker-prod.yml`

```yaml
all:
  children:
    macos:
      hosts:
        evenko-tracker-001:
          ansible_host: 100.64.2.10
          ansible_user: admin
        evenko-tracker-002:
          ansible_host: 100.64.2.11
          ansible_user: admin
    production:
      children:
        - macos
    evenko_base:
      children:
        - macos
    tracker_specialized:
      children:
        - macos
      vars:
        # Tracker-specific configurations
        oa_environment:
          tracker:
            enabled: true
            config:
              detection_classes: ["person", "head"]
              confidence_threshold: 0.5
```

## 🔧 Variable Configuration Examples

### Global Defaults (`group_vars/all/ansible_connection.yml`)

```yaml
# Connection settings applied to all hosts
ansible_connection: ssh
ansible_ssh_pipelining: true
ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
ansible_python_interpreter: auto_silent
```

### Platform Defaults (`group_vars/platforms/macos.yml`)

```yaml
# macOS-specific configurations
runtime:
  python:
    version: "3.12"
    installer: "pyenv"
  node:
    version: "20"
    installer: "nvm"

system:
  homebrew:
    packages:
      - git
      - curl
      - wget
      - htop
```

### Project Base (`group_vars/f1_base.yml`)

```yaml
# F1 project-wide configurations
project_name: "f1"
project_environment: "{{ group_names | select('match', '(production|preprod|staging)') | first | default('development') }}"

# Component deployment configuration
oa_environment:
  macos_api:
    enabled: true
    config:
      port: 9090
      log_level: "INFO"
  
  tracker:
    enabled: true
    config:
      port: 8080
      model_path: "models/yolo11m.pt"
      detection_classes: ["person"]
  
  player:
    enabled: true
    config:
      display_mode: "dual"
      content_source: "{{ project_name }}_content"
```

### Environment Settings (`group_vars/environments/production.yml`)

```yaml
# Production environment configurations
environment_type: "production"
log_level: "WARNING"
monitoring_enabled: true
debug_mode: false

# Production-specific service configurations
service_configs:
  restart_policy: "always"
  health_check_interval: 30
  max_memory_usage: "2G"
```

## 🚀 Usage Examples

### Deploying to Specific Projects

```bash
# Deploy to F1 production environment
./scripts/run projects/f1/prod -t macos-api,tracker

# Deploy to Spectra pre-production
./scripts/run projects/spectra/preprod -t base,network,security

# Deploy to Evenko tracker-specific hosts
./scripts/run projects/evenko/tracker-prod -t tracker
```

### Variable Resolution Examples

For host `f1-ca-001` in `projects/f1/prod.yml`:

1. **Global**: `ansible_connection: ssh` (from `group_vars/all/`)
2. **Platform**: `runtime.python.version: "3.12"` (from `group_vars/platforms/macos.yml`)
3. **Project**: `project_name: "f1"` (from `group_vars/f1_base.yml`)
4. **Environment**: `environment_type: "production"` (from `group_vars/environments/production.yml`)
5. **Host**: `ansible_host: 100.64.1.10` (from inventory file)

### Component-Specific Deployments

```bash
# Deploy only API component with component-specific variables
./scripts/run projects/f1/prod -t macos-api

# Deploy tracker with specialized configuration
./scripts/run projects/evenko/tracker-prod -t tracker
```

## 🛠️ Best Practices

### Inventory Organization

1. **Keep inventory files minimal** - Only host definitions and group assignments
2. **Use group_vars for configuration** - Leverage variable hierarchy
3. **Follow naming conventions** - `{project}_base.yml` for project configurations
4. **Organize by purpose** - Separate specialized inventories when needed

### Variable Management

1. **Global first** - Put common configurations in `group_vars/all/`
2. **Platform separation** - Use `platforms/` for OS-specific settings
3. **Project isolation** - Keep project-specific configs in `{project}_base.yml`
4. **Environment differentiation** - Use `environments/` for env-specific settings

### Deployment Patterns

1. **Use project paths** - Always specify full project path: `projects/{project}/{env}`
2. **Tag-based deployment** - Use component tags for granular control
3. **Preview changes** - Use `--check --diff` before production deployments
4. **Limit scope** - Use `-l` flag for specific host targeting

## 🔍 Troubleshooting

### Variable Precedence Issues

```bash
# Check variable resolution for specific host
ansible-inventory -i inventory/projects/f1/prod.yml --host f1-ca-001

# View all variables for a group
ansible-inventory -i inventory/projects/f1/prod.yml --group macos --vars
```

### Inventory Validation

```bash
# Validate inventory syntax
ansible-inventory -i inventory/projects/f1/prod.yml --list

# Check group membership
ansible-inventory -i inventory/projects/f1/prod.yml --graph
```

### Common Issues

1. **Missing group assignments** - Ensure hosts are in appropriate groups for variable inheritance
2. **Variable conflicts** - Check precedence order when variables don't resolve as expected
3. **Path issues** - Use full project paths: `inventory/projects/{project}/{env}.yml`

## 📚 Migration from Legacy

### Legacy Structure (Deprecated)

```bash
# Old format (no longer used)
inventory/f1-prod.yml
inventory/spectra-preprod.yml
inventory/alpr-staging.yml
```

### Modern Structure (Current)

```bash
# New format (current)
inventory/projects/f1/prod.yml
inventory/projects/spectra/preprod.yml
inventory/projects/alpr/staging.yml
```

### Migration Steps

1. **Move inventory files** to `projects/{project}/{env}.yml` structure
2. **Extract variables** from inventory files to appropriate `group_vars/` locations
3. **Update deployment commands** to use new project paths
4. **Test variable inheritance** to ensure proper configuration resolution

## 🎯 Summary

The modern inventory structure provides:

- **Simplified Management**: Project-centric organization with clear hierarchy
- **Reduced Redundancy**: Centralized variables with inheritance
- **Enhanced Flexibility**: Component-specific and environment-specific configurations
- **Improved Maintainability**: Clear separation of concerns and consistent patterns

This structure supports the complete oaAnsible ecosystem including oaDashboard integration, oaSentinel model deployment, and multi-platform device management across the OrangeAd infrastructure.
