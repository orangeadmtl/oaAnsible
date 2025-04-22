from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from ..services.display import take_screenshot, get_screenshot_history, get_display_info
from ..models.schemas import ScreenshotInfo
from ..core.config import SCREENSHOT_RATE_LIMIT

router = APIRouter()

@router.get("/screenshots/latest")
async def get_latest_screenshot(include_info: bool = False):
    """Get the latest screenshot.
    
    Args:
        include_info: If True, include screenshot metadata in response headers
    
    Returns:
        The screenshot file or error information for headless Macs
    """
    # Get display info to check headless status
    display_info = get_display_info()
    
    # Handle headless Mac gracefully
    if display_info.get("is_headless", True):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "message": "Screenshots unavailable on headless system",
                "is_headless": True,
                "display_info": display_info
            }
        )
    
    # Get screenshot history
    screenshots = get_screenshot_history()
    if not screenshots:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "message": "No screenshots available",
                "is_headless": False
            }
        )
    
    # Get latest screenshot
    latest = screenshots[-1]
    screenshot_path = Path(latest.path)
    
    if not screenshot_path.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "message": "Screenshot file not found",
                "is_headless": False
            }
        )
    
    # Return the file with optional metadata
    response = FileResponse(screenshot_path)
    
    if include_info:
        # Add metadata as headers
        response.headers["X-Screenshot-Timestamp"] = latest.timestamp
        response.headers["X-Screenshot-Resolution"] = f"{latest.resolution[0]}x{latest.resolution[1]}"
        response.headers["X-Screenshot-Size"] = str(latest.size)
    
    return response

@router.get("/screenshots/history")
async def get_screenshots():
    """Get the history of screenshots.
    
    Returns:
        List of screenshot info objects or empty list for headless Macs
    """
    # Get display info
    display_info = get_display_info()
    
    # For headless systems, return empty list with display info
    if display_info.get("is_headless", True):
        return {
            "screenshots": [],
            "is_headless": True,
            "display_info": display_info,
            "message": "Screenshots unavailable on headless system"
        }
    
    # Return screenshot history
    return {
        "screenshots": get_screenshot_history(),
        "is_headless": False,
        "count": len(get_screenshot_history())
    }

@router.post("/screenshots/capture")
async def capture_screenshot():
    """Capture a new screenshot.
    
    Returns:
        Success response with screenshot info or error for headless Macs
    """
    # Take screenshot (the take_screenshot function now handles headless detection internally)
    result = await take_screenshot()
    
    # If screenshot failed
    if not result.get("success", False):
        error_message = result.get("error", "Unknown error")
        status_code = status.HTTP_400_BAD_REQUEST
        
        # Different status code for rate limiting
        if "Rate limit" in error_message:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": error_message,
                "is_headless": result.get("is_headless", False),
                "display_info": result.get("display_info", {}),
                "retry_after": result.get("retry_after")
            }
        )
    
    # Return success with screenshot info
    return {
        "status": "success",
        "message": "Screenshot captured successfully",
        "screenshot": result.get("screenshot", {})
    }

@router.get("/display/info")
async def get_display_information():
    """Get detailed information about connected displays.
    
    Returns:
        Display information including headless status
    """
    return get_display_info()
