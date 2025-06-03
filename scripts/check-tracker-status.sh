#!/bin/bash
# Script to check oaTracker status on a remote Mac

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

echo -e "${BLUE}Checking oaTracker status on ${HOSTNAME}...${NC}"

# Check if the device is accessible via Tailscale
echo -e "${YELLOW}Verifying Tailscale connectivity...${NC}"
if ping -c 1 -W 2 ${HOSTNAME} &> /dev/null; then
    echo -e "${GREEN}✓ Device is reachable via Tailscale${NC}"
else
    echo -e "${RED}✗ Cannot reach device via Tailscale. Check Tailscale status.${NC}"
    exit 1
fi

# Check if the oaTracker service is running
echo -e "${YELLOW}Checking oaTracker service status...${NC}"
ssh ${HOSTNAME} "launchctl list | grep com.orangead.tracker" || {
    echo -e "${RED}✗ oaTracker service is not running${NC}"
    echo -e "${YELLOW}Attempting to start the service...${NC}"
    ssh ${HOSTNAME} "launchctl load -w ~/Library/LaunchAgents/com.orangead.tracker.plist" || {
        echo -e "${RED}✗ Failed to start oaTracker service${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ oaTracker service started${NC}"
}

# Check if the oaTracker API is accessible
echo -e "${YELLOW}Checking oaTracker API...${NC}"
if ssh ${HOSTNAME} "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/stats" | grep -q "200"; then
    echo -e "${GREEN}✓ oaTracker API is accessible${NC}"
else
    echo -e "${RED}✗ oaTracker API is not responding${NC}"
    
    # Check logs for errors
    echo -e "${YELLOW}Checking oaTracker logs...${NC}"
    ssh ${HOSTNAME} "cat /var/log/orangead/tracker.log | tail -n 20"
    
    # Check if Python process is running
    echo -e "${YELLOW}Checking for oaTracker process...${NC}"
    ssh ${HOSTNAME} "ps aux | grep -v grep | grep oaTracker"
    
    # Check port availability
    echo -e "${YELLOW}Checking if port 8080 is in use...${NC}"
    ssh ${HOSTNAME} "sudo lsof -i :8080"
fi

# Check if the device is headless
echo -e "${YELLOW}Checking display status...${NC}"
DISPLAY_COUNT=$(ssh ${HOSTNAME} "system_profiler SPDisplaysDataType | grep -c 'Display Type'" || echo "0")
if [ "$DISPLAY_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠ Device is running in headless mode${NC}"
    echo -e "${BLUE}This may be expected if no physical display is connected.${NC}"
    echo -e "${BLUE}For camera functionality, consider connecting a display or using a headless display adapter.${NC}"
else
    echo -e "${GREEN}✓ Device has ${DISPLAY_COUNT} display(s) connected${NC}"
fi

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Status check complete for ${HOSTNAME}${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
