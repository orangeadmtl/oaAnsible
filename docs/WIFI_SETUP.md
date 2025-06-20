# WiFi Configuration Guide

Complete guide for setting up WiFi networks on macOS devices using oaAnsible.

## 🔧 Setup Process

### Step 1: Enable WiFi Configuration

Edit the macOS platform configuration:

```bash
# Edit the group_vars file
vim inventory/platforms/macos/group_vars/all.yml
```

Change the network configuration:

```yaml
# Network configuration
network:
  configure_wifi: true # Change from false to true
```

### Step 2: Add WiFi Credentials to Vault

Add your WiFi network credentials securely to the vault:

```bash
# Edit the encrypted vault file
ansible-vault edit group_vars/all/vault.yml
```

Add the WiFi networks section:

```yaml
# WiFi configuration (for macOS devices)
vault_wifi_networks:
  - ssid: "Kampus"
    password: "Kampus94"
    security_type: "WPA2"
    auto_connect: true

  # Add more networks as needed
  - ssid: "Office-WiFi"
    password: "office-password-123"
    security_type: "WPA2"
    auto_connect: false

  - ssid: "Guest-Network"
    password: "guest-pass"
    security_type: "WPA2"
    auto_connect: false
```

### Step 3: Deploy WiFi Configuration

Deploy the WiFi configuration to your devices:

```bash
# Deploy WiFi to specific device
./scripts/run-staging -l mac-mini-01 -t wifi

# Deploy WiFi to all staging devices
./scripts/run-staging -t wifi

# Check mode to see what would be configured
./scripts/run-staging -l mac-mini-01 -t wifi --check

# Deploy WiFi as part of network stack
./scripts/run-component staging network-stack -l mac-mini-01
```

## 📋 WiFi Network Configuration Options

### Basic Configuration

```yaml
vault_wifi_networks:
  - ssid: "NetworkName"
    password: "NetworkPassword"
    security_type: "WPA2" # WPA2, WPA3, WEP, Open
```

### Advanced Configuration

```yaml
vault_wifi_networks:
  - ssid: "CorporateNetwork"
    password: "secure-password"
    security_type: "WPA2"
    auto_connect: true # Automatically connect to this network
    priority: 1 # Connection priority (lower = higher priority)
    hidden: false # Set to true for hidden networks
```

### Multiple Networks

```yaml
vault_wifi_networks:
  - ssid: "Primary-Network"
    password: "primary-pass"
    security_type: "WPA2"
    auto_connect: true
    priority: 1

  - ssid: "Backup-Network"
    password: "backup-pass"
    security_type: "WPA2"
    auto_connect: true
    priority: 2

  - ssid: "Guest-Access"
    password: "guest-pass"
    security_type: "WPA2"
    auto_connect: false
    priority: 3
```

## 🎯 Usage Examples

### Single Device WiFi Setup

```bash
# Configure WiFi on specific Mac Mini
./scripts/run-staging -l kampus-rig -t wifi

# With verbose output to see configuration details
./scripts/run-staging -l kampus-rig -t wifi -v

# Check mode to preview WiFi configuration
./scripts/run-staging -l kampus-rig -t wifi --check
```

### Mass WiFi Deployment

```bash
# Configure WiFi on all staging macOS devices
./scripts/run-staging -t wifi

# Configure WiFi on specific group of devices
./scripts/run-staging -l "mac-mini-01,mac-mini-02,kampus-rig" -t wifi

# Configure WiFi on all production devices
./scripts/run-prod -t wifi
```

### Combined Deployments

```bash
# Deploy network stack including WiFi
./scripts/run-component staging network-stack -l mac-mini-01

# Deploy full system with WiFi included
./scripts/run-staging -l mac-mini-01

# Deploy base system + WiFi configuration
./scripts/run-environment staging base -l mac-mini-01 -t wifi
```

## 🔍 Verification and Troubleshooting

### Verify WiFi Configuration

```bash
# Verify network configuration
./scripts/run-verify staging network -l mac-mini-01

# Check WiFi status via SSH
./scripts/oassh mac-mini-01
# Then run: networksetup -getairportnetwork en0
```

### Common Issues and Solutions

#### WiFi Not Connecting

```bash
# Check if WiFi is available
ssh mac-mini-01 "networksetup -listallhardwareports"

# Check current WiFi status
ssh mac-mini-01 "networksetup -getairportnetwork en0"

# List available networks
ssh mac-mini-01 "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
```

#### Configuration Not Applied

```bash
# Run with verbose mode to see detailed output
./scripts/run-staging -l mac-mini-01 -t wifi -vv

# Check if WiFi configuration is enabled
grep -A 5 "configure_wifi" inventory/platforms/macos/group_vars/all.yml

# Verify vault contains WiFi networks
ansible-vault view group_vars/all/vault.yml --vault-password-file vault_password_file | grep -A 10 vault_wifi_networks
```

#### Permission Issues

```bash
# Ensure the target device allows network configuration changes
# May require manual approval on first run for some security settings
```

### Debug WiFi Deployment

```bash
# Run WiFi configuration with maximum verbosity
./scripts/run-staging -l mac-mini-01 -t wifi -vvv

# Check network service configuration
ssh mac-mini-01 "networksetup -listnetworkserviceorder"

# Verify WiFi interface name
ssh mac-mini-01 "networksetup -listallhardwareports | grep -A 1 Wi-Fi"
```

## 🔐 Security Considerations

### Vault Security

- WiFi passwords are stored encrypted in the Ansible vault
- Use strong vault passwords
- Rotate WiFi passwords regularly
- Limit access to vault files

### Network Security

- Use WPA2 or WPA3 security protocols
- Avoid WEP or open networks when possible
- Consider using enterprise authentication for corporate networks

### Deployment Security

- Test WiFi configuration in staging before production
- Use check mode to preview changes
- Monitor device connectivity after WiFi changes

## 🚀 Advanced Usage

### Environment-Specific WiFi

```bash
# Different WiFi networks for different environments
# Edit inventory/staging/group_vars/all.yml for staging-specific networks
# Edit inventory/production/group_vars/all.yml for production-specific networks
```

### Conditional WiFi Configuration

```yaml
# In group_vars, configure WiFi based on device location or type
vault_wifi_networks: >-
  {% if inventory_hostname.startswith('kampus-') %} [{"ssid": "Kampus", "password": "Kampus94", "security_type": "WPA2"}] {% elif
  inventory_hostname.startswith('office-') %} [{"ssid": "Office-WiFi", "password": "office-pass", "security_type": "WPA2"}] {% else %} [] {% endif %}
```

### WiFi with Other Network Components

```bash
# Deploy complete network stack including Tailscale + WiFi
./scripts/run-component staging network-stack -l mac-mini-01

# Deploy WiFi + DNS configuration
./scripts/run-staging -l mac-mini-01 -t "wifi,dns"

# Deploy network security + WiFi
./scripts/run-staging -l mac-mini-01 -t "wifi,network,security"
```

---

## 📚 Related Documentation

- [Script Usage Guide](SCRIPT_USAGE.md) - Complete script usage examples
- [Quick Reference](QUICK_REFERENCE.md) - Common commands
- [Network Configuration](../roles/macos/network/README.md) - Network role details

For additional help, check the troubleshooting section above or consult the main project documentation.
