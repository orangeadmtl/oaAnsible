#!/bin/bash

# Script to run Ansible playbook for staging environment,
# ensuring SSH key from vault is loaded into ssh-agent.

# Determine the directory of this script to reliably find helpers.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SCRIPT_PATH="$SCRIPT_DIR/helpers.sh"

if [ -f "$HELPER_SCRIPT_PATH" ]; then
  # shellcheck source=./helpers.sh
  source "$HELPER_SCRIPT_PATH"
else
  # Fallback basic logging if helpers.sh is missing, and exit.
  echo "[ERROR] Critical: helpers.sh not found at '$HELPER_SCRIPT_PATH'. This script cannot continue."
  exit 1
fi

# Now that helpers.sh is sourced, we can use its functions and variables.
# Ensure we are running from the Ansible root directory.
ensure_ansible_root_dir

# --- SSH Agent Key Loading ---
log_info "Checking and loading SSH key into agent for staging run..."

# Ensure ssh-agent is running for this script's execution context
# Using >/dev/null to suppress the agent's output unless debugging
if ! ssh-add -l >/dev/null 2>&1; then # Check if agent has any keys / is reachable
  log_info "ssh-agent not running or no keys loaded. Starting agent..."
  eval "$(ssh-agent -s)" >/dev/null
  if [ $? -ne 0 ]; then
    log_error "Failed to start ssh-agent. Please start it manually."
    exit 1
  fi
fi

# Variables from helpers.sh or defined here if overridden
VAULT_YML_FILE="$OA_ANSIBLE_GROUP_VARS_DIR/all/vault.yml"
# OA_ANSIBLE_VAULT_PASSWORD_FILE is already defined in helpers.sh

# Check for required dependencies using helper functions
check_vault_password_file
check_yq_installed
check_ansible_vault_installed
check_ansible_installed

log_info "Attempting to add SSH private key from Ansible Vault to ssh-agent..."
if ansible-vault view "$VAULT_YML_FILE" --vault-password-file "$OA_ANSIBLE_VAULT_PASSWORD_FILE" |
  yq -re '.vault_ssh_private_key // ""' |
  ssh-add - >/dev/null 2>&1; then
  log_info "SSH key from vault successfully added/verified in ssh-agent."
else
  if ssh-add -l >/dev/null 2>&1; then
    log_warn "Could not add key (it might already be loaded, or requires a passphrase). An identity is present in the agent."
  else
    log_error "Failed to add SSH key from vault to ssh-agent AND no keys are present in the agent. SSH authentication for Ansible might fail."
    log_error "Make sure 'vault_ssh_private_key' exists in '$VAULT_YML_FILE' and is a valid private key."
    # Consider exiting: exit 1
  fi
fi
# --- End SSH Agent Key Loading ---

log_info "Running Ansible playbook for staging environment..."

# Check if this is the first run by looking for a flag file
FIRST_RUN_FLAG="$OA_ANSIBLE_ROOT_DIR/.first_run_completed"
SUDO_FLAG=""

if [ ! -f "$FIRST_RUN_FLAG" ]; then
  log_info "First-time setup detected. Will ask for sudo password."
  SUDO_FLAG="--ask-become-pass"
fi

# ANSIBLE_CONFIG is set relative to the Ansible root, which ensure_ansible_root_dir should have handled.
ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml -i inventory/staging/hosts.yml $SUDO_FLAG "$@"

PLAYBOOK_EXIT_CODE=$?

# If the playbook runs successfully, create the flag file to indicate first run is complete
if [ $PLAYBOOK_EXIT_CODE -eq 0 ] && [ ! -f "$FIRST_RUN_FLAG" ]; then
  touch "$FIRST_RUN_FLAG"
  log_info "First-time setup completed successfully. Future runs will not require sudo password."
fi

if [ $PLAYBOOK_EXIT_CODE -eq 0 ]; then
  log_info "Ansible playbook completed successfully for staging."
else
  log_error "Ansible playbook failed for staging with exit code $PLAYBOOK_EXIT_CODE."
fi

exit $PLAYBOOK_EXIT_CODE
