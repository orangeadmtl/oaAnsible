# oaAnsible Documentation Index

Complete documentation for the oaAnsible multi-platform orchestration system.

## 🎯 Start Here

| Document                                  | Purpose                                           | Audience                                          |
| ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| **[Script Usage Guide](SCRIPT_USAGE.md)** | Complete examples for all platforms and scenarios | All users - start here for comprehensive guidance |
| **[Quick Reference](QUICK_REFERENCE.md)** | Common commands and quick examples                | Daily operations and quick lookup                 |
| **[WiFi Setup Guide](WIFI_SETUP.md)**     | Complete WiFi configuration walkthrough           | Network configuration setup                       |

## 📚 Complete Documentation

### User Guides

- **[Script Usage Guide](SCRIPT_USAGE.md)** - Comprehensive script usage examples
- **[Quick Reference](QUICK_REFERENCE.md)** - Command reference card
- **[WiFi Setup Guide](WIFI_SETUP.md)** - WiFi configuration guide

### System Documentation

- **[Component Framework](components.md)** - Component system architecture

### Integration Guides

- **[Server API](server-api.md)** - REST API documentation

## 🚀 Quick Navigation

### By Use Case

**New to oaAnsible?** → Start with [Script Usage Guide](SCRIPT_USAGE.md)

**Need a quick command?** → Check [Quick Reference](QUICK_REFERENCE.md)

**Setting up WiFi?** → Follow [WiFi Setup Guide](WIFI_SETUP.md)

**Deploying to production?** → See [Script Usage Guide](SCRIPT_USAGE.md#-mass-deployments)

**Environment configuration?** → Check [Script Usage Guide](SCRIPT_USAGE.md#-environment-configuration)

**Troubleshooting issues?** → Check [Script Usage Guide](SCRIPT_USAGE.md#-troubleshooting)

### By Platform

**macOS Deployments:**

- Full stack: [Script Usage Guide](SCRIPT_USAGE.md#full-macos-stack)
- API only: [Script Usage Guide](SCRIPT_USAGE.md#macos-api-only)
- Tracker: [Script Usage Guide](SCRIPT_USAGE.md#tracker-only)

**Ubuntu Server:**

- Server setup: [Script Usage Guide](SCRIPT_USAGE.md#ubuntu-server-onboarding)
- Full stack: [Script Usage Guide](SCRIPT_USAGE.md#ubuntu-full-stack)

**Mass Operations:**

- All devices: [Script Usage Guide](SCRIPT_USAGE.md#deploy-to-all-devices-in-environment)
- Device groups: [Script Usage Guide](SCRIPT_USAGE.md#deploy-to-device-groups)
- Custom stacks: [Script Usage Guide](SCRIPT_USAGE.md#deploy-to-all-devices-with-specific-stack)

## 🔧 Common Scenarios

### Development Workflow

```bash
# 1. Test in staging with check mode
./scripts/run-staging -l hostname --check

# 2. Deploy to staging
./scripts/run-staging -l hostname

# 3. Verify deployment
./scripts/run-verify staging all -l hostname

# 4. Deploy to production
./scripts/run-prod -l hostname
```

### Component Development

```bash
# Deploy single component for testing
./scripts/run-component staging macos-api -l hostname

# Deploy component stack
./scripts/run-component staging macos-api tracker -l hostname

# Verify component
./scripts/run-verify staging macos_api -l hostname
```

### Mass Operations

```bash
# Deploy to all staging devices
./scripts/run-staging

# Deploy specific components to all production
./scripts/run-component production macos-api

# Deploy custom stack to device group
./scripts/run-component staging base-system python macos-api -l "device1,device2"
```

## 📖 Documentation Standards

### File Organization

- **User-facing guides** in main `/docs` directory
- **Technical documentation** in respective component directories
- **Quick references** linked from main guides

### Content Standards

- **Examples-first approach** - show commands before explaining
- **Copy-pasteable commands** - all examples should work as-is
- **Progressive complexity** - simple examples first, advanced later
- **Clear section headers** - easy navigation and scanning

## 🆘 Getting Help

### Documentation Issues

- Missing information? Check the [Script Usage Guide](SCRIPT_USAGE.md)
- Command not working? Try the [Quick Reference](QUICK_REFERENCE.md)
- WiFi problems? See [WiFi Setup Guide](WIFI_SETUP.md)

### Script Issues

- Use `--check` mode to preview deployments
- Add `-v` flag for verbose output
- Check the [troubleshooting section](SCRIPT_USAGE.md#-troubleshooting)

### Advanced Configuration

- See [Environment Configuration](SCRIPT_USAGE.md#-environment-configuration) for environment setup
- Check [Component Framework](components.md) for component details

---

💡 **Quick Tip**: Bookmark this page and the [Script Usage Guide](SCRIPT_USAGE.md) for easy reference!
