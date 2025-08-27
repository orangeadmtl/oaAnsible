# Maintenance Playbooks

This directory contains specialized playbooks for system maintenance operations that were previously handled by standalone scripts.

## Available Playbooks

### 1. `stop_services.yml` - Service Management

Gracefully stops OrangeAd services across macOS and Ubuntu hosts.

**Usage:**
```bash
# Stop all services
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml

# Stop specific services by tag
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags "api,tracker"
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags player

# Target specific hosts
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --limit "f1-ca-001,f1-ca-002"
```

**Available Tags:**
- `api` / `device-api` - Device API service
- `tracker` / `tracker-api` - AI tracking services
- `player` / `video` - Video player service
- `camguard` - CamGuard and related services
- `alpr` - ALPR services
- `health` / `monitor` - Health monitoring services

### 2. `reboot_hosts.yml` - System Reboot

Safely reboots hosts with graceful service shutdown and post-reboot verification.

**Usage:**
```bash
# Standard reboot with graceful service shutdown
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --extra-vars "confirm_reboot=yes"

# Target specific hosts
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --limit "f1-ca-001" --extra-vars "confirm_reboot=yes"

# Immediate reboot (skip graceful shutdown)
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --tags immediate --extra-vars "confirm_reboot=yes"

# Custom reboot settings
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml \
  --extra-vars "confirm_reboot=yes reboot_delay=30 reboot_timeout=600"
```

**Safety Features:**
- Requires explicit confirmation via `confirm_reboot=yes`
- Graceful service shutdown before reboot
- Configurable delays and timeouts
- Post-reboot system verification
- Service status reporting

**Available Tags:**
- `graceful` - Include graceful service shutdown (default)
- `immediate` - Skip graceful shutdown, reboot immediately
- `reboot` - The actual reboot operation

## Integration with Scripts

These playbooks replace the functionality previously provided by:
- `scripts/stop` → `playbooks/maintenance/stop_services.yml`
- `scripts/reboot` → `playbooks/maintenance/reboot_hosts.yml`

## Using with the `run` Script

You can also use these maintenance playbooks through the main `run` script:

```bash
# Via run script (recommended)
./scripts/run projects/f1/prod --extra-vars "playbook=maintenance/stop_services.yml" --tags api

# Direct ansible-playbook execution
cd /path/to/oaAnsible
ansible-playbook -i inventory/projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api
```

## Best Practices

1. **Always test first**: Use `--check` or `--dry-run` modes when possible
2. **Production safety**: These playbooks include safety confirmations for production environments
3. **Service dependencies**: Stop services in the correct order (API → Tracker → Player)
4. **Monitoring**: Check service status after operations complete
5. **Coordination**: Coordinate reboots with team members for production systems

## Troubleshooting

### Services Won't Stop
- Check if services are loaded: `launchctl list | grep orangead` (macOS)
- Verify service names match your deployment
- Check for processes holding resources

### Reboot Issues
- Increase `reboot_timeout` for slower systems
- Use `--tags immediate` if graceful shutdown hangs
- Check SSH connectivity after reboot

### Permission Issues
- Ensure proper sudo/admin privileges
- Verify service ownership (user vs system level)
- Check SSH key authentication