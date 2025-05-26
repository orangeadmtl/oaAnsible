#!/bin/bash
# OrangeAd Mac Mini Onboarding Script
# This script automates the process of onboarding a Mac Mini M1 device
# with Tailscale, macos-api, and oaTracker.

set -e

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "  ____                              _       _ "
echo " / __ \                            / \     | |"
echo "| |  | |_ __ __ _ _ __   __ _  ___/_\ \ __| |"
echo "| |  | | '__/ _\` | '_ \ / _\` |/ _ \/ _ \/ _\` |"
echo "| |__| | | | (_| | | | | (_| |  __/ \_/ | (_| |"
echo " \____/|_|  \__,_|_| |_|\__, |\___\_/ \_\\__,_|"
echo "                         __/ |                "
echo "                        |___/                 "
echo -e "${NC}"
echo -e "${YELLOW}Mac Mini M1 Onboarding Script${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

# Check if running from the correct directory
if [[ ! -f "main.yml" ]]; then
    echo -e "${RED}Error: This script must be run from the oaAnsible directory.${NC}"
    echo -e "Please run: ${YELLOW}cd /path/to/oaPangaea/oaAnsible && ./scripts/onboard-mac.sh${NC}"
    exit 1
fi

# Collect information from the user
echo -e "${GREEN}Enter target Mac information:${NC}"
read -p "Mac IP address: " TARGET_IP
read -p "SSH username (e.g., admin): " TARGET_USER
read -p "Device hostname (e.g., b3): " TARGET_HOSTNAME

# Validate inputs
if [[ -z "$TARGET_IP" || -z "$TARGET_USER" || -z "$TARGET_HOSTNAME" ]]; then
    echo -e "${RED}Error: All fields are required.${NC}"
    exit 1
fi

# Create temporary inventory file
TEMP_INVENTORY_FILE="/tmp/ansible_onboard_inventory_$(date +%s).yml"
echo "Creating temporary inventory file at $TEMP_INVENTORY_FILE"

cat > "$TEMP_INVENTORY_FILE" << EOF
all:
  children:
    macos:
      hosts:
        $TARGET_HOSTNAME:
          ansible_host: $TARGET_IP
          ansible_user: $TARGET_USER
          ansible_port: 22
EOF

echo -e "${GREEN}Temporary inventory created.${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

# Display onboarding plan
echo -e "${GREEN}Onboarding Plan:${NC}"
echo -e "1. Deploy core macOS configuration and Tailscale"
echo -e "2. Deploy macOS API service"
echo -e "3. Deploy oaTracker application"
echo -e "${BLUE}----------------------------------------${NC}"

# Confirm before proceeding
read -p "Proceed with onboarding? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo -e "${YELLOW}Onboarding cancelled.${NC}"
    rm "$TEMP_INVENTORY_FILE"
    exit 0
fi

# Step 1: Deploy core macOS configuration and Tailscale
echo -e "${GREEN}Step 1: Deploying core macOS configuration and Tailscale...${NC}"
ansible-playbook -i "$TEMP_INVENTORY_FILE" main.yml --tags macos --ask-become-pass --ask-vault-pass

# Step 2: Deploy macOS API
echo -e "${GREEN}Step 2: Deploying macOS API service...${NC}"
ansible-playbook -i "$TEMP_INVENTORY_FILE" playbooks/deploy-macos-api.yml --ask-become-pass

# Step 3: Deploy oaTracker
echo -e "${GREEN}Step 3: Deploying oaTracker application...${NC}"
ansible-playbook -i "$TEMP_INVENTORY_FILE" playbooks/deploy-macos-tracker.yml --ask-become-pass

# Clean up
rm "$TEMP_INVENTORY_FILE"

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Onboarding complete for $TARGET_HOSTNAME ($TARGET_IP)!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Verify the device appears in the oaDashboard"
echo -e "2. Check that camera feeds and tracker status are visible"
echo -e "3. Test device actions (reboot, restart tracker)"
echo -e "${BLUE}----------------------------------------${NC}"
