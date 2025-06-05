#!/bin/bash

# JPR Launch Agents/Daemons Cleanup Script
# This script removes legacy ca.jpr.* Launch Agents and Daemons
# Can be run independently or as part of Ansible automation

set -e

# Define the directories
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LAUNCH_DAEMONS_DIR="/Library/LaunchDaemons"

echo "🧹 Starting JPR cleanup..."

# Unload and remove all ca.jpr.* LaunchAgents
echo "📋 Checking for JPR Launch Agents..."
JPR_AGENTS=$(launchctl list | grep ca.jpr | awk '{print $3}' || true)

if [ -n "$JPR_AGENTS" ]; then
    echo "Found JPR Launch Agents:"
    echo "$JPR_AGENTS"
    
    while IFS= read -r plist; do
        if [ -n "$plist" ]; then
            echo "  🔄 Unloading $plist..."
            launchctl unload "$LAUNCH_AGENTS_DIR/$plist.plist" || echo "    ⚠️  Failed to unload $plist"
            
            echo "  🗑️  Removing $plist.plist..."
            rm -f "$LAUNCH_AGENTS_DIR/$plist.plist" || echo "    ⚠️  Failed to remove $plist.plist"
        fi
    done <<< "$JPR_AGENTS"
else
    echo "  ✅ No JPR Launch Agents found"
fi

# Unload and remove all ca.jpr.* LaunchDaemons (requires sudo)
echo "📋 Checking for JPR Launch Daemons..."
JPR_DAEMONS=$(sudo launchctl list | grep ca.jpr | awk '{print $3}' || true)

if [ -n "$JPR_DAEMONS" ]; then
    echo "Found JPR Launch Daemons:"
    echo "$JPR_DAEMONS"
    
    while IFS= read -r plist; do
        if [ -n "$plist" ]; then
            echo "  🔄 Unloading $plist..."
            sudo launchctl unload "$LAUNCH_DAEMONS_DIR/$plist.plist" || echo "    ⚠️  Failed to unload $plist"
            
            echo "  🗑️  Removing $plist.plist..."
            sudo rm -f "$LAUNCH_DAEMONS_DIR/$plist.plist" || echo "    ⚠️  Failed to remove $plist.plist"
        fi
    done <<< "$JPR_DAEMONS"
else
    echo "  ✅ No JPR Launch Daemons found"
fi

# Verify cleanup
echo "🔍 Verifying cleanup..."

REMAINING_AGENTS=$(launchctl list | grep ca.jpr || true)
REMAINING_DAEMONS=$(sudo launchctl list | grep ca.jpr || true)

if [ -z "$REMAINING_AGENTS" ]; then
    echo "  ✅ JPR Launch Agents cleanup: COMPLETE"
else
    echo "  ⚠️  JPR Launch Agents cleanup: INCOMPLETE"
    echo "      Remaining agents: $REMAINING_AGENTS"
fi

if [ -z "$REMAINING_DAEMONS" ]; then
    echo "  ✅ JPR Launch Daemons cleanup: COMPLETE"
else
    echo "  ⚠️  JPR Launch Daemons cleanup: INCOMPLETE"
    echo "      Remaining daemons: $REMAINING_DAEMONS"
fi

echo "🎉 JPR cleanup completed!"