from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from pathlib import Path

from ..services.display import take_screenshot, get_screenshot_history, get_display_info
from ..models.schemas import ScreenshotInfo
from ..core.config import SCREENSHOT_RATE_LIMIT

router = APIRouter()

@router.get("/screenshots/latest")
async def get_latest_screenshot():
    """Get the latest screenshot."""
    # Check if system is headless
    display_info = get_display_info()
    if not display_info.get("connected", False):
        raise HTTPException(status_code=404, detail="No display connected - screenshots unavailable on headless system")
    
    screenshots = get_screenshot_history()
    if not screenshots:
        raise HTTPException(status_code=404, detail="No screenshots available")
    
    latest = screenshots[-1]
    if not Path(latest.path).exists():
        raise HTTPException(status_code=404, detail="Screenshot file not found")
    
    return FileResponse(latest.path)

@router.get("/screenshots/history")
async def get_screenshots():
    """Get the history of screenshots."""
    # Check if system is headless
    display_info = get_display_info()
    if not display_info.get("connected", False):
        # Return empty list for headless systems instead of error
        return []
    
    return get_screenshot_history()

@router.post("/screenshots/capture")
async def capture_screenshot():
    """Capture a new screenshot."""
    # Check if system is headless
    display_info = get_display_info()
    if not display_info.get("connected", False):
        raise HTTPException(
            status_code=400, 
            detail="Cannot capture screenshot on headless system"
        )
    
    screenshot_path = await take_screenshot()
    if not screenshot_path:
        raise HTTPException(
            status_code=429, 
            detail=f"Please wait {SCREENSHOT_RATE_LIMIT} seconds between screenshots"
        )
    
    return {
        "status": "success",
        "message": "Screenshot captured successfully",
        "path": str(screenshot_path)
    }
