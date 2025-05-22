#!/bin/bash

# Script to run Ansible playbook for production environment with safety checks

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

# Check for required dependencies using helper functions
check_ansible_installed
check_vault_password_file

log_warn "⚠️  Running in PRODUCTION environment"
log_warn "Press CTRL+C now to abort, or wait 5 seconds to continue..."
sleep 5

log_info "Running Ansible playbook for production environment..."
ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml -i inventory/production/hosts.yml "$@"

PLAYBOOK_EXIT_CODE=$?

if [ $PLAYBOOK_EXIT_CODE -eq 0 ]; then
  log_info "Ansible playbook completed successfully for production."
else
  log_error "Ansible playbook failed for production with exit code $PLAYBOOK_EXIT_CODE."
fi

exit $PLAYBOOK_EXIT_CODE
