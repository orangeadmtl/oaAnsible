from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Dict
import platform

from ..services.system import get_system_metrics, get_device_info, get_version_info
from ..services.tracker import check_tracker_status, get_deployment_info
from ..services.display import get_display_info
from ..services.health import calculate_health_score, get_health_summary
from ..services.utils import cache_with_ttl
from ..core.config import CACHE_TTL, APP_VERSION
from ..models.schemas import HealthResponse, ErrorResponse

router = APIRouter()


# Cache expensive operations
@cache_with_ttl(CACHE_TTL)
def get_cached_metrics() -> Dict:
    return get_system_metrics()


@cache_with_ttl(CACHE_TTL)
def get_cached_display_info() -> Dict:
    return get_display_info()


@cache_with_ttl(CACHE_TTL)
def get_cached_deployment_info() -> Dict:
    return get_deployment_info()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Get comprehensive system health status and metrics."""
    try:
        # Use cached versions of expensive operations
        metrics = get_cached_metrics()
        deployment = get_cached_deployment_info()
        display_info = get_cached_display_info()
        tracker = check_tracker_status()  # Don't cache this as it needs to be real-time
        device = get_device_info()

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Calculate health scores
        health_scores = calculate_health_score(metrics, tracker, display_info)

        # Determine overall status
        status = "online"
        if not tracker["healthy"]:
            status = "maintenance" if tracker["service_status"] == "active" else "offline"

        # Get macOS version info for system details
        version_info = get_version_info()

        # Prepare system information
        system_info = {
            "os_version": version_info.get("macos_version", platform.release()),
            "kernel_version": platform.release(),
            "uptime": version_info.get("uptime", {}).get("formatted", "Unknown"),
            "uptime_human": version_info.get("uptime", {}).get("formatted", "Unknown"),
            "boot_time": version_info.get("uptime", {}).get("seconds", 0),
            "hostname": device["hostname"],
            "cpu_model": version_info.get("processor", platform.processor()),
            "cpu_cores": metrics.get("cpu", {}).get("cores", 0),
            "memory_total": metrics.get("memory", {}).get("total", 0),
            "architecture": version_info.get("machine_type", platform.machine()),
            "model": version_info.get("product_name", "Mac"),
        }

        # Format response to match oaDashboard expectations
        return {
            "status": status,
            "hostname": device["hostname"],
            "timestamp": now.isoformat(),
            "timestamp_epoch": int(now.timestamp()),
            "version": {
                "api": APP_VERSION,
                "python": platform.python_version(),
                "tailscale": version_info.get("tailscale_version"),
                "system": {
                    "platform": platform.system(),
                    "release": platform.release(),
                    "os": f"{platform.system()} {platform.release()}",
                    "type": device["type"],
                    "series": device["series"],
                },
            },
            "metrics": metrics,
            "deployment": deployment,
            "tracker": tracker,  # Using tracker instead of player for Mac devices
            "health_scores": health_scores,
            "device_info": device,  # Device info with headless status
            "system": system_info,  # Detailed system information
            "display": {
                "connected_displays": len(display_info.get("displays", [])),
                "main_display": display_info.get("main_display", {}),
                "all_displays": display_info.get("displays", []),
                "is_headless": device.get("is_headless", False),
                "headless_reason": display_info.get("headless_reason", None) if device.get("is_headless", False) else None,
            },
            "capabilities": {
                "supports_camera_stream": True,
                "supports_tracker_restart": True,
                "supports_reboot": True,
                "supports_ssh": True,
                "device_has_camera_support": True,
            },
            "_cache_info": {
                "metrics": get_cached_metrics.cache_info(),
                "display": get_cached_display_info.cache_info(),
                "deployment": get_cached_deployment_info.cache_info(),
            },
        }
    except Exception as e:
        now = datetime.now(timezone.utc)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(status="error", timestamp=now.isoformat(), timestamp_epoch=int(now.timestamp()), error=str(e)).dict(),
        )


@router.get("/health/summary")
async def health_summary():
    """Get a summary of system health with recommendations."""
    try:
        metrics = get_cached_metrics()
        tracker = check_tracker_status()
        display_info = get_cached_display_info()

        return get_health_summary(metrics, tracker, display_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
