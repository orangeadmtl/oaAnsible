#!/bin/bash
# Script to grant camera permissions to OrangeAd applications
# Will use sudo for all privileged operations

set -e

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OrangeAd Camera Permission Utility${NC}"
echo "This script grants camera access to macOS API and Tracker applications"
echo "----------------------------------------------------------------------"

# Detect user home directory
if [ -n "$SUDO_USER" ]; then
  USER_HOME=$(eval echo ~$SUDO_USER)
else
  USER_HOME=$HOME
fi

# Define paths to the Python executables
MACOS_API_PYTHON="$USER_HOME/orangead/macos-api/.venv/bin/python3"
TRACKER_PYTHON="$USER_HOME/orangead/tracker/.venv/bin/python"

# Verify Python executables exist
if [ ! -f "$MACOS_API_PYTHON" ]; then
  echo -e "${RED}Error: macOS API Python executable not found at $MACOS_API_PYTHON${NC}"
  echo "Make sure the macOS API is properly installed"
  exit 1
fi

if [ ! -f "$TRACKER_PYTHON" ]; then
  echo -e "${RED}Error: Tracker Python executable not found at $TRACKER_PYTHON${NC}"
  echo "Make sure the Tracker is properly installed"
  exit 1
fi

# Define TCC database path
TCC_DB="/Library/Application Support/com.apple.TCC/TCC.db"

# Check if TCC database exists
if [ ! -f "$TCC_DB" ]; then
  echo -e "${RED}Error: TCC database not found at $TCC_DB${NC}"
  exit 1
fi

# Get current timestamp for database updates
TIMESTAMP=$(date +%s)

# Function to grant camera access
grant_camera_access() {
  local app_path="$1"
  local app_identifier="$app_path"
  
  echo -e "${YELLOW}Granting camera access to:${NC} $app_path"
  
  # Check if the app already has camera access
  existing_entry=$(sudo sqlite3 "$TCC_DB" "SELECT service, client, allowed FROM access WHERE service='kTCCServiceCamera' AND client='$app_identifier';")
  
  if [ -z "$existing_entry" ]; then
    # Add new entry
    sudo sqlite3 "$TCC_DB" "INSERT INTO access VALUES('kTCCServiceCamera','$app_identifier',0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1,NULL,NULL,NULL,'UNUSED',$TIMESTAMP);"
    echo -e "${GREEN}Added new camera permission for $app_identifier${NC}"
  else
    # Update existing entry
    sudo sqlite3 "$TCC_DB" "UPDATE access SET allowed=1, prompt_count=1, last_modified=$TIMESTAMP WHERE service='kTCCServiceCamera' AND client='$app_identifier';"
    echo -e "${GREEN}Updated camera permission for $app_identifier${NC}"
  fi
}

# Reset camera permissions using tccutil
echo -e "${YELLOW}Resetting camera permissions...${NC}"
sudo /usr/bin/tccutil reset Camera
echo -e "${GREEN}Camera permissions reset${NC}"

# Grant camera access to both Python executables
grant_camera_access "$MACOS_API_PYTHON"
grant_camera_access "$TRACKER_PYTHON"

# Restart the TCC service to apply changes
echo -e "${YELLOW}Restarting TCC service...${NC}"
sudo launchctl unload /System/Library/LaunchAgents/com.apple.tccd.system.plist 2>/dev/null || true
sudo launchctl load -w /System/Library/LaunchAgents/com.apple.tccd.system.plist 2>/dev/null || true

# Clean up shared memory files that might have wrong permissions
echo -e "${YELLOW}Cleaning up shared memory files...${NC}"
sudo rm -f /tmp//cam.shm /tmp/stop_detection.json 2>/dev/null || true
echo -e "${GREEN}Shared memory files cleaned up${NC}"

# Restart the services
echo -e "${YELLOW}Restarting macOS API and Tracker services...${NC}"
sudo launchctl unload /Library/LaunchDaemons/com.orangead.macosapi.plist 2>/dev/null || true
sudo launchctl load -w /Library/LaunchDaemons/com.orangead.macosapi.plist
sudo launchctl unload /Library/LaunchDaemons/com.orangead.tracker.plist 2>/dev/null || true
sudo launchctl load -w /Library/LaunchDaemons/com.orangead.tracker.plist

echo -e "${GREEN}Services restarted${NC}"
echo "----------------------------------------------------------------------"
echo -e "${GREEN}Camera permissions have been granted successfully!${NC}"
echo "If you still experience camera access issues, you may need to:"
echo "1. Check System Settings > Privacy & Security > Camera"
echo "2. Ensure Python applications have camera access"
echo "3. Reboot the system if permissions don't take effect immediately"

exit 0
