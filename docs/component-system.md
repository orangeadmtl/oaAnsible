# Component Resolution System

## Overview

The improved component system automatically determines which components to deploy based on:

1. **Foundation Defaults** - Always deployed components (base, network, security, device-api)
2. **Project Stack** - Project-specific components defined in `stack.yml`
3. **Explicit Selection** - Components specified via `--tags` parameter

## Foundation Components (Always Deployed)

Unless explicitly disabled, these components are automatically included:

- **base** - System foundation setup (users, directories, basic tools)
- **network** - Network configuration (Tailscale, SSH hardening)
- **security** - Security hardening and SSH key management
- **device-api** - Unified device API (mandatory for all hosts)

## Configuration Files

### Project Stack (`30_projects/[project]/stack.yml`)

```yaml
project_stack:
  # Only specify project-specific components
  # Foundation components auto-included
  components:
    - parking-monitor  # AI parking detection (port 9091)
    - player          # Video player (if needed)
  
  component_configs:
    parking-monitor:
      service:
        port: 9091
        log_level: "INFO"
      detection:
        confidence_threshold: 0.6
```

### Host Configuration (`30_projects/[project]/hosts/staging.yml`)

```yaml
all:
  vars:
    # Minimal configuration - component resolution handled automatically
    target_env: "project-staging"
    deployment_environment: "staging"
    project_name: "project"
```

## Component Resolution Process

1. **Load Foundation Defaults** from `00_foundation/defaults.yml`
2. **Load Project Stack** from `30_projects/[project]/stack.yml`
3. **Load Component Registry** from `10_components/_registry.yml`
4. **Resolve Components**:
   - Start with foundation components
   - Add project-specific components
   - Override with explicit `--tags` if provided
   - Add dependencies automatically
   - Filter by platform compatibility
5. **Validate Dependencies** and conflicts

## Component Information

### oaParkingMonitor API Details

- **Service**: `com.orangead.parking-monitor`
- **Port**: 9091
- **API Endpoints**:
  - `/health` - Service health check
  - `/api/stats` - Detection statistics
  - `/api/detection` - Current parking results
  - `/api/spaces` - Parking space definitions
  - `/dashboard` - Monitoring UI
- **Repository**: `https://github.com/oa-device/oaParkingMonitor.git`
- **Dependencies**: Requires `device-api`

## Usage Examples

### Default Deployment (Foundation + Project Components)
```bash
# Deploys: base, network, security, device-api, parking-monitor
./scripts/run projects/yuh/staging
```

### Explicit Component Selection (Still includes Foundation)
```bash
# Deploys: base, network security, device-api, parking-monitor
./scripts/run projects/yuh/staging --tags parking-monitor
```

### Foundation Only Deployment
```bash
# Deploys: base, network, security, device-api
./scripts/run projects/yuh/staging --tags device-api
```

## Benefits

1. **Simplified Configuration**: No more manual `deploy_*` flags
2. **Consistent Defaults**: Foundation components always deployed
3. **Dependency Resolution**: Automatic dependency management  
4. **Platform Filtering**: Components filtered by platform compatibility
5. **Explicit Override**: `--tags` still works for selective deployment

## Migration from Old System

### Before (Manual Flags)
```yaml
deploy_device_api: true
deploy_parking_monitor: true
deploy_player: false
deploy_tracker: false
```

### After (Automatic Resolution)
```yaml
# In stack.yml - only project-specific components
components:
  - parking-monitor

# Foundation components (base, network, security, device-api) auto-included
```

The system is backward compatible - old explicit flags still work but are no longer needed.