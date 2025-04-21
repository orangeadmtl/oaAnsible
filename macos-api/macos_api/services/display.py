import os
import re
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List
from PIL import Image
from ..core.config import PYTHON_CMD, TRACKER_ROOT, SCREENCAPTURE_CMD, SCREENSHOT_DIR, SCREENSHOT_MAX_HISTORY, SCREENSHOT_RATE_LIMIT
from ..services.utils import run_command
from ..models.schemas import ScreenshotInfo
from collections import deque

# Global state for screenshots
screenshots: deque[ScreenshotInfo] = deque(maxlen=SCREENSHOT_MAX_HISTORY)
LAST_SCREENSHOT_FILE = SCREENSHOT_DIR / ".last_screenshot_time"


async def take_screenshot() -> Optional[Path]:
    """Take a screenshot using macOS screencapture command."""
    # Check if system is headless
    display_info = get_display_info()
    if not display_info.get("connected", False):
        print("Cannot take screenshot: No display connected")
        return None
    
    # Check rate limit
    now = datetime.now(timezone.utc)
    last_time = get_last_screenshot_time()

    if last_time:
        time_since_last = (now - last_time).total_seconds()
        print(f"Time since last screenshot: {time_since_last} seconds")
        if time_since_last < SCREENSHOT_RATE_LIMIT:
            print(f"Rate limit hit: Need to wait {SCREENSHOT_RATE_LIMIT - time_since_last:.1f} more seconds")
            return None
    else:
        print("No previous screenshot time recorded")

    timestamp = now
    filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    path = SCREENSHOT_DIR / filename
    print(f"Taking new screenshot: {filename}")

    try:
        # Ensure screenshot directory exists
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

        # Take screenshot using macOS screencapture command
        # -x: No sound
        # -C: Capture the cursor
        result = subprocess.run(
            [SCREENCAPTURE_CMD, "-x", "-C", str(path)],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        if result.returncode != 0 or not path.exists():
            print(f"Screenshot failed: {result.stderr}")
            return None
            
        # Process the screenshot
        with Image.open(path) as img:
            # Calculate dimensions for FullHD while maintaining aspect ratio
            width, height = img.size
            # For portrait orientation, use 1080p vertically
            if height > width:
                target_height = 1920
                target_width = 1080
            else:
                target_width = 1920
                target_height = 1080

            # Calculate scale to fit the target resolution
            scale = min(target_width / width, target_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            # Resize the image with high-quality settings
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized.save(path, "JPEG", quality=85, optimize=True)

            print(f"Screenshot dimensions: {resized.size}")

            # Check if image is not all black or white
            pixels = list(resized.getdata())[:100]
            if all(p[0] == 0 and p[1] == 0 and p[2] == 0 for p in pixels):
                print("Screenshot appears to be all black")
                path.unlink(missing_ok=True)
                return None
            if all(p[0] == 255 and p[1] == 255 and p[2] == 255 for p in pixels):
                print("Screenshot appears to be all white")
                path.unlink(missing_ok=True)
                return None

            # Save screenshot info
            screenshot_info = ScreenshotInfo(
                timestamp=timestamp.isoformat(), 
                filename=filename, 
                path=str(path), 
                resolution=(new_width, new_height), 
                size=path.stat().st_size
            )
            screenshots.append(screenshot_info)

            # Clean up old files
            while len(screenshots) > SCREENSHOT_MAX_HISTORY:
                old = screenshots.popleft()
                Path(old.path).unlink(missing_ok=True)

            # Update last screenshot time only on success
            set_last_screenshot_time(timestamp)
            print("Screenshot info saved and timestamp updated")
            return path

    except Exception as e:
        print(f"Screenshot error: {str(e)}")
        if path.exists():
            path.unlink()
        return None


def get_last_screenshot_time() -> Optional[datetime]:
    """Get the last screenshot time from file."""
    try:
        if LAST_SCREENSHOT_FILE.exists():
            timestamp = float(LAST_SCREENSHOT_FILE.read_text().strip())
            last_time = datetime.fromtimestamp(timestamp, timezone.utc)

            # Check if the timestamp is too old (e.g., from a previous session)
            now = datetime.now(timezone.utc)
            if (now - last_time).total_seconds() > 3600:  # If older than 1 hour
                LAST_SCREENSHOT_FILE.unlink(missing_ok=True)
                return None
            return last_time
    except (ValueError, OSError):
        LAST_SCREENSHOT_FILE.unlink(missing_ok=True)
    return None


def set_last_screenshot_time(timestamp: datetime) -> None:
    """Save the last screenshot time to file."""
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        LAST_SCREENSHOT_FILE.write_text(str(timestamp.timestamp()))
    except OSError as e:
        print(f"Error saving timestamp: {e}")


def get_display_info() -> Dict:
    """Get display configuration and status for macOS."""
    display_info = {
        "connected": False,
        "resolution": "unknown",
        "refresh_rate": "unknown",
        "vendor": "unknown",
        "model": "unknown",
        "displays": []
    }
    
    try:
        # Use system_profiler to get display information
        cmd = ["system_profiler", "SPDisplaysDataType", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                displays_data = data.get("SPDisplaysDataType", [])
                
                if displays_data:
                    display_info["connected"] = True
                    
                    # Process each display
                    displays = []
                    for display in displays_data:
                        display_details = {}
                        
                        # Extract resolution
                        resolution = display.get("spdisplays_resolution", "unknown")
                        if isinstance(resolution, str) and "x" in resolution:
                            display_details["resolution"] = resolution
                        
                        # Extract refresh rate
                        refresh_rate = display.get("spdisplays_refresh", "unknown")
                        if refresh_rate:
                            display_details["refresh_rate"] = refresh_rate
                            
                        # Extract vendor/model
                        vendor = display.get("spdisplays_vendor", "unknown")
                        if vendor:
                            display_details["vendor"] = vendor
                            
                        model = display.get("spdisplays_device_name", "unknown")
                        if model:
                            display_details["model"] = model
                            
                        # Add to displays list
                        displays.append(display_details)
                    
                    display_info["displays"] = displays
                    
                    # Set primary display info if available
                    if displays:
                        primary = displays[0]  # Assume first display is primary
                        display_info["resolution"] = primary.get("resolution", "unknown")
                        display_info["refresh_rate"] = primary.get("refresh_rate", "unknown")
                        display_info["vendor"] = primary.get("vendor", "unknown")
                        display_info["model"] = primary.get("model", "unknown")
            except json.JSONDecodeError:
                pass
                
    except Exception as e:
        print(f"Error getting display info: {e}")
    
    return display_info


def get_screenshot_history() -> List[ScreenshotInfo]:
    """Get the history of screenshots."""
    # If screenshots deque is empty, try to populate from directory
    if not screenshots:
        try:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            screenshot_files = sorted(
                [f for f in SCREENSHOT_DIR.glob("screenshot_*.png") if f.is_file()],
                key=lambda f: f.stat().st_mtime
            )
            
            for file in screenshot_files[-SCREENSHOT_MAX_HISTORY:]:
                try:
                    # Extract timestamp from filename
                    timestamp_str = file.stem.replace("screenshot_", "")
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # Get image dimensions
                    with Image.open(file) as img:
                        resolution = img.size
                    
                    # Create ScreenshotInfo
                    screenshot_info = ScreenshotInfo(
                        timestamp=timestamp.replace(tzinfo=timezone.utc).isoformat(),
                        filename=file.name,
                        path=str(file),
                        resolution=resolution,
                        size=file.stat().st_size
                    )
                    screenshots.append(screenshot_info)
                except Exception:
                    continue
        except Exception as e:
            print(f"Error loading screenshot history: {e}")
    
    return list(screenshots)
