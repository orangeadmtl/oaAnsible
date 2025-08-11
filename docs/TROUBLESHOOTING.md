# oaAnsible Troubleshooting Guide

Comprehensive troubleshooting guide for the modern oaAnsible system, covering common issues, diagnostic procedures, and resolution steps.

## 🚨 Quick Issue Resolution

### Most Common Issues

| Issue                       | Quick Fix                                                | Reference                                    |
| --------------------------- | -------------------------------------------------------- | -------------------------------------------- |
| **Inventory not found**     | Check path: `projects/project/env.yml`                   | [Inventory Issues](#inventory-issues)        |
| **SSH connection failed**   | Run `./scripts/genSSH` to deploy keys                    | [Connection Issues](#connection-issues)      |
| **Service not starting**    | Check logs and restart with maintenance playbook         | [Service Issues](#service-issues)            |
| **Vault decryption failed** | Verify vault password file exists and is correct         | [Vault Issues](#vault-issues)                |
| **Deprecated script used**  | Check [Script Migration](#script-migration-issues) table | [Script Migration](#script-migration-issues) |

<!-- markdownlint-disable-next-line MD033 -->
## 📁 Inventory Issues <a id="inventory-issues"></a>

### Problem: Inventory File Not Found

**Error Messages:**

```bash
ERROR! the playbook: projects/f1/prod.yml could not be found
No inventory was parsed, please check your configuration and options
```

**Diagnosis:**

```bash
# Check if inventory file exists
ls -la inventory/projects/f1/prod.yml

# List available inventories
find inventory/projects -name "*.yml" | sort
```

**Solutions:**

1. **Verify Path Format:**

   ```bash
   # Correct format
   ./scripts/run projects/f1/prod -t macos-api

   # Wrong format (legacy)
   ./scripts/run f1-prod -t macos-api  # ❌ Will fail
   ```

2. **Check Available Inventories:**

   ```bash
   # List all project inventories
   find inventory/projects -name "*.yml" -exec basename {} \; | sed 's/\.yml$//' | sort

   # Or use interactive mode to see options
   ./scripts/run
   ```

3. **Create Missing Inventory:**

   ```bash
   # Create project directory
   mkdir -p inventory/projects/myproject

   # Create inventory file
   cat > inventory/projects/myproject/prod.yml << 'EOF'
   all:
     children:
       macos:
         hosts:
           host-001:
             ansible_host: 192.168.1.10
             ansible_user: admin
   EOF
   ```

### Problem: Invalid Inventory Format

**Error Messages:**

```bash
ERROR! Syntax Error while loading YAML
mapping values are not allowed here
```

**Diagnosis:**

```bash
# Validate YAML syntax
ansible-inventory -i projects/f1/prod.yml --list

# Check with yq
yq e . inventory/projects/f1/prod.yml
```

**Solutions:**

1. **Fix YAML Syntax:**

   ```yaml
   # Common fixes
   all:
     children: # Ensure proper indentation
       macos: # Use spaces, not tabs
         hosts: # Check colons have space after
   ```

2. **Validate Structure:**

   ```bash
   # Check required sections exist
   yq e '.all.children.macos.hosts' inventory/projects/f1/prod.yml
   ```

<!-- markdownlint-disable-next-line MD033 -->
## 🔌 Connection Issues <a id="connection-issues"></a>

### Problem: SSH Connection Failed

**Error Messages:**

```bash
UNREACHABLE! => {"msg": "Failed to connect to the host via ssh"}
Permission denied (publickey,password)
```

**Diagnosis:**

```bash
# Test direct SSH connection
ssh admin@100.64.1.10

# Test with verbose SSH
ssh -vvv admin@100.64.1.10

# Test ansible connectivity
ansible all -i projects/f1/prod.yml -m ping
```

**Solutions:**

1. **Deploy SSH Keys:**

   ```bash
   # Interactive deployment
   ./scripts/genSSH

   # Direct deployment to host
   ./scripts/genSSH 100.64.1.10 admin

   # With password if needed
   ./scripts/genSSH 100.64.1.10 admin mypassword
   ```

2. **Verify SSH Configuration:**

   ```bash
   # Check SSH key is loaded
   ssh-add -l

   # Load SSH key manually if needed
   ssh-add ~/.ssh/id_rsa

   # Test key-based auth
   ssh -o PasswordAuthentication=no admin@100.64.1.10
   ```

3. **Check Host Accessibility:**

   ```bash
   # Verify host is reachable
   ping 100.64.1.10

   # Check SSH service is running
   nmap -p 22 100.64.1.10

   # Test different port if needed
   ssh -p 2222 admin@100.64.1.10
   ```

### Problem: Tailscale Network Issues

**Error Messages:**

```bash
ssh: connect to host 100.64.1.10 port 22: No route to host
```

**Diagnosis:**

```bash
# Check Tailscale status
tailscale status

# Check if host is in network
tailscale ping 100.64.1.10

# Check routing
ip route | grep 100.64
```

**Solutions:**

1. **Verify Tailscale Connection:**

   ```bash
   # Restart Tailscale
   sudo tailscale down
   sudo tailscale up

   # Check authentication
   tailscale status --peers
   ```

2. **Update Host IP Addresses:**

   ```bash
   # Get current Tailscale IP
   tailscale ip -4

   # Update inventory file with correct IP
   ansible-inventory -i projects/f1/prod.yml --host f1-ca-001
   ```

<!-- markdownlint-disable-next-line MD033 -->
## 🔧 Service Issues <a id="service-issues"></a>

### Problem: Service Not Starting

**Error Messages:**

```bash
FAILED - RETVAL: 1 >> The service com.orangead.macosapi could not be loaded
```

**Diagnosis:**

```bash
# Check service status
ansible macos -i projects/f1/prod.yml -m shell -a "launchctl list | grep com.orangead"

# Check service files
ansible macos -i projects/f1/prod.yml -m shell -a "ls -la ~/Library/LaunchAgents/com.orangead.*.plist"

# Check service logs
ansible macos -i projects/f1/prod.yml -m fetch -a "src=~/orangead/macos-api/logs/api.log dest=./debug-logs/"
```

**Solutions:**

1. **Restart Service with Maintenance Playbook:**

   ```bash
   # Stop service
   ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api

   # Redeploy service
   ./scripts/run projects/f1/prod -t macos-api

   # Verify service is running
   curl http://100.64.1.10:9090/health
   ```

2. **Manual Service Management:**

   ```bash
   # Unload service
   ansible macos -i projects/f1/prod.yml -m shell -a "launchctl unload ~/Library/LaunchAgents/com.orangead.macosapi.plist"

   # Load service
   ansible macos -i projects/f1/prod.yml -m shell -a "launchctl load ~/Library/LaunchAgents/com.orangead.macosapi.plist"

   # Force restart
   ansible macos -i projects/f1/prod.yml -m shell -a "launchctl kickstart -k gui/\$(id -u)/com.orangead.macosapi"
   ```

3. **Check Service Dependencies:**

   ```bash
   # Verify Python environment
   ansible macos -i projects/f1/prod.yml -m shell -a "~/orangead/macos-api/.venv/bin/python --version"

   # Check required packages
   ansible macos -i projects/f1/prod.yml -m shell -a "~/orangead/macos-api/.venv/bin/pip list | grep fastapi"

   # Test manual startup
   ansible macos -i projects/f1/prod.yml -m shell -a "cd ~/orangead/macos-api && .venv/bin/python main.py"
   ```

### Problem: Service Port Already in Use

**Error Messages:**

```bash
[ERROR] Port 9090 is already in use
OSError: [Errno 48] Address already in use
```

**Diagnosis:**

```bash
# Check what's using the port
ansible macos -i projects/f1/prod.yml -m shell -a "lsof -i :9090"

# Check for multiple service instances
ansible macos -i projects/f1/prod.yml -m shell -a "pgrep -f macos-api"
```

**Solutions:**

1. **Stop Conflicting Services:**

   ```bash
   # Stop all OrangeAd services
   ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml

   # Kill conflicting processes
   ansible macos -i projects/f1/prod.yml -m shell -a "pkill -f 'macos-api'"

   # Restart clean
   ./scripts/run projects/f1/prod -t macos-api
   ```

2. **Change Service Port:**

   ```bash
   # Deploy with different port
   ./scripts/run projects/f1/prod -t macos-api -e "macos_api_port=9091"
   ```

<!-- markdownlint-disable-next-line MD033 -->
## 🔐 Vault Issues <a id="vault-issues"></a>

### Problem: Vault Decryption Failed

**Error Messages:**

```bash
ERROR! Decryption failed (no vault secrets would be decrypted)
Vault password incorrect
```

**Diagnosis:**

```bash
# Check vault password file exists
ls -la ~/.ansible_vault_pass

# Test vault decryption
ansible-vault view inventory/group_vars/all/vault.yml

# Check vault file permissions
ls -la inventory/group_vars/all/vault.yml
```

**Solutions:**

1. **Fix Vault Password:**

   ```bash
   # Recreate vault password file
   echo "correct-password" > ~/.ansible_vault_pass
   chmod 600 ~/.ansible_vault_pass

   # Or set environment variable
   export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
   ```

2. **Rekey Vault if Password Lost:**

   ```bash
   # If you know the old password
   ansible-vault rekey inventory/group_vars/all/vault.yml

   # If password is completely lost, you'll need to recreate vault
   ansible-vault create inventory/group_vars/all/vault.yml.new
   ```

3. **Validate Vault Structure:**

   ```bash
   # Check vault content format
   ansible-vault view inventory/group_vars/all/vault.yml | yq e .
   ```

### Problem: Vault Variables Not Loading

**Error Messages:**

```bash
The task includes an option with an undefined variable 'vault_ssh_private_key'
```

**Diagnosis:**

```bash
# Check if vault is being loaded
ansible-playbook universal.yml -i projects/f1/prod.yml --list-tasks -v

# Verify vault variable names
ansible-vault view inventory/group_vars/all/vault.yml | grep "vault_"
```

**Solutions:**

1. **Verify Vault Variable Names:**

   ```bash
   # Check exact variable names in vault
   ansible-vault view inventory/group_vars/all/vault.yml

   # Update role/template references to match
   grep -r "vault_ssh_private_key" roles/
   ```

2. **Force Vault Loading:**

   ```bash
   # Explicitly load vault in playbook run
   ./scripts/run projects/f1/prod -t macos-api --extra-vars "@inventory/group_vars/all/vault.yml"
   ```

<!-- markdownlint-disable-next-line MD033 -->
## 🔄 Deployment Issues <a id="deployment-issues"></a>

### Problem: Deployment Hangs or Times Out

**Error Messages:**

```bash
TASK [Gathering Facts] *********************************************************
fatal: [f1-ca-001]: UNREACHABLE! => {"msg": "Timed out"}
```

**Diagnosis:**

```bash
# Check deployment with verbose output
./scripts/run projects/f1/prod -t base -vvv

# Test connection separately
ansible all -i projects/f1/prod.yml -m ping -f 1
```

**Solutions:**

1. **Reduce Parallelism:**

   ```bash
   # Deploy to fewer hosts at once
   ./scripts/run projects/f1/prod -t macos-api -f 1

   # Deploy to single host first
   ./scripts/run projects/f1/prod -t macos-api -l f1-ca-001
   ```

2. **Check System Resources:**

   ```bash
   # Check target host resources
   ansible all -i projects/f1/prod.yml -m setup -a "filter=ansible_memory_mb"

   # Check controller resources
   top | head -20
   ```

### Problem: Idempotency Issues

**Error Messages:**

```bash
TASK [some_task] ***************************************************************
changed: [f1-ca-001]
# Task shows changed every run when it shouldn't
```

**Diagnosis:**

```bash
# Run deployment twice and compare
./scripts/run projects/f1/prod -t base --check | grep changed
./scripts/run projects/f1/prod -t base --check | grep changed
```

**Solutions:**

1. **Check Task Idempotency:**

   ```bash
   # Review specific task implementation
   grep -A 10 -B 5 "task_name" roles/*/tasks/*.yml
   ```

2. **Use Check Mode:**

   ```bash
   # Test what would change
   ./scripts/run projects/f1/prod -t base --check --diff
   ```

<!-- markdownlint-disable-next-line MD033 -->
## 🛠️ Script Migration Issues <a id="script-migration-issues"></a>

### Problem: Using Deprecated Scripts

**Error Messages:**

```bash
[DEPRECATED] This script is deprecated. Use: ./scripts/run [inventory] --check
```

**Migration Table:**

| Deprecated Script  | Error/Warning       | Modern Alternative          | Example                                                                                                             |
| ------------------ | ------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `./scripts/check`  | Deprecation warning | `./scripts/run --check`     | `./scripts/run projects/f1/prod --check`                                                                            |
| `./scripts/sync`   | Deprecation warning | `./scripts/run` interactive | `./scripts/run` (select inventory)                                                                                  |
| `./scripts/stop`   | Deprecation warning | Maintenance playbook        | `ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api`                       |
| `./scripts/reboot` | Deprecation warning | Maintenance playbook        | `ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --extra-vars "confirm_reboot=yes"` |

**Solutions:**

1. **Update Scripts in Automation:**

   ```bash
   # Update CI/CD pipelines
   # Old: ./scripts/check f1-prod
   # New: ./scripts/run projects/f1/prod --check

   # Update deployment scripts
   # Old: ./scripts/stop f1-prod --api
   # New: ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/stop_services.yml --tags api
   ```

2. **Update Documentation:**

   ```bash
   # Find references to deprecated scripts
   grep -r "scripts/check\|scripts/stop\|scripts/reboot" docs/ README.md

   # Update with modern alternatives
   sed -i 's/scripts\/check/scripts\/run --check/g' docs/*.md
   ```

## 🧪 Testing and Validation

### Problem: Deployment Validation Failed

**Error Messages:**

```bash
TASK [Verify service is running] **********************************************
FAILED - RETVAL: 1 >> Service check failed
```

**Diagnosis:**

```bash
# Test service endpoints directly
curl -v http://100.64.1.10:9090/health

# Check service logs
ansible macos -i projects/f1/prod.yml -m shell -a "tail -50 ~/orangead/macos-api/logs/api.log"

# Verify service process
ansible macos -i projects/f1/prod.yml -m shell -a "pgrep -f macos-api"
```

**Solutions:**

1. **Manual Service Verification:**

   ```bash
   # Check if service is actually running
   ssh admin@100.64.1.10 "launchctl list | grep com.orangead"

   # Test service manually
   ssh admin@100.64.1.10 "cd orangead/macos-api && .venv/bin/python main.py"
   ```

2. **Debug Service Configuration:**

   ```bash
   # Check service configuration
   ansible macos -i projects/f1/prod.yml -m fetch -a "src=~/Library/LaunchAgents/com.orangead.macosapi.plist dest=./debug/"

   # Validate plist format
   plutil -lint debug/com.orangead.macosapi.plist
   ```

## 📊 Performance Issues

### Problem: Slow Deployments

**Symptoms:**

- Deployments taking longer than expected
- High CPU/memory usage during deployment
- Network timeouts

**Diagnosis:**

```bash
# Time deployment execution
time ./scripts/run projects/f1/prod -t macos-api

# Check system resources during deployment
ansible all -i projects/f1/prod.yml -m shell -a "top -l 1 | head -10"

# Check network connectivity
ansible all -i projects/f1/prod.yml -m shell -a "ping -c 3 8.8.8.8"
```

**Solutions:**

1. **Optimize Deployment:**

   ```bash
   # Reduce parallelism for slower networks
   ./scripts/run projects/f1/prod -t macos-api -f 2

   # Deploy components separately
   ./scripts/run projects/f1/prod -t base
   ./scripts/run projects/f1/prod -t macos-api
   ```

2. **Use Tags for Targeted Deployment:**

   ```bash
   # Deploy only what's needed
   ./scripts/run projects/f1/prod -t macos-api,tracker

   # Skip expensive tasks if not needed
   ./scripts/run projects/f1/prod -t base --skip-tags "slow_tasks"
   ```

## 🆘 Emergency Procedures

### Complete System Recovery

**When Everything is Broken:**

1. **Stop All Services:**

   ```bash
   # Emergency stop all services
   ansible all -i projects/f1/prod.yml -m shell -a "launchctl unload ~/Library/LaunchAgents/com.orangead.*.plist" || true
   ```

2. **Clear Application Data:**

   ```bash
   # Remove all OrangeAd data (BE CAREFUL!)
   ansible all -i projects/f1/prod.yml -m file -a "path=~/orangead state=absent"
   ```

3. **Redeploy from Scratch:**

   ```bash
   # Full clean deployment
   ./scripts/run projects/f1/prod
   ```

### Emergency Host Access

**When SSH is Broken:**

1. **Direct Console Access:**

   - Use physical access or remote console (iDRAC, iLO, etc.)
   - Login as admin user directly

2. **Alternative SSH Methods:**

   ```bash
   # Try different user
   ssh root@100.64.1.10

   # Try password auth
   ssh -o PasswordAuthentication=yes admin@100.64.1.10

   # Try different port
   ssh -p 2222 admin@100.64.1.10
   ```

3. **Reset SSH Configuration:**

   ```bash
   # On the target host directly
   sudo systemctl restart ssh  # Ubuntu
   sudo launchctl unload /System/Library/LaunchDaemons/ssh.plist  # macOS
   sudo launchctl load /System/Library/LaunchDaemons/ssh.plist
   ```

## 📞 Getting Help

### Diagnostic Information to Collect

Before asking for help, collect this information:

```bash
# System information
./scripts/run projects/f1/prod --version
ansible --version
python3 --version

# Error reproduction
./scripts/run projects/f1/prod -t macos-api -vvv 2>&1 | tee deployment-error.log

# Inventory information
ansible-inventory -i projects/f1/prod.yml --list > inventory-dump.json

# Service status
ansible all -i projects/f1/prod.yml -m shell -a "launchctl list | grep com.orangead" > service-status.txt
```

### Support Channels

1. **Check Documentation:**

   - [Architecture Guide](ARCHITECTURE.md) - System design
   - [Quick Reference](QUICK_REFERENCE.md) - Common commands
   - [Migration Guide](MIGRATION_GUIDE.md) - Legacy migration

2. **Search Known Issues:**

   - Check project issues for similar problems
   - Review deployment logs for error patterns

3. **Create Support Request:**
   - Include diagnostic information above
   - Describe exact steps to reproduce issue
   - Note any recent changes to system/configuration

---

💡 **Pro Tips:**

- Always test with `--dry-run` or `--check` first
- Use verbose output (`-v`, `-vv`, `-vvv`) for debugging
- Keep backups of working configurations
- Document any custom modifications for troubleshooting
