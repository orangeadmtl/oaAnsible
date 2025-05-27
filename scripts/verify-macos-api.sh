#!/bin/bash
# Script to verify the macOS API is running properly

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

# Target host from inventory
TARGET_HOST="192.168.2.9"
API_PORT="9090"

log_info "Verifying macOS API on $TARGET_HOST:$API_PORT..."

# Check if the API endpoint is accessible
if curl -s "http://$TARGET_HOST:$API_PORT/health" | grep -q "status"; then
    log_info "✅ macOS API health check successful!"
    
    # Get more detailed information
    log_info "API Status Information:"
    curl -s "http://$TARGET_HOST:$API_PORT/health" | jq '.'
    
    log_info "System Information:"
    curl -s "http://$TARGET_HOST:$API_PORT/system/info" | jq '.'
    
    log_info "Verification completed successfully!"
else
    log_error "❌ macOS API health check failed. The service may not be running."
    log_info "Checking service status on the target machine..."
    
    # Try to SSH to check service status
    ssh admin@$TARGET_HOST "sudo launchctl list | grep orangead"
    
    log_info "Troubleshooting tips:"
    log_info "1. Check if the service is loaded: ssh admin@$TARGET_HOST 'sudo launchctl list | grep orangead'"
    log_info "2. Check service logs: ssh admin@$TARGET_HOST 'cat ~/orangead/macos-api/logs/api-error.log'"
    log_info "3. Try restarting the service: ssh admin@$TARGET_HOST 'sudo launchctl unload -w /Library/LaunchDaemons/com.orangead.macosapi.plist && sudo launchctl load -w /Library/LaunchDaemons/com.orangead.macosapi.plist'"
fi

# Check if jq is installed (needed for JSON formatting)
check_command_installed() {
    local command_name=$1
    if ! command -v "$command_name" &>/dev/null; then
        log_error "$command_name command not found. This script may not work correctly."
        return 1
    fi
    return 0
}

# Verify jq is available
check_command_installed "jq" || log_warn "jq is not installed. JSON output will not be formatted."
