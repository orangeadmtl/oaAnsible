# Inventory Templates

This directory contains template files for creating new inventory configurations.

## Templates Available

### `environment_template.yml`
Template for creating new project environment inventory files.

**Usage:**
1. Copy the template: `cp templates/environment_template.yml projects/myproject/staging.yml`
2. Replace all UPPERCASE placeholders with actual values
3. Customize service configurations as needed
4. Update host information in the children section

**Key Features:**
- Uses centralized service defaults with environment-specific overrides
- Automatic Python version resolution via `python_runtime.default_version`
- Environment-aware logging and monitoring configuration
- Security settings that adapt to production vs development environments

## Template Usage Guidelines

1. **Always use templates** when creating new environment files
2. **Replace ALL placeholders** - search for UPPERCASE words
3. **Test configurations** in staging before production deployment
4. **Follow naming conventions** established in existing inventory files
5. **Document customizations** when deviating from defaults

## Benefits of Templates

- **Consistency** - All environments start with the same structure
- **Best Practices** - Templates encode proven configuration patterns
- **Reduced Errors** - Less copy-paste mistakes and configuration drift
- **Documentation** - Self-documenting through consistent structure