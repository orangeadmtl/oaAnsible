# Ubuntu Server Optimization Role

## Overview
Comprehensive optimization role for Ubuntu servers in the OrangeAd infrastructure, including specialized ethernet optimization for common Realtek controller issues.

## Features

### Core Optimizations
- **Kernel Parameter Tuning**: Network, memory, and filesystem optimizations
- **System Limits**: Increased file handles and process limits
- **Service Management**: Disable unnecessary services, enable essential ones
- **Storage Optimization**: SSD trim, log rotation, cleanup automation
- **Network Performance**: DNS optimization and TCP tuning
- **Security Hardening**: Automatic updates and kernel security features

### Ethernet Optimization (NEW)
- **Hardware Detection**: Automatic detection of Realtek ethernet controllers
- **Driver Stability**: Configure r8169 driver for maximum stability
- **Power Management**: Disable WoL and interface power management
- **Speed Optimization**: Ensure Gigabit speeds where supported
- **Monitoring**: Continuous monitoring of ethernet stability and Tailscale connectivity
- **Diagnostics**: Comprehensive troubleshooting tools and guides

## Realtek Controller Support

### Supported Controllers
- RTL8111/8168/8211/8411 PCI Express Gigabit Ethernet Controllers
- Common in mini PCs, servers, and workstations

### Common Issues Addressed
1. **Random disconnections** (LinkChange: all links down)
2. **Speed downshift** (1000Mbps → 100Mbps)
3. **Tailscale connectivity issues** due to ethernet instability
4. **"Network unreachable" errors** in logs

### Solutions Applied
1. **Driver Configuration**: `r8169` options for stability
   - `use_dac=1`: 64-bit DMA addressing
   - `eee_enable=0`: Disable Energy Efficient Ethernet
2. **Power Management**: Disable Wake-on-LAN and interface sleep
3. **Monitoring**: Real-time ethernet and connectivity monitoring
4. **Diagnostics**: Comprehensive troubleshooting tools

## Usage

### During Server Onboarding
Ethernet optimization is automatically included in the Ubuntu server onboarding process:
```bash
ansible-playbook playbooks/onboard-ubuntu-server.yml -i inventory/your-inventory.yml
```

### For Existing Servers
Apply optimizations to existing Ubuntu servers:
```bash
ansible-playbook playbooks/ubuntu-server-optimizations.yml -i inventory/your-inventory.yml
```

### Selective Application
Run only ethernet optimization:
```bash
ansible-playbook playbooks/ubuntu-server-optimizations.yml -i inventory/your-inventory.yml --tags ethernet
```

## Configuration

### Default Settings
All optimizations are enabled by default. Key ethernet settings:

```yaml
ethernet_optimization:
  enabled: true
  detect_realtek: true
  power_management:
    disable_wol: true
    disable_interface_pm: true
  monitoring:
    enabled: true
    interval_minutes: 2
    monitor_tailscale: true
```

### Customization
Override defaults in group_vars or host_vars:

```yaml
# Disable ethernet optimization
ethernet_optimization:
  enabled: false

# Custom monitoring interval
ethernet_optimization:
  monitoring:
    interval_minutes: 5
    log_retention_days: 14
```

## Files Created

### Driver Configuration
- `/etc/modprobe.d/r8169-orangead.conf` - Driver options
- `/etc/systemd/system/ethernet-pm-disable.service` - Power management service

### Monitoring and Diagnostics
- `/home/{user}/orangead/network-monitor/monitor.sh` - Monitoring script
- `/home/{user}/orangead/network-monitor/network.log` - Connection log
- `/home/{user}/orangead/network-monitor/ethernet-diagnostics.sh` - Diagnostic tool
- `/home/{user}/orangead/network-monitor/troubleshooting-guide.md` - Guide

## Troubleshooting

### Check Ethernet Status
```bash
# Run diagnostics
/home/{user}/orangead/network-monitor/ethernet-diagnostics.sh

# Check monitoring log
tail -f /home/{user}/orangead/network-monitor/network.log

# Check interface status
cat /sys/class/net/*/operstate
ethtool eth0  # or your interface name
```

### Common Issues

#### Still Getting 100Mbps Instead of Gigabit
1. **Replace ethernet cable** (most common fix)
2. **Try different switch/router port**
3. **Check cable quality** (Cat6/Cat6a recommended)
4. **Verify switch supports Gigabit**

#### Random Disconnections Continue
1. **Check monitoring logs** for patterns
2. **Run ethernet diagnostics** for detailed analysis
3. **Consider USB ethernet adapter** as backup
4. **Contact support** with diagnostic output

### Emergency Recovery
If network becomes unresponsive after optimization:

```bash
# Reset to safe defaults
sudo ethtool -s eth0 autoneg on
sudo systemctl restart systemd-networkd

# Remove driver configuration if needed
sudo rm /etc/modprobe.d/r8169-orangead.conf
sudo update-initramfs -u
```

## Integration with OrangeAd Infrastructure

### Tailscale Compatibility
- Ethernet optimization runs **before** Tailscale setup in onboarding
- Monitoring includes Tailscale connectivity status
- Helps prevent Tailscale disconnections due to ethernet issues

### Fleet Management
- Consistent ethernet configuration across all Ubuntu servers
- Proactive monitoring and issue detection
- Standardized troubleshooting tools and procedures

## Testing

Tested and validated on:
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS
- Various Realtek ethernet controllers
- kampus-rig (validation system)

## Performance Impact
- **Positive**: Improved network stability and consistent Gigabit speeds
- **Minimal**: Low overhead monitoring (every 2 minutes by default)
- **None**: Optimizations only applied to detected Realtek controllers