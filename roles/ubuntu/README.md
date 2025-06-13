# Ubuntu Server Roles

This directory contains Ansible roles for onboarding and configuring Ubuntu servers in the OrangeAd infrastructure.

## Roles

### `ubuntu/base`
- Installs essential packages and utilities
- Configures system timezone
- Creates and configures the ansible user
- Sets up basic directory structure

### `ubuntu/security`
- Configures passwordless sudo access for the ansible user
- Sets up SSH hardening (disable password auth, enable key-based auth)
- Configures basic firewall rules (ufw)

### `ubuntu/network/tailscale`
- Installs Tailscale from official repository
- Configures Tailscale with proper tags (`tag:oa-server`, `tag:oa-ubuntu`)
- Enables SSH access via Tailscale
- Sets up subnet routing for `192.168.1.0/24`
- Enables IP forwarding for routing

## Usage

Use the `deploy-server` script to run the Ubuntu server onboarding playbook:

```bash
# Basic usage
./scripts/deploy-server -e staging -h 192.168.1.100

# With custom SSH user
./scripts/deploy-server -e staging -h 192.168.1.100 -u ubuntu

# Run specific tags only
./scripts/deploy-server -e staging -h 192.168.1.100 -t base,security

# Dry run (check mode)
./scripts/deploy-server -e staging -h 192.168.1.100 --check

# Verbose output
./scripts/deploy-server -e staging -h 192.168.1.100 -v
```

## Prerequisites

1. **Target Server Requirements:**
   - Ubuntu 20.04 LTS or newer
   - SSH access configured
   - User with sudo privileges for initial setup

2. **Vault Configuration:**
   - Update `group_vars/all/vault.yml` with:
     - `vault_ubuntu_ansible_user`: Username for Ansible operations
     - `vault_ubuntu_sudo_password`: Sudo password for the ansible user
     - `vault_tailscale_auth_key`: Tailscale authentication key

3. **Inventory Configuration:**
   - Add target server to appropriate inventory file under `ubuntu_servers` group
   - Set `ansible_host` to server IP address

## Example Inventory Entry

```yaml
ubuntu_servers:
  vars:
    ansible_user: "{{ vault_ubuntu_ansible_user }}"
    ansible_become_password: "{{ vault_ubuntu_sudo_password }}"
  hosts:
    ubuntu-server-001:
      ansible_host: 192.168.1.100
      ansible_port: 22
```

## Post-Deployment Verification

After successful deployment, verify:

1. **Tailscale Status:**
   ```bash
   sudo tailscale status
   ```

2. **Sudo Access:**
   ```bash
   sudo whoami
   ```

3. **Firewall Status:**
   ```bash
   sudo ufw status
   ```

4. **SSH Access:**
   - SSH should work via Tailscale network
   - Password authentication should be disabled

## Security Notes

- The ansible user is granted passwordless sudo access
- SSH password authentication is disabled
- Basic firewall rules allow SSH (port 22) and Tailscale (port 41641/udp)
- Tailscale provides encrypted communication and access control