#!/bin/bash
# Script to deploy the macOS API to staging environment

# Change to the oaAnsible directory
cd "$(dirname "$0")/.." || exit 1

# Check if ansible is installed
if ! command -v ansible-playbook &>/dev/null; then
    echo "Error: ansible-playbook command not found. Please install Ansible first."
    echo "You can install it with: pip install ansible"
    exit 1
fi

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
        echo "Unknown option: $1"
        echo "Usage: $0 [--force-restart] [--host hostname]"
        exit 1
        ;;
    esac
done

# Run the deployment playbook
echo "Deploying macOS API to staging environment..."
ansible-playbook playbooks/deploy-macos-api.yml -i inventory/staging/hosts.yml --ask-pass --ask-become-pass

# Check the exit status
DEPLOY_STATUS=$?
if [ $DEPLOY_STATUS -eq 0 ]; then
    echo "Deployment completed successfully!"
    echo "The macOS API should now be running on the target machine."
    echo "You can access it at: http://${TARGET_HOST}:9090"

    # Force restart if requested
    if [ "$FORCE_RESTART" = true ]; then
        echo "\nForcing service restart..."
        echo "You will be prompted for SSH password and sudo password."
        ssh admin@${TARGET_HOST} "sudo launchctl unload /Library/LaunchDaemons/com.orangead.macosapi.plist && sudo launchctl load /Library/LaunchDaemons/com.orangead.macosapi.plist"
        if [ $? -eq 0 ]; then
            echo "Service restarted successfully!"
        else
            echo "Service restart failed. Please check the error messages above."
        fi
    fi
else
    echo "Deployment failed. Please check the error messages above."
fi
