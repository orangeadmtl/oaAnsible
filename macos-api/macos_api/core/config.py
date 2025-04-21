import os
from pathlib import Path

# API Version
APP_VERSION = "1.0.0"

# Paths
TRACKER_ROOT = Path(os.getenv("TRACKER_ROOT_DIR", "/usr/local/orangead/tracker"))
SCREENSHOT_DIR = Path("/tmp/screenshots")

# Command paths
LAUNCHCTL_CMD = "/bin/launchctl"
PS_CMD = "/bin/ps"
READLINK_CMD = "/usr/bin/readlink"
PYTHON_CMD = "/usr/bin/python3"
SCREENCAPTURE_CMD = "/usr/bin/screencapture"

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
