# macOS Server Optimizations Role

This role configures macOS devices to operate in a server-like mode with minimal UI and maximum uptime. It's designed for OrangeAd's Mac Mini devices that need
to run reliably with minimal user interaction.

## Features

### Auto-Login Configuration

- Enables automatic login to eliminate manual intervention after reboots
- Hides user list from login screen for security
- Disables guest user login

### UI Minimization

- Disables or minimizes the Dock
- Disables Dashboard and Mission Control
- Disables Notification Center
- Disables animations and visual effects
- Disables desktop icons

### System Services Optimization

- Disables Spotlight indexing
- Disables unnecessary services (Bluetooth, AirDrop, Time Machine)
- Disables iCloud services
- Disables automatic software updates
- Disables crash reporter and diagnostics submission
- Configures system resource limits

### Power Management

- Ensures system never sleeps on AC power
- Enables automatic restart on power failure
- Enables automatic restart after kernel panic
- Enables wake for network access
- Disables hibernation for faster sleep/wake

### System Stability Enhancements

- Implements watchdog service for critical processes
- Creates system health check script
- Increases file descriptor limits
- Configures persistent sysctl settings

### Logging Improvements

- Configures log rotation
- Enhances system log retention
- Implements service monitoring

## Usage

This role is included in the main playbook and tagged with `server`, `configuration`, and `optimization`. You can run it specifically with:

```bash
ansible-playbook main.yml --tags "server"
```

## Configuration

Default variables can be overridden in your inventory or playbook:

```yaml
# Example: Disable auto-login
enable_auto_login: false

# Example: Customize health check thresholds
healthcheck_thresholds:
  cpu: 80
  memory: 85
  disk: 90
```

## Dependencies

This role depends on the base macOS configuration being applied first.
