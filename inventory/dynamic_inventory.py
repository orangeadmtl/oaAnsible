#!/usr/bin/env python3
"""
Dynamic inventory script for Ansible that queries Tailscale API
to get macOS devices for management.
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, List, Optional

# Configuration
TAILSCALE_API_KEY = os.environ.get("TAILSCALE_API_KEY", "")
TAILSCALE_TAILNET = os.environ.get("TAILSCALE_TAILNET", "-")  # Default to current tailnet
TAILSCALE_API_URL = f"https://api.tailscale.com/api/v2/tailnet/{TAILSCALE_TAILNET}/devices"
MACOS_TAG = "tag:macos-managed"  # Tag to identify managed macOS devices


def get_tailscale_devices() -> List[Dict]:
    """Query Tailscale API for devices."""
    if not TAILSCALE_API_KEY:
        sys.stderr.write("Error: TAILSCALE_API_KEY environment variable not set\n")
        return []

    headers = {
        "Authorization": f"Bearer {TAILSCALE_API_KEY}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(TAILSCALE_API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get("devices", [])
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Error querying Tailscale API: {e}\n")
        return []


def is_macos_device(device: Dict) -> bool:
    """Check if a device is a macOS device that should be managed."""
    # Check if device has the macOS tag
    if MACOS_TAG in device.get("tags", []):
        return True
    
    # Check OS (fallback)
    os_name = device.get("os", "").lower()
    return "mac" in os_name or "darwin" in os_name


def build_inventory(devices: List[Dict]) -> Dict:
    """Build Ansible inventory from Tailscale devices."""
    inventory = {
        "macos": {
            "hosts": {}
        },
        "_meta": {
            "hostvars": {}
        }
    }

    for device in devices:
        # Skip devices that are not macOS or not online
        if not is_macos_device(device) or not device.get("online", False):
            continue

        # Get device details
        hostname = device.get("hostname", "").split(".")[0]  # Remove domain part
        ip_address = device.get("addresses", [None])[0]  # Get first IP (Tailscale IP)
        
        if not hostname or not ip_address:
            continue

        # Add to hosts
        inventory["macos"]["hosts"][hostname] = hostname
        
        # Add host variables
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": ip_address,
            "ansible_user": "admin",  # Default user, can be overridden in group_vars
            "tailscale_id": device.get("id", ""),
            "tailscale_name": device.get("name", ""),
            "os": device.get("os", ""),
            "tags": device.get("tags", [])
        }

    return inventory


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Tailscale dynamic inventory")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all hosts")
    group.add_argument("--host", help="Get variables for a specific host")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    if args.list:
        devices = get_tailscale_devices()
        inventory = build_inventory(devices)
        print(json.dumps(inventory, indent=2))
    elif args.host:
        # --host output is handled by the _meta field in --list
        print(json.dumps({}))


if __name__ == "__main__":
    main()
