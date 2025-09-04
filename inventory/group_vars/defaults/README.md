# Service Defaults Directory

This directory contains centralized default configurations that can be imported and overridden by specific environments and projects.

## Usage Pattern

```yaml
# In environment-specific files (e.g., yuh/staging.yml)
parking_monitor: "{{ parking_monitor_defaults | combine(environment_overrides.staging.parking_monitor, recursive=True) }}"
```

## Benefits

1. **DRY Principle**: Eliminates configuration duplication
2. **Consistency**: Ensures consistent defaults across environments  
3. **Maintainability**: Central location for configuration updates
4. **Type Safety**: Structured approach to configuration management

## Files

- `service_defaults.yml` - Default configurations for all services
- Additional service-specific defaults can be added as needed