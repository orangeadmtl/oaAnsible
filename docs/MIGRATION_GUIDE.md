# oaAnsible Migration Guide

Complete guide for migrating from legacy oaAnsible structure to the modern project-centric architecture.

## 🎯 Migration Overview

The oaAnsible system has undergone a complete architectural transformation across 5 phases:

- **From**: Complex legacy structure with redundant configurations and scattered playbooks
- **To**: Modern project-centric inventory with component-based deployment and maintenance infrastructure

## 📋 Migration Checklist

### Pre-Migration Assessment

- [ ] **Inventory Review**: List all existing inventories and their purposes
- [ ] **Playbook Audit**: Identify currently used playbooks and their functions  
- [ ] **Script Usage**: Document which scripts are actively used by teams
- [ ] **Custom Configurations**: Note any custom variables or role modifications
- [ ] **Backup Creation**: Create backup of entire oaAnsible directory

### Migration Execution

- [ ] **Phase 1**: Adopt new inventory structure
- [ ] **Phase 2**: Update deployment workflows  
- [ ] **Phase 3**: Migrate operational scripts
- [ ] **Phase 4**: Update team documentation
- [ ] **Phase 5**: Validate and optimize

## 📁 Inventory Structure Migration

### Legacy → Modern Mapping

**Old Structure:**

```bash
# Legacy inventory structure
inventory/
├── f1-prod.yml                       # Flat files with duplicated config
├── f1-preprod.yml
├── spectra-prod.yml  
├── spectra-preprod.yml
├── alpr-staging.yml
└── evenko-tracker-prod.yml
```

**New Structure:**

```bash
# Modern project-centric structure
inventory/
├── projects/
│   ├── f1/
│   │   ├── prod.yml                   # Clean host definitions only
│   │   ├── preprod.yml
│   │   └── staging.yml
│   ├── spectra/
│   │   ├── prod.yml
│   │   ├── preprod.yml
│   │   └── staging.yml
│   └── evenko/
│       ├── prod.yml
│       └── tracker-prod.yml
├── group_vars/                        # Hierarchical configuration
│   ├── all/                          # Global defaults
│   ├── platforms/                     # Platform-specific  
│   ├── environments/                  # Environment-specific
│   └── {project}_base.yml            # Project-specific
└── components/                        # Component configurations
```

### Inventory File Conversion

**Legacy File Content:**

```yaml
# Old f1-prod.yml (verbose, duplicated config)
all:
  children:
    macos:
      hosts:
        f1-ca-001:
          ansible_host: 100.64.1.10
          ansible_user: admin
          ansible_python_interpreter: /usr/bin/python3
          runtime:
            python:
              version: "3.12.0"
          configure:
            pyenv: true
            homebrew: true
          system:
            homebrew:
              packages:
                - git
                - curl
                - wget
          # ... 50+ more lines of config
```

**Modern File Content:**

```yaml
# New projects/f1/prod.yml (clean, host-focused)
all:
  children:
    macos:
      hosts:
        f1-ca-001:
          ansible_host: 100.64.1.10
          ansible_user: admin
        f1-ca-002:
          ansible_host: 100.64.1.11
          ansible_user: admin
```

**Configuration moved to hierarchy:**

```yaml
# group_vars/all/runtime_versions.yml
runtime:
  python:
    version: "3.12.0"

# group_vars/platforms/macos.yml
ansible_python_interpreter: /usr/bin/python3
configure:
  pyenv: true
  homebrew: true

# group_vars/f1_base.yml
system:
  homebrew:
    packages:
      - git
      - curl
      - wget
```

### Migration Steps

#### Step 1: Create New Structure

```bash
# Create project directories
mkdir -p inventory/projects/{f1,spectra,evenko,alpr}
mkdir -p inventory/group_vars/{all,platforms,environments}
mkdir -p inventory/components
```

#### Step 2: Convert Inventory Files

```bash
# For each legacy inventory file:
# 1. Extract host definitions only
# 2. Move to appropriate projects/{project}/{env}.yml
# 3. Move variables to group_vars hierarchy

# Example conversion script
./scripts/convert_inventory.sh f1-prod.yml projects/f1/prod.yml
```

#### Step 3: Validate New Structure

```bash
# Test inventory loading
ansible-inventory -i projects/f1/prod.yml --list

# Verify variable inheritance
ansible-inventory -i projects/f1/prod.yml --host f1-ca-001
```

## 🚀 Deployment Workflow Migration

### Command Migration

**Legacy Commands:**

```bash
# Old deployment patterns
ansible-playbook main.yml -i f1-prod.yml
ansible-playbook macos-full.yml -i spectra-preprod.yml  
ansible-playbook server_optimizations.yml -i f1-prod.yml
```

**Modern Commands:**

```bash
# New deployment patterns  
./scripts/run projects/f1/prod                                    # Full deployment
./scripts/run projects/spectra/preprod -t macos-api,tracker      # Component deployment
./scripts/run projects/f1/prod -t base,network --dry-run         # Preview changes
```

### Playbook Migration

**Legacy → Modern Mapping:**

| Legacy Playbook | Modern Alternative | Migration Notes |
|-----------------|-------------------|-----------------|
| `main.yml` | `./scripts/run` | Use run script instead |
| `macos-full.yml` | `universal.yml` | Tag-based deployment |
| `server_optimizations.yml` | `universal.yml -t base` | Component-based |
| `ubuntu-full.yml` | `universal.yml -t ml,nvidia` | Platform tags |

**Migration Process:**

```bash
# 1. Identify legacy playbook usage
grep -r "ansible-playbook.*\.yml" scripts/ docs/

# 2. Map to modern equivalents
# macos-full.yml → ./scripts/run projects/f1/prod
# specific-role.yml → ./scripts/run projects/f1/prod -t specific-tag

# 3. Update automation scripts
sed -i 's/ansible-playbook main.yml -i f1-prod.yml/\.\/scripts\/run projects\/f1\/prod/g' deploy.sh
```

## 🛠️ Script Migration

### Script Status Changes

**Active Scripts (✅ Continue Using):**

- `./scripts/run` - **Enhanced** with new inventory support
- `./scripts/genSSH` - **Enhanced** for new structure, still critical for SSH bootstrap

**Deprecated Scripts (⚠️ Migrate Away):**

| Script | Status | Migration Path |
|--------|--------|---------------|
| `./scripts/check` | Deprecated | `./scripts/run --check` or `--dry-run` |
| `./scripts/sync` | Deprecated | `./scripts/run` interactive mode |
| `./scripts/stop` | Deprecated | `playbooks/maintenance/stop_services.yml` |
| `./scripts/reboot` | Deprecated | `playbooks/maintenance/reboot_hosts.yml` |
| `./scripts/format` | Deprecated | `./pangaea.sh format oaAnsible` |

### Script Migration Examples

**Legacy Service Stop:**

```bash
# Old approach
./scripts/stop spectra-preprod --api --tracker

# New approach  
ansible-playbook -i projects/spectra/preprod.yml playbooks/maintenance/stop_services.yml --tags "api,tracker"
```

**Legacy Host Reboot:**

```bash
# Old approach
./scripts/reboot f1-prod f1-ca-001

# New approach
ansible-playbook -i projects/f1/prod.yml playbooks/maintenance/reboot_hosts.yml --limit f1-ca-001 --extra-vars "confirm_reboot=yes"
```

**Legacy Validation:**

```bash
# Old approach
./scripts/check spectra-preprod --check-all

# New approach
./scripts/run projects/spectra/preprod --dry-run
./scripts/run projects/spectra/preprod --check --diff
```

## 🔧 Configuration Migration

### Variable Hierarchy Migration

**Legacy Approach (Duplicated):**

```yaml
# Every inventory file had duplicated config
f1-prod.yml:       # 200+ lines with all config
spectra-prod.yml:  # 200+ lines with mostly same config  
alpr-staging.yml:  # 200+ lines with mostly same config
```

**Modern Approach (DRY):**

```yaml
# Clean separation of concerns
projects/f1/prod.yml:          # 10 lines - hosts only
group_vars/all/:              # Global defaults
group_vars/platforms/macos.yml: # Platform defaults
group_vars/f1_base.yml:       # Project defaults
group_vars/environments/production.yml: # Environment defaults
```

### Variable Migration Process

#### Step 1: Extract Common Variables

```bash
# Find duplicated variables across inventory files
grep -h "ansible_python_interpreter" inventory/*.yml | sort | uniq
grep -h "runtime:" inventory/*.yml | sort | uniq

# Move to group_vars/all/ or group_vars/platforms/
```

#### Step 2: Extract Platform Variables  

```bash
# macOS-specific variables → group_vars/platforms/macos.yml
# Ubuntu-specific variables → group_vars/platforms/ubuntu.yml
```

#### Step 3: Extract Project Variables

```bash
# Project-specific config → group_vars/{project}_base.yml
# Component-specific config → inventory/components/{component}.yml
```

#### Step 4: Extract Environment Variables

```bash
# Production settings → group_vars/environments/production.yml
# Staging settings → group_vars/environments/staging.yml  
```

## 🔒 Security Migration

### Vault Structure Updates

**Legacy Vault (Scattered):**

```yaml
# Old vault.yml - mixed organization
vault_tailscale_key: "key1"
vault_f1_api_key: "key2"  
vault_spectra_api_key: "key3"
vault_ssh_key: "key4"
vault_f1_sudo_pass: "pass1"
vault_spectra_sudo_pass: "pass2"
```

**Modern Vault (Organized):**

```yaml
# New vault.yml - structured organization
vault_network:
  tailscale_auth_key: "key1"
  ssh_private_key: "key4"

vault_api_keys:
  production: "key2"
  preprod: "key3"
  
vault_sudo_passwords:
  default: "pass1"
  f1_specific: "pass1"
  spectra_specific: "pass2"
```

### Security Migration Steps

#### Step 1: Backup Current Vault

```bash
# Create backup of current vault
cp inventory/group_vars/all/vault.yml inventory/group_vars/all/vault.yml.backup

# Document current vault structure
ansible-vault view inventory/group_vars/all/vault.yml > vault_contents.txt
```

#### Step 2: Restructure Vault

```bash
# Edit vault with new structure
ansible-vault edit inventory/group_vars/all/vault.yml

# Update variable references in roles/templates
grep -r "vault_f1_api_key" roles/ --include="*.yml" --include="*.j2"
# Replace with vault_api_keys.production
```

#### Step 3: Update Role References

```bash
# Update role templates to use new vault structure
# Old: {{ vault_f1_api_key }}
# New: {{ vault_api_keys.production }}
```

## 🧪 Testing Migration

### Validation Steps

#### Step 1: Inventory Validation

```bash
# Test inventory loading
ansible-inventory -i projects/f1/prod.yml --list

# Verify host accessibility  
ansible all -i projects/f1/prod.yml -m ping

# Check variable resolution
ansible-inventory -i projects/f1/prod.yml --host f1-ca-001 | jq .
```

#### Step 2: Deployment Testing

```bash
# Test deployment in check mode
./scripts/run projects/f1/preprod --check

# Test component deployment
./scripts/run projects/f1/preprod -t base --dry-run

# Test full deployment on non-production
./scripts/run projects/f1/preprod --dry-run
```

#### Step 3: Service Testing  

```bash
# Test maintenance playbooks
ansible-playbook -i projects/f1/preprod.yml playbooks/maintenance/stop_services.yml --check

# Test service functionality
curl http://f1-ca-001:9090/health
curl http://f1-ca-001:8080/api/stats
```

### Rollback Plan

#### Preparation

```bash
# Create complete backup before migration
tar -czf oaAnsible-backup-$(date +%Y%m%d).tar.gz oaAnsible/

# Document current working deployment commands
echo "Legacy commands that work:" > migration-rollback.md
ansible-playbook main.yml -i f1-preprod.yml --list-tasks >> migration-rollback.md
```

#### Rollback Process

```bash
# If migration fails, restore from backup
cd .. && rm -rf oaAnsible
tar -xzf oaAnsible-backup-$(date +%Y%m%d).tar.gz

# Verify rollback functionality
ansible-playbook main.yml -i f1-preprod.yml --check
```

## 👥 Team Migration

### Communication Plan

#### Pre-Migration

1. **Announcement**: Notify team of upcoming changes and timeline
2. **Training**: Provide training on new structure and commands
3. **Documentation**: Share this migration guide and new documentation

#### During Migration  

1. **Staged Rollout**: Migrate non-production environments first
2. **Support**: Provide dedicated support during transition
3. **Monitoring**: Watch for issues and gather feedback

#### Post-Migration

1. **Validation**: Confirm all team workflows are functioning
2. **Cleanup**: Remove legacy files once migration is confirmed
3. **Optimization**: Identify opportunities for further improvement

### Training Materials

#### Quick Command Reference

```bash
# Legacy → Modern command mapping
echo "Legacy: ansible-playbook main.yml -i f1-prod.yml"
echo "Modern: ./scripts/run projects/f1/prod"
echo ""
echo "Legacy: ansible-playbook macos-full.yml -i spectra-preprod.yml"  
echo "Modern: ./scripts/run projects/spectra/preprod"
echo ""
echo "Legacy: ./scripts/stop spectra-prod --api"
echo "Modern: ansible-playbook -i projects/spectra/prod.yml playbooks/maintenance/stop_services.yml --tags api"
```

#### Team Workflow Updates

```bash
# Update CI/CD pipelines
# Old: ansible-playbook main.yml -i f1-prod.yml
# New: ./scripts/run projects/f1/prod

# Update documentation  
# Old: "Deploy with: ansible-playbook main.yml -i inventory.yml"
# New: "Deploy with: ./scripts/run projects/project/env"

# Update runbooks
# Old: "./scripts/stop inventory-name --service"
# New: "ansible-playbook -i projects/proj/env.yml playbooks/maintenance/stop_services.yml --tags service"
```

## ✅ Migration Completion Checklist

### Technical Completion

- [ ] All inventory files converted to project structure
- [ ] Variable hierarchy established and tested
- [ ] New deployment commands working in all environments  
- [ ] Maintenance playbooks tested and functional
- [ ] Deprecated scripts marked with clear alternatives
- [ ] Vault restructured and validated
- [ ] Legacy files backed up and archived

### Documentation Completion  

- [ ] README.md updated with modern examples
- [ ] Architecture documentation created
- [ ] Quick reference guide available
- [ ] Team trained on new workflows
- [ ] CI/CD pipelines updated
- [ ] Runbooks updated with new procedures

### Operational Completion

- [ ] Production deployments tested and confirmed
- [ ] Monitoring and alerting updated
- [ ] Backup procedures updated
- [ ] Incident response procedures updated
- [ ] Knowledge base articles updated

## 🎉 Post-Migration Benefits

### Achieved Improvements

- **📁 Clean Structure**: Project-centric organization eliminates confusion
- **⚡ Performance**: 94% average role complexity reduction, 60% playbook consolidation
- **🛠️ Professional Tools**: Dedicated maintenance playbooks with safety features
- **📚 Documentation**: Comprehensive guides for all operational aspects
- **🚀 Maintainability**: Modern architecture ready for future enhancements

### Ongoing Optimization

- **Monitor Usage**: Track which components are deployed most frequently
- **Performance**: Measure deployment time improvements  
- **User Experience**: Gather feedback on new workflows
- **Automation**: Identify additional automation opportunities
- **Documentation**: Keep guides updated as system evolves

---

💡 **Remember**: Migration is a process, not an event. Take time to validate each step and ensure team comfort with new workflows before proceeding to production environments.
