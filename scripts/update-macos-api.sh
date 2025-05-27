#!/bin/bash
# Script to update the macos-api on a remote Mac Mini with the new tracker proxy

set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if hostname is provided
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Missing hostname parameter.${NC}"
    echo -e "Usage: $0 <hostname>"
    exit 1
fi

HOSTNAME=$1

echo -e "${BLUE}Updating macos-api on ${HOSTNAME} with tracker proxy...${NC}"

# Check if the device is accessible via Tailscale
echo -e "${YELLOW}Verifying Tailscale connectivity...${NC}"
if ping -c 1 -W 2 ${HOSTNAME} &> /dev/null; then
    echo -e "${GREEN}✓ Device is reachable via Tailscale${NC}"
else
    echo -e "${RED}✗ Cannot reach device via Tailscale. Check Tailscale status.${NC}"
    exit 1
fi

# Create temporary directory for files
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Created temporary directory: ${TEMP_DIR}${NC}"

# Copy the new tracker.py file to the temporary directory
echo -e "${YELLOW}Preparing files...${NC}"
cp "$(pwd)/macos-api/macos_api/routers/tracker.py" "${TEMP_DIR}/"
cp "$(pwd)/macos-api/main.py" "${TEMP_DIR}/"
cp "$(pwd)/macos-api/macos_api/core/config.py" "${TEMP_DIR}/"

# Copy files to the remote Mac
echo -e "${YELLOW}Copying files to ${HOSTNAME}...${NC}"
ssh ${HOSTNAME} "mkdir -p /tmp/macos-api-update"
scp "${TEMP_DIR}/tracker.py" "${HOSTNAME}:/tmp/macos-api-update/"
scp "${TEMP_DIR}/main.py" "${HOSTNAME}:/tmp/macos-api-update/"
scp "${TEMP_DIR}/config.py" "${HOSTNAME}:/tmp/macos-api-update/"

# Deploy the files on the remote Mac
echo -e "${YELLOW}Deploying files on ${HOSTNAME}...${NC}"
ssh ${HOSTNAME} "sudo cp /tmp/macos-api-update/tracker.py /Users/admin/orangead/macos-api/macos_api/routers/ && \
                 sudo cp /tmp/macos-api-update/main.py /Users/admin/orangead/macos-api/ && \
                 sudo cp /tmp/macos-api-update/config.py /Users/admin/orangead/macos-api/macos_api/core/ && \
                 sudo chown -R admin:staff /Users/admin/orangead/macos-api && \
                 sudo chmod -R 755 /Users/admin/orangead/macos-api"

# Restart the macos-api service
echo -e "${YELLOW}Restarting macos-api service...${NC}"
ssh ${HOSTNAME} "sudo launchctl unload -w /Library/LaunchDaemons/com.orangead.macosapi.plist && \
                 sudo launchctl load -w /Library/LaunchDaemons/com.orangead.macosapi.plist"

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "${TEMP_DIR}"
ssh ${HOSTNAME} "rm -rf /tmp/macos-api-update"

# Verify the service is running
echo -e "${YELLOW}Verifying macos-api service...${NC}"
if ssh ${HOSTNAME} "launchctl list | grep com.orangead.macosapi"; then
    echo -e "${GREEN}✓ macos-api service is running${NC}"
else
    echo -e "${RED}✗ macos-api service is not running${NC}"
    exit 1
fi

# Test the tracker proxy endpoint
echo -e "${YELLOW}Testing tracker proxy endpoint...${NC}"
if ssh ${HOSTNAME} "curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/tracker/status"; then
    echo -e "${GREEN}✓ Tracker proxy endpoint is accessible${NC}"
else
    echo -e "${RED}✗ Tracker proxy endpoint is not responding${NC}"
    exit 1
fi

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Update completed successfully for ${HOSTNAME}${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}The oaDashboard should now be able to connect to the oaTracker via the macos-api proxy.${NC}"
echo -e "${YELLOW}Please refresh the dashboard to see the updated tracker status.${NC}"
