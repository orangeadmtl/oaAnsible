#!/bin/bash
# zshrc_enhancement.sh
# This script enhances the zsh shell experience with key bindings and plugins
# similar to fish shell without requiring a shell change

# Install Oh My Zsh if not already installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
  echo "Installing Oh My Zsh..."
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Install zsh-syntax-highlighting if not already installed
if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ]; then
  echo "Installing zsh-syntax-highlighting..."
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# Install zsh-autosuggestions if not already installed
if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" ]; then
  echo "Installing zsh-autosuggestions..."
  git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi

# Create enhanced .zshrc configuration
cat > "$HOME/.zshrc.enhanced" << 'EOL'
# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set theme with customized prompt to show username and hostname
# Create a custom theme based on robbyrussell that includes username@hostname
cat > "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/robbyrussell-custom.zsh-theme" << 'THEME_EOL'
PROMPT="%(?:%{$fg_bold[green]%}%n@%m:%{$fg_bold[red]%}%n@%m) %{$fg[cyan]%}%c%{$reset_color%} $(git_prompt_info)"

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg_bold[blue]%}git:(%{$fg[red]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%} "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[blue]%}) %{$fg[yellow]%}✗"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$fg[blue]%})"
THEME_EOL

# Use our custom theme
ZSH_THEME="robbyrussell-custom"

# Enable plugins
plugins=(
  git
  zsh-syntax-highlighting
  zsh-autosuggestions
  history-substring-search
)

# Fix bracketed paste mode issues that cause problems with pasted content
# This prevents Oh My Zsh magic functions from interfering with paste operations
DISABLE_MAGIC_FUNCTIONS=true

# Limit autosuggestion buffer size to prevent slow pasting of large content
# This improves paste performance when zsh-autosuggestions plugin is active
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20

# Source Oh My Zsh
source $ZSH/oh-my-zsh.sh

# Additional fix for bracketed paste mode issues
# Completely disable bracketed paste mode as a fallback solution
# This prevents terminal escape sequences from appearing in pasted content
unset zle_bracketed_paste

# Key bindings for better navigation
# bindkey '^[[A' history-substring-search-up
# bindkey '^[[B' history-substring-search-down
# bindkey "^[[H" beginning-of-line      # Home key
# bindkey "^[[F" end-of-line            # End key
# bindkey "^[[3~" delete-char           # Delete key
# bindkey "^[[1;5C" forward-word        # Ctrl+Right
# bindkey "^[[1;5D" backward-word       # Ctrl+Left

# Additional key bindings for macOS Terminal
# bindkey "^[^[[C" forward-word         # Alt+Right
# bindkey "^[^[[D" backward-word        # Alt+Left
# bindkey "^[[1~" beginning-of-line     # Home key alternative
# bindkey "^[[4~" end-of-line           # End key alternative

# Set EDITOR
export EDITOR='vim'

# Set language
export LANG=en_US.UTF-8

# Your custom directory listing aliases using lsd
alias ls='lsd --group-dirs first'
alias l='ls -lah'
alias la='ls -A'
alias ll='ls -alhF'
alias lsa='ls -lah'
alias lt='lsd --tree'

# Source profile for PATH and environment variables
if [ -f "$HOME/.zprofile" ]; then
    source "$HOME/.zprofile"
fi

# Preserve existing PATH configuration
EOL

# Backup original .zshrc if it exists and hasn't been backed up yet
if [ -f "$HOME/.zshrc" ] && [ ! -f "$HOME/.zshrc.bak" ]; then
  echo "Backing up original .zshrc to .zshrc.bak..."
  cp "$HOME/.zshrc" "$HOME/.zshrc.bak"
fi

# Merge existing PATH and environment settings with new enhanced config
if [ -f "$HOME/.zshrc" ]; then
  echo "Merging existing PATH and environment settings from .zshrc..."
  grep -E "export PATH=|eval \"\$\(.*shellenv\)|PYENV_ROOT|NVM_DIR" "$HOME/.zshrc" >> "$HOME/.zshrc.enhanced"
fi

# Also check .zprofile for PATH settings (which is where the base role puts them)
if [ -f "$HOME/.zprofile" ]; then
  echo "Merging existing PATH and environment settings from .zprofile..."
  grep -E "export PATH=|eval \"\$\(.*shellenv\)|PYENV_ROOT|NVM_DIR" "$HOME/.zprofile" >> "$HOME/.zshrc.enhanced"
fi

# Move enhanced config to .zshrc
mv "$HOME/.zshrc.enhanced" "$HOME/.zshrc"

echo "zsh configuration enhanced successfully!"
