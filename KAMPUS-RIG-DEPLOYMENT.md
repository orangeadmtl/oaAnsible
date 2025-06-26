# kampus-rig Ubuntu Server Deployment Guide

## Quick Reference Commands

When you're on the same local network as kampus-rig (192.168.1.247):

### 1. Full Ubuntu Server Onboarding (Recommended)
```bash
cd /Users/kaitran/OrangeAd/oaPangaea/oaAnsible
./scripts/run ubuntu-servers
```

This will apply:
- ✅ Base system configuration
- ✅ Security hardening 
- ✅ **Ethernet optimization (fixes Realtek controller issues)**
- ✅ Tailscale setup
- ✅ System performance tuning
- ✅ Network monitoring setup

### 2. Ethernet Optimization Only (If you want just the fixes)
```bash
./scripts/run ubuntu-servers -t optimization,ethernet
```

### 3. Dry Run First (Safe Preview)
```bash
./scripts/run ubuntu-servers --dry-run
```

### 4. Validation After Deployment
```bash
./scripts/check ubuntu-servers
```

## What This Fixes on kampus-rig

### Ethernet Issues Addressed:
1. **Random Disconnections**: Configures r8169 driver with stability options
2. **Speed Downshift**: Ensures Gigabit speeds (100Mbps → 1000Mbps)
3. **Power Management**: Disables Wake-on-LAN and interface sleep
4. **Monitoring**: Sets up real-time connection monitoring
5. **Diagnostics**: Provides troubleshooting tools

### Files Created:
- `/etc/modprobe.d/r8169-orangead.conf` - Driver configuration
- `/etc/systemd/system/ethernet-pm-disable.service` - Power management
- `/home/kai/orangead/network-monitor/` - Monitoring and diagnostics

## Verification Commands

After deployment, SSH to kampus-rig and run:

```bash
# Check ethernet optimization
sudo /home/kai/orangead/network-monitor/ethernet-diagnostics.sh

# Monitor network status
tail -f /home/kai/orangead/network-monitor/network.log

# Check interface speed
ethtool enp34s0 | grep Speed

# Validate configuration
/home/kai/orangead/network-monitor/validate-ethernet-optimization.sh
```

## Troubleshooting

If the deployment fails:

1. **Check SSH access**:
   ```bash
   ssh kai@192.168.1.247
   ```

2. **Test with limit to specific host**:
   ```bash
   ./scripts/run ubuntu-servers -l kampus-rig
   ```

3. **Check inventory**:
   ```bash
   ./scripts/sync list
   ```

## Expected Results

After successful deployment:
- ✅ Stable Tailscale connections (no more random disconnections)
- ✅ Consistent Gigabit ethernet speeds  
- ✅ Real-time network monitoring
- ✅ Comprehensive diagnostic tools
- ✅ Hardened Ubuntu server configuration

The ethernet optimization specifically targets the Realtek controller issues we encountered and should resolve the Tailscale connectivity problems.