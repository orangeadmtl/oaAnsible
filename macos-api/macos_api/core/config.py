import os
from pathlib import Path

# API Version
APP_VERSION = "1.0.0"

# Security Configuration
# Tailscale uses the 100.64.0.0/10 CGNAT range by default
# https://tailscale.com/kb/1015/100.x-addresses/
TAILSCALE_SUBNET = os.getenv("TAILSCALE_SUBNET", "100.64.0.0/10")

# Paths
# Default to user's home directory if TRACKER_ROOT_DIR is not set
default_tracker_path = os.path.expanduser("~/orangead/tracker")
TRACKER_ROOT = Path(os.getenv("TRACKER_ROOT_DIR", default_tracker_path))

# API URLs
TRACKER_API_URL = os.getenv("TRACKER_API_URL", "http://localhost:8080")

# Command paths
LAUNCHCTL_CMD = "/bin/launchctl"
PS_CMD = "/bin/ps"
READLINK_CMD = "/usr/bin/readlink"
PYTHON_CMD = "/usr/bin/python3"

# Command finder utility
def find_command(command_name):
    possible_paths = [
        f"/usr/bin/{command_name}",
        f"/usr/local/bin/{command_name}",
        f"/opt/homebrew/bin/{command_name}",
        f"/bin/{command_name}",
        f"/sbin/{command_name}"
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    # If not found, return the default path and let the error handling in the code deal with it
    return f"/usr/bin/{command_name}"

# Cache settings
CACHE_TTL = 5  # Cache TTL in seconds

# Health check settings
HEALTH_SCORE_WEIGHTS = {
    "cpu": 0.2,
    "memory": 0.2,
    "disk": 0.2,
    "tracker": 0.2,  # Changed from "player" to "tracker"
    "display": 0.15,
    "network": 0.05
}

HEALTH_SCORE_THRESHOLDS = {
    "critical": 50,
    "warning": 80
}

# Screenshot settings
SCREENSHOT_MAX_HISTORY = 50  # Maximum number of screenshot files to keep
SCREENSHOT_RATE_LIMIT = 1  # seconds
