# Development & Testing Playbooks

This directory contains playbooks used for development, testing, and debugging purposes.

## Development Playbooks

### `cleanup.yml` (formerly dev-cleanup.yml)

**Purpose**: Clean up macOS development environment for fresh installation testing

- Removes Homebrew, Python (pyenv), Node.js (nvm), Tailscale
- Reverts system settings to defaults
- **[WARNING] STAGING ONLY**: Has safety checks to prevent production use

**Usage**:

```bash
ansible-playbook playbooks/dev/cleanup.yml -i inventory/staging-target.yml
```

### `enhance-macos-shell.yml`

**Purpose**: Minimal shell enhancement testing

- Tests zsh enhancement functionality
- **Alternative**: Use `universal.yml -t shell` for production

**Usage**:

```bash
ansible-playbook playbooks/dev/enhance-macos-shell.yml -i inventory/test-target.yml
```

## Testing Playbooks

### `test-ml-setup.yml`

**Purpose**: Local ML workstation testing

- Tests oaSentinel setup on localhost
- Used for development validation

**Usage**:

```bash
ansible-playbook playbooks/dev/test-ml-setup.yml
```

## Debugging Playbooks

### `debug-vault.yml`

**Purpose**: Ansible vault debugging

- Tests vault variable loading
- Displays vault passwords for troubleshooting
- **[WARNING] SENSITIVE**: Only use in secure development environments

**Usage**:

```bash
ansible-playbook playbooks/dev/debug-vault.yml -i inventory/target.yml --ask-vault-pass
```

## Development Guidelines

1. **Never use in production**: These playbooks are for development/testing only
2. **Safety first**: Always verify target inventory before running cleanup scripts
3. **Use universal.yml alternatives**: For production deployments, use the universal component framework
4. **Document changes**: Update this README when adding new dev playbooks

## Production Alternatives

Instead of development playbooks, use these production-ready alternatives:

| Dev Playbook              | Production Alternative                     |
| ------------------------- | ------------------------------------------ |
| `cleanup.yml`             | Manual cleanup or fresh OS installation    |
| `enhance-macos-shell.yml` | `universal.yml -t shell`                   |
| `test-ml-setup.yml`       | `universal.yml -t oasentinel-full`         |
| `debug-vault.yml`         | Use `ansible-vault view` or proper logging |
