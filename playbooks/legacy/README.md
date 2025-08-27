# Legacy Playbooks

This directory contains playbooks that have been superseded by the universal component framework in `universal.yml`.

## Migrated Playbooks

### Redundant Playbooks (Replaced by universal.yml)

| Legacy Playbook                   | Replacement Command                                                      | Notes                                                 |
| --------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------- |
| `macos-full.yml`                  | `ansible-playbook universal.yml -i inventory/target.yml`                 | Full macOS deployment via inventory configuration     |
| `ubuntu-full.yml`                 | `ansible-playbook universal.yml -i inventory/ubuntu-servers.yml`         | Full Ubuntu deployment via inventory configuration    |
| `server_optimizations.yml`        | `ansible-playbook universal.yml -i inventory/target.yml -t optimization` | Server optimizations via tags                         |
| `platform-detection.yml`          | Built into `universal.yml`                                               | Platform detection is automatic in universal playbook |
| `ubuntu-server-optimizations.yml` | `ansible-playbook universal.yml -i inventory/target.yml -t optimization` | Ubuntu optimizations via tags                         |

### Duplicate Playbooks

| Legacy Playbook             | Kept Playbook           | Reason                                   |
| --------------------------- | ----------------------- | ---------------------------------------- |
| `onboard-ubuntu-server.yml` | `ubuntu-onboarding.yml` | Newer, more comprehensive implementation |

## Migration Benefits

1. **Reduced Complexity**: From 13+ playbooks to 5 active playbooks
2. **Tag-based Deployment**: Use universal.yml with tags for specific components
3. **Inventory-driven Configuration**: Components determined by inventory variables
4. **Consistent Framework**: All deployments use the same component framework
5. **Better Maintainability**: Single source of truth for deployment logic

## Universal.yml Tag Examples

```bash
# Deploy specific components
ansible-playbook universal.yml -i inventory/f1-prod.yml -t device-api
ansible-playbook universal.yml -i inventory/f1-prod.yml -t tracker,security
ansible-playbook universal.yml -i inventory/f1-prod.yml -t base,network,player

# Full deployment (determined by inventory)
ansible-playbook universal.yml -i inventory/f1-prod.yml

# Platform-specific optimizations
ansible-playbook universal.yml -i inventory/target.yml -t optimization
```

## Inventory Configuration

Instead of separate playbooks, use inventory variables to control deployments:

```yaml
# inventory/f1-prod.yml
all:
  vars:
    oa_environment:
      deploy_macos_api: true
      deploy_tracker: true
      deploy_player: false
      deploy_alpr_service: false
```

These playbooks are kept for reference but should not be used for new deployments.
