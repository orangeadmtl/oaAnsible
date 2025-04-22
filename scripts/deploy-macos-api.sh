#!/bin/bash
# Script to deploy the macOS API to staging environment

# Change to the oaAnsible directory
cd "$(dirname "$0")/.." || exit 1

# Check if ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "Error: ansible-playbook command not found. Please install Ansible first."
    echo "You can install it with: pip install ansible"
    exit 1
fi

# Run the deployment playbook
echo "Deploying macOS API to staging environment..."
ansible-playbook deploy-macos-api.yml -i inventory/staging/hosts.yml --ask-pass --ask-become-pass

# Check the exit status
if [ $? -eq 0 ]; then
    echo "Deployment completed successfully!"
    echo "The macOS API should now be running on the target machine."
    echo "You can access it at: http://192.168.2.9:9090"
else
    echo "Deployment failed. Please check the error messages above."
fi
