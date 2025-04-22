import os
import re
import json
import time
import asyncio
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


async def take_screenshot() -> Optional[Dict]:
    """Take a screenshot using macOS screencapture command.
    
    Returns:
        Dict with screenshot info or None if screenshot failed
    """
    # Check if system is headless
    display_info = get_display_info()
    is_headless = not display_info.get("connected", False)
    
    # Check rate limit
    now = datetime.now(timezone.utc)
    last_time = get_last_screenshot_time()

    if last_time:
        time_since_last = (now - last_time).total_seconds()
        print(f"Time since last screenshot: {time_since_last} seconds")
        if time_since_last < SCREENSHOT_RATE_LIMIT:
            print(f"Rate limit hit: Need to wait {SCREENSHOT_RATE_LIMIT - time_since_last:.1f} more seconds")
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": SCREENSHOT_RATE_LIMIT - time_since_last
            }
    
    # Ensure screenshot directory exists
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = now
    filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    path = SCREENSHOT_DIR / filename
    print(f"Taking new screenshot: {filename}")

    try:
        # Find screencapture command if not in expected location
        screencapture_cmd = SCREENCAPTURE_CMD
        if not os.path.exists(screencapture_cmd):
            try:
                # Try to find screencapture using 'which' command
                process = await asyncio.create_subprocess_exec(
                    "which", "screencapture",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0 and stdout:
                    screencapture_cmd = stdout.decode().strip()
                else:
                    # Try common locations as fallback
                    for path in ["/usr/sbin/screencapture", "/usr/local/bin/screencapture", "/opt/homebrew/bin/screencapture"]:
                        if os.path.exists(path) and os.access(path, os.X_OK):
                            screencapture_cmd = path
                            break
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not locate screencapture command: {str(e)}",
                    "is_headless": False
                }
        
        # Log the path being used
        print(f"Using screencapture command at: {screencapture_cmd}")
        
        # Take screenshot using macOS screencapture command with improved options
        # -x: No sound
        # -C: Capture the cursor
        # -t png: Ensure PNG format
        # -S: Capture the screen (not a selection)
        # -o: No shadow for windows
        result = subprocess.run(
            [screencapture_cmd, "-x", "-C", "-t", "png", "-S", "-o", str(path)],
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
            timeout=10    # Add timeout to prevent hanging
        )
        
        if result.returncode != 0 or not path.exists():
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            print(f"Screenshot failed: {error_msg}")
            return {
                "success": False,
                "error": f"Screenshot command failed: {error_msg}",
                "exit_code": result.returncode
            }
            
        # Process the screenshot
        with Image.open(path) as img:
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate dimensions for FullHD while maintaining aspect ratio
            if orig_height > orig_width:
                # Portrait orientation
                target_height = 1920
                target_width = 1080
            else:
                # Landscape orientation
                target_width = 1920
                target_height = 1080

            # Calculate scale to fit the target resolution
            scale = min(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)

            # Resize the image with high-quality settings
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as JPEG for smaller file size
            jpeg_path = path.with_suffix('.jpg')
            # Convert to RGB mode before saving as JPEG (JPEG doesn't support alpha channel)
            if resized.mode == 'RGBA':
                resized = resized.convert('RGB')
            resized.save(jpeg_path, "JPEG", quality=85, optimize=True)
            
            # Remove original PNG file
            path.unlink(missing_ok=True)
            path = jpeg_path
            filename = path.name

            print(f"Screenshot resized: {orig_width}x{orig_height} → {new_width}x{new_height}")

            # Check if image is not all black or white (potential error)
            # Sample more pixels for better detection
            pixels = list(resized.getdata())[:1000]  # Sample more pixels
            # Count black and white pixels instead of requiring all to be black/white
            black_count = sum(1 for p in pixels if p[0] < 5 and p[1] < 5 and p[2] < 5)
            white_count = sum(1 for p in pixels if p[0] > 250 and p[1] > 250 and p[2] > 250)
            
            # Calculate percentages
            black_percent = (black_count / len(pixels)) * 100
            white_percent = (white_count / len(pixels)) * 100
            
            # Only consider it an error if >95% black or white
            mostly_black = black_percent > 95
            mostly_white = white_percent > 95
            
            print(f"Screenshot analysis: {black_percent:.1f}% black, {white_percent:.1f}% white")
            
            # For headless Macs, we'll accept black screens as valid
            # This allows capturing the actual state of the display
            if (mostly_black or mostly_white) and not is_headless:
                error_type = "mostly black" if mostly_black else "mostly white"
                print(f"Screenshot appears to be {error_type}, but keeping it for headless Mac")
                # We'll continue with the screenshot instead of returning an error

            # Save screenshot info
            file_size = path.stat().st_size
            screenshot_info = ScreenshotInfo(
                timestamp=timestamp.isoformat(), 
                filename=filename, 
                path=str(path), 
                resolution=(new_width, new_height), 
                size=file_size
            )
            screenshots.append(screenshot_info)

            # Clean up old files
            while len(screenshots) > SCREENSHOT_MAX_HISTORY:
                old = screenshots.popleft()
                Path(old.path).unlink(missing_ok=True)

            # Update last screenshot time only on success
            set_last_screenshot_time(timestamp)
            
            return {
                "success": True,
                "screenshot": {
                    "timestamp": timestamp.isoformat(),
                    "filename": filename,
                    "path": str(path),
                    "resolution": {
                        "width": new_width,
                        "height": new_height,
                        "original_width": orig_width,
                        "original_height": orig_height
                    },
                    "size_bytes": file_size,
                    "size_formatted": f"{file_size / 1024:.1f} KB"
                }
            }

    except subprocess.TimeoutExpired:
        print("Screenshot command timed out")
        return {
            "success": False,
            "error": "Screenshot command timed out"
        }
    except Exception as e:
        print(f"Screenshot error: {str(e)}")
        if path.exists():
            path.unlink(missing_ok=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


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
    """Get display configuration and status for macOS.
    
    This function uses multiple methods to detect displays and determine
    if the Mac is headless, providing detailed information about connected displays.
    
    Returns:
        Dict with display information including headless status
    """
    display_info = {
        "connected": False,
        "is_headless": True,  # Default to headless until proven otherwise
        "resolution": "unknown",
        "refresh_rate": "unknown",
        "vendor": "unknown",
        "model": "unknown",
        "displays": [],
        "detection_method": "none"
    }
    
    # Method 1: Use system_profiler (most reliable but slower)
    try:
        cmd = ["system_profiler", "SPDisplaysDataType", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=5)
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                displays_data = data.get("SPDisplaysDataType", [])
                
                # Check if we have actual display devices (not just graphics cards)
                real_displays = []
                for display in displays_data:
                    # Skip entries that are just graphics cards without displays
                    if "spdisplays_resolution" in display:
                        real_displays.append(display)
                
                if real_displays:
                    display_info["connected"] = True
                    display_info["is_headless"] = False
                    display_info["detection_method"] = "system_profiler"
                    
                    # Process each display
                    displays = []
                    for display in real_displays:
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
                        
                        # Extract connection type
                        connection = display.get("spdisplays_connection_type", "unknown")
                        if connection:
                            display_details["connection"] = connection
                            
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
        print(f"Error getting display info via system_profiler: {e}")
    
    # Method 2: If still headless, try using ioreg as a backup method
    if display_info["is_headless"]:
        try:
            cmd = ["ioreg", "-l", "-d", "2", "-c", "IODisplay"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=3)
            
            if result.returncode == 0 and "IODisplayConnect" in result.stdout:
                # IODisplayConnect presence indicates a display is connected
                display_info["connected"] = True
                display_info["is_headless"] = False
                display_info["detection_method"] = "ioreg"
        except Exception as e:
            print(f"Error getting display info via ioreg: {e}")
    
    # Method 3: Try CGDisplayBounds via Python script as a last resort
    if display_info["is_headless"]:
        try:
            # Create a temporary Python script that uses Objective-C bridge
            script_content = """
#!/usr/bin/env python3
import json
from ctypes import cdll, c_int32, POINTER, Structure

class CGRect(Structure):
    _fields_ = [("origin_x", c_int32), ("origin_y", c_int32), ("width", c_int32), ("height", c_int32)]

try:
    # Load CoreGraphics framework
    core_graphics = cdll.LoadLibrary("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")
    
    # Get number of displays
    CGGetActiveDisplayList = core_graphics.CGGetActiveDisplayList
    CGGetActiveDisplayList.argtypes = [c_int32, POINTER(c_int32), POINTER(c_int32)]
    CGGetActiveDisplayList.restype = c_int32
    
    # Get display bounds
    CGDisplayBounds = core_graphics.CGDisplayBounds
    CGDisplayBounds.argtypes = [c_int32]
    CGDisplayBounds.restype = CGRect
    
    # Get active displays
    max_displays = 16
    display_count = c_int32(0)
    display_list = (c_int32 * max_displays)()
    
    result = CGGetActiveDisplayList(max_displays, display_list, display_count)
    
    if result == 0 and display_count.value > 0:
        displays = []
        for i in range(display_count.value):
            display_id = display_list[i]
            bounds = CGDisplayBounds(display_id)
            displays.append({
                "id": display_id,
                "bounds": {
                    "x": bounds.origin_x,
                    "y": bounds.origin_y,
                    "width": bounds.width,
                    "height": bounds.height
                }
            })
        
        print(json.dumps({"success": True, "displays": displays, "count": display_count.value}))
    else:
        print(json.dumps({"success": False, "error": "No displays found"}))
        
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
"""
            
            # Write script to temporary file
            temp_script = Path("/tmp/check_displays.py")
            temp_script.write_text(script_content)
            temp_script.chmod(0o755)
            
            # Execute script
            result = subprocess.run([str(temp_script)], capture_output=True, text=True, check=False, timeout=3)
            temp_script.unlink(missing_ok=True)
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    if data.get("success") and data.get("count", 0) > 0:
                        display_info["connected"] = True
                        display_info["is_headless"] = False
                        display_info["detection_method"] = "coregraphics"
                        
                        # Add display information
                        cg_displays = []
                        for display in data.get("displays", []):
                            bounds = display.get("bounds", {})
                            if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                                cg_displays.append({
                                    "resolution": f"{bounds.get('width')}x{bounds.get('height')}",
                                    "id": display.get("id"),
                                    "bounds": bounds
                                })
                        
                        # If we have display info from CoreGraphics but not from system_profiler
                        if cg_displays and not display_info["displays"]:
                            display_info["displays"] = cg_displays
                            
                            # Set primary display resolution if available
                            if cg_displays:
                                primary = cg_displays[0]
                                if "resolution" in primary:
                                    display_info["resolution"] = primary["resolution"]
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Error getting display info via CoreGraphics: {e}")
    
    # Final headless determination
    display_info["is_headless"] = not display_info["connected"]
    
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
