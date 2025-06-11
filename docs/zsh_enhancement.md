# ZSH Enhancement for macOS Devices

This document describes the zsh shell enhancements implemented for macOS devices in the OrangeAd infrastructure.

## Overview

The zsh enhancement solution provides a fish-like shell experience without requiring a shell change, addressing issues with key bindings, navigation, and usability in the default zsh configuration.

## Features

- **Key Bindings**: Fixed navigation with arrow keys, home/end keys, and word navigation
- **Syntax Highlighting**: Code and command syntax highlighting similar to fish
- **Autosuggestions**: Command suggestions based on history
- **History Substring Search**: Improved history navigation
- **Oh My Zsh Framework**: Provides a solid foundation for zsh configuration

## Implementation

The solution is implemented as:

1. A shell script (`zshrc_enhancement.sh`) that:
   - Installs Oh My Zsh if not already installed
   - Installs zsh-syntax-highlighting plugin
   - Installs zsh-autosuggestions plugin
   - Creates an enhanced .zshrc configuration
   - Preserves existing PATH and environment settings

2. An Ansible task file (`enhance_zsh.yml`) that:
   - Copies the enhancement script to the target device
   - Executes the script
   - Displays the results
   - Cleans up the script

3. Integration with the base role in `main.yml`

4. A dedicated playbook (`enhance-macos-shell.yml`) for easy deployment

## Deployment

To deploy the zsh enhancements to your macOS devices:

```bash
ansible-playbook -i inventory/your_inventory playbooks/enhance-macos-shell.yml
```

Or to include it as part of another deployment:

```bash
ansible-playbook -i inventory/your_inventory your_playbook.yml --tags "shell,zsh"
```

## Rollback

If you need to revert to the original zsh configuration:

1. The original `.zshrc` is backed up to `.zshrc.bak` during the enhancement process
2. To restore:

```bash
ansible-playbook -i inventory/your_inventory playbooks/rollback-shell.yml
```

Or manually on the device:

```bash
mv ~/.zshrc.bak ~/.zshrc
```

## Customization

The enhanced zsh configuration can be further customized by:

1. Modifying the `zshrc_enhancement.sh` script in `roles/macos/base/files/`
2. Adding additional plugins to the `plugins=()` list in the script
3. Changing the theme by modifying the `ZSH_THEME` variable

## Troubleshooting

If you encounter issues:

1. Verify Oh My Zsh is installed: `ls -la ~/.oh-my-zsh`
2. Check if plugins are installed: `ls -la ~/.oh-my-zsh/custom/plugins/`
3. Examine the current `.zshrc`: `cat ~/.zshrc`
4. Try sourcing the configuration: `source ~/.zshrc`
