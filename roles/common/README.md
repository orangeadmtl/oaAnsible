# Common Cross-Platform Roles

This directory contains Ansible roles that provide cross-platform abstractions for common tasks across macOS and Ubuntu platforms.

## Philosophy

The common roles implement platform-neutral interfaces that automatically adapt to the target platform. This allows for consistent deployment patterns while respecting platform-specific implementations.

## Roles

### `common/package_manager`
- Provides unified package installation interface
- Automatically detects and uses the appropriate package manager (apt, brew, etc.)
- Handles platform-specific package name mappings

### `common/service_manager`
- Unified service management across systemd, launchd, and other service managers
- Consistent service configuration patterns
- Platform-agnostic service health checking

### `common/network_config`
- Cross-platform network configuration management
- Unified firewall rule management
- Platform-neutral DNS configuration

### `common/monitoring`
- Standardized health monitoring and metrics collection
- Cross-platform log management
- Unified alerting interfaces

### `common/security`
- Platform-agnostic security hardening
- Consistent user and permission management
- Cross-platform certificate and key management

## Usage Patterns

### Direct Role Usage
```yaml
- role: common/package_manager
  vars:
    common_packages:
      - name: "python3"
        required: true
      - name: "git"
        required: true
```

### Platform Detection
```yaml
- role: common/service_manager
  vars:
    common_services:
      - name: "{{ 'tailscaled' if ansible_os_family == 'Darwin' else 'tailscaled' }}"
        state: started
        enabled: true
```

### Conditional Platform Logic
```yaml
- role: common/monitoring
  when: monitoring_enabled | default(true)
  vars:
    monitoring_tools:
      - htop
      - "{{ 'iostat' if ansible_os_family != 'Darwin' else 'iotop' }}"
```

## Platform Mapping

The common roles use internal mapping tables to translate generic requests to platform-specific implementations:

- **Package Names**: `curl` → `curl` (Linux), `curl` (macOS)
- **Service Names**: `ssh` → `ssh` (Linux), `com.openssh.sshd` (macOS)
- **Paths**: `/etc/config` → `/etc/config` (Linux), `/usr/local/etc/config` (macOS)
- **Commands**: `systemctl` → `systemctl` (Linux), `launchctl` (macOS)

## Benefits

1. **Consistency**: Same deployment patterns across all platforms
2. **Maintainability**: Single source of truth for common tasks
3. **Flexibility**: Easy platform-specific customization when needed
4. **Scalability**: Add new platforms by extending mapping tables
5. **Testing**: Consistent testing patterns across platforms

## Best Practices

1. Always use common roles for standard tasks when possible
2. Platform-specific roles should focus on unique platform features
3. Test common roles across all supported platforms
4. Document platform differences and limitations
5. Use feature detection rather than platform detection when possible