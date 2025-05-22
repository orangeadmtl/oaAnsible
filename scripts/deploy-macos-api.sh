#!/bin/bash
# Script to deploy the macOS API to staging environment

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

# Parse command line arguments
FORCE_RESTART=false
TARGET_HOST="192.168.2.41"

while [[ $# -gt 0 ]]; do
    case $1 in
    --force-restart)
        FORCE_RESTART=true
        shift
        ;;
    --host)
        TARGET_HOST="$2"
        shift 2
        ;;
    *)
        log_error "Unknown option: $1"
        log_error "Usage: $0 [--force-restart] [--host hostname]"
        exit 1
        ;;
    esac
done

# Run the deployment playbook
log_info "Deploying macOS API to staging environment..."
ansible-playbook playbooks/deploy-macos-api.yml -i inventory/staging/hosts.yml --ask-pass --ask-become-pass

# Check the exit status
DEPLOY_STATUS=$?
if [ $DEPLOY_STATUS -eq 0 ]; then
    log_info "Deployment completed successfully!"
    log_info "The macOS API should now be running on the target machine."
    log_info "You can access it at: http://${TARGET_HOST}:9090"

    # Force restart if requested
    if [ "$FORCE_RESTART" = true ]; then
        log_info "Forcing service restart..."
        log_info "You will be prompted for SSH password and sudo password."
        ssh admin@${TARGET_HOST} "sudo launchctl unload /Library/LaunchDaemons/com.orangead.macosapi.plist && sudo launchctl load /Library/LaunchDaemons/com.orangead.macosapi.plist"
        if [ $? -eq 0 ]; then
            log_info "Service restarted successfully!"
        else
            log_error "Service restart failed. Please check the error messages above."
        fi
    fi
else
    log_error "Deployment failed. Please check the error messages above."
fi
