from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    cpu: Dict
    memory: Dict
    disk: Dict
    network: Optional[Dict] = None
    boot_time: Optional[float] = None


class TrackerStatus(BaseModel):
    service_status: str
    tracker_status: str
    display_connected: bool
    healthy: bool
    error: Optional[str] = None


class VersionInfo(BaseModel):
    api: str
    python: str
    tailscale: Optional[str] = None
    system: Dict[str, str]


class DeviceInfo(BaseModel):
    type: str = "Mac"
    series: str
    hostname: str
    is_headless: bool = False


class HealthScore(BaseModel):
    cpu: float
    memory: float
    disk: float
    tracker: float  # Changed from "player" to "tracker"
    display: float
    network: float
    overall: float
    status: Dict[str, bool]


class ScreenshotInfo(BaseModel):
    timestamp: str
    filename: str
    path: str
    resolution: Optional[Tuple[int, int]] = None
    size: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    hostname: str
    timestamp: str
    timestamp_epoch: int
    version: VersionInfo
    metrics: SystemMetrics
    deployment: Dict
    tracker: TrackerStatus  # Changed from "player" to "tracker"
    health_scores: HealthScore
    device_info: DeviceInfo
    _cache_info: Optional[Dict] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    timestamp: str
    timestamp_epoch: int
    error: str
