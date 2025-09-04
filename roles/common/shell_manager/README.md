# Shell Manager Role

Centralized, platform-aware shell configuration management for OrangeAd infrastructure.

## Overview

The Shell Manager provides unified shell configuration across macOS, Ubuntu, and OrangePi platforms, eliminating the PATH duplication issues and ensuring consistent, idempotent deployments.

## Features

- **Platform-Aware**: Automatically detects and configures for macOS, Ubuntu, and OrangePi
- **Template-Driven**: Uses Jinja2 templates for consistent, duplicate-free configuration
- **Component Management**: Declarative configuration for uv, nvm, bun, cargo, homebrew
- **Validation & Rollback**: Built-in syntax validation and automatic rollback on failure
- **Backup Management**: Automatic backup with configurable retention
- **Zero Duplicates**: Eliminates PATH export duplication through template-based generation

## Quick Start

### Basic Usage

```yaml
# In your playbook
- name: Configure shell environment
  ansible.builtin.include_role:
    name: common/shell_manager
```

### With Project-Specific Overrides

```yaml
# In inventory group_vars or host_vars
shell_manager_overrides:
  components:
    cargo: false          # Disable Rust for this project
    oh_my_zsh:
      theme: "custom-theme"
  custom:
    aliases:
      logs: "tail -f $HOME/orangead/logs/*.log"
      status: "launchctl list | grep orangead"
    exports:
      PROJECT_ENV: "production"
```

## Platform Support

| Platform | Shell | Components Supported |
|----------|-------|---------------------|
| macOS    | zsh   | homebrew, uv, nvm, bun, cargo, oh-my-zsh |
| Ubuntu   | bash  | uv, nvm, bun, cargo |
| OrangePi | zsh   | uv, nvm, bun, cargo, oh-my-zsh |

## Configuration

### Default Components

```yaml
shell_manager:
  components:
    python:  # UV-based Python environment
      enabled: true
      default_version: "3.11.11"
    nvm:
      enabled: true  
      default_version: "22.11.0"
    bun:
      enabled: true
    cargo:
      enabled: false  # Disabled by default
    oh_my_zsh:
      enabled: true   # macOS and OrangePi only
```

### Project Overrides

Projects can override defaults through `shell_manager_overrides`:

```yaml
# evenko project example
shell_manager_overrides:
  components:
    cargo: false
  custom:
    aliases:
      cam: "launchctl list | grep camguard"
      logs: "tail -f $HOME/orangead/logs/*.log"
```

## Migration from Legacy Shell Configuration

### Automated Cleanup

Clean up existing duplicate configurations:

```bash
# Run cleanup playbook
ansible-playbook -i inventory/your-inventory.yml \
  playbooks/maintenance/shell_cleanup.yml

# Deploy new shell manager
ansible-playbook -i inventory/your-inventory.yml \
  universal.yml --tags shell_manager
```

### Manual Migration Steps

1. **Backup Current Configuration**
   ```bash
   cp ~/.zshrc ~/.zshrc.backup
   cp ~/.zprofile ~/.zprofile.backup
   ```

2. **Run Shell Manager**
   ```bash
   ansible-playbook universal.yml --tags shell_manager --limit your-host
   ```

3. **Verify Configuration**
   ```bash
   source ~/.zprofile
   echo $PATH | tr ':' '\n' | sort | uniq -d  # Should show no duplicates
   ```

## File Structure

```
roles/common/shell_manager/
├── defaults/main.yml          # Default configuration
├── tasks/
│   ├── main.yml              # Main orchestration
│   ├── deploy.yml            # Template deployment
│   ├── validate.yml          # Pre/post validation
│   ├── backup.yml            # Backup management
│   └── rollback.yml          # Emergency rollback
├── templates/
│   ├── zshrc.j2             # Zsh interactive config
│   ├── zprofile.j2          # Zsh environment config (macOS)
│   ├── bashrc.j2            # Bash interactive config
│   └── bash_profile.j2      # Bash environment config (Ubuntu)
├── files/
│   └── shell_deduplicator.py # Cleanup utility
└── README.md                 # This file
```

## Generated Files

### macOS
- **`.zprofile`**: Environment variables (PATH, exports)
- **`.zshrc`**: Interactive shell settings (aliases, oh-my-zsh)

### Ubuntu/OrangePi
- **`.bash_profile`**: Environment variables (PATH, exports)
- **`.bashrc`**: Interactive shell settings (aliases, history)

## Validation

The shell manager includes comprehensive validation:

- **Syntax Validation**: Ensures shell files are syntactically correct
- **Component Validation**: Verifies enabled components are available
- **Performance Validation**: Ensures shell load time < 3 seconds
- **Duplicate Detection**: Prevents PATH export duplication

## Backup and Recovery

### Automatic Backups
- Created before every deployment
- Stored in `~/.shell_manager_backups/`
- Retention: 7 days (configurable)
- Maximum: 5 backups (configurable)

### Manual Rollback
```bash
# List available backups
ls ~/.shell_manager_backups/backup_*.json

# Restore specific backup (replace timestamp)
ansible-playbook universal.yml --tags shell_manager \
  -e "force_rollback=true" \
  -e "rollback_timestamp=1640995200"
```

## Troubleshooting

### Common Issues

1. **Shell Load Time Too Slow**
   ```yaml
   shell_manager_overrides:
     validation:
       max_load_time: 5  # Increase threshold
   ```

2. **Component Not Found**
   - Ensure component is installed before running shell_manager
   - Check component enabled_platforms in defaults

3. **Permission Denied**
   - Ensure ansible_user has write access to home directory
   - Check file permissions after deployment

### Debug Mode

```bash
# Run with maximum verbosity
ansible-playbook universal.yml --tags shell_manager -vvv
```

### Log Locations

- Deployment logs: Ansible output
- Backup metadata: `~/.shell_manager_backups/backup_*.json`
- Rollback logs: `~/.shell_manager_backups/rollback_*.log`

## Integration with Existing Roles

The shell manager replaces shell configuration in:

- `roles/macos/base/tasks/shell_config.yml` → **DEPRECATED**
- `roles/macos/base/tasks/enhance_zsh.yml` → **DEPRECATED**
- `roles/macos/python/tasks/main.yml` → Shell integration removed
- `roles/macos/node/tasks/main.yml` → Shell integration removed

These roles now rely on shell_manager for consistent configuration.

## Tags

- `shell_manager`: All shell manager tasks
- `shell_manager.backup`: Backup operations only
- `shell_manager.deploy`: Deployment operations only
- `shell_manager.validation`: Validation operations only
- `shell_manager.cleanup`: Cleanup operations only

## Contributing

When adding new components or platforms:

1. Update `defaults/main.yml` with component configuration
2. Add platform support to templates
3. Update validation logic in `tasks/validate.yml`
4. Test across all supported platforms
5. Update this documentation

## Version History

- **v1.0**: Initial implementation with macOS, Ubuntu, OrangePi support
- **v1.1**: Added comprehensive validation and rollback mechanisms
- **v1.2**: Platform-aware template selection and component management