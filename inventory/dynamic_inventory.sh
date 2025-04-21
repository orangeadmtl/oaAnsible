#!/bin/bash
# Wrapper script for dynamic_inventory.py that ensures the Python script has execute permissions

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INVENTORY_SCRIPT="$SCRIPT_DIR/dynamic_inventory.py"

# Ensure the Python script is executable
chmod +x "$INVENTORY_SCRIPT"

# Pass all arguments to the Python script
"$INVENTORY_SCRIPT" "$@"
