#!/bin/bash
# Script to verify the macOS API is running properly

# Target host from inventory
TARGET_HOST="192.168.2.9"
API_PORT="9090"

echo "Verifying macOS API on $TARGET_HOST:$API_PORT..."

# Check if the API endpoint is accessible
if curl -s "http://$TARGET_HOST:$API_PORT/health" | grep -q "status"; then
    echo "✅ macOS API health check successful!"
    
    # Get more detailed information
    echo -e "\nAPI Status Information:"
    curl -s "http://$TARGET_HOST:$API_PORT/health" | jq '.'
    
    echo -e "\nSystem Information:"
    curl -s "http://$TARGET_HOST:$API_PORT/system/info" | jq '.'
    
    echo -e "\nVerification completed successfully!"
else
    echo "❌ macOS API health check failed. The service may not be running."
    echo "Checking service status on the target machine..."
    
    # Try to SSH to check service status
    ssh admin@$TARGET_HOST "sudo launchctl list | grep orangead"
    
    echo -e "\nTroubleshooting tips:"
    echo "1. Check if the service is loaded: ssh admin@$TARGET_HOST 'sudo launchctl list | grep orangead'"
    echo "2. Check service logs: ssh admin@$TARGET_HOST 'cat /usr/local/orangead/macos-api/logs/api-error.log'"
    echo "3. Try restarting the service: ssh admin@$TARGET_HOST 'sudo launchctl unload -w /Library/LaunchDaemons/com.orangead.macosapi.plist && sudo launchctl load -w /Library/LaunchDaemons/com.orangead.macosapi.plist'"
fi
