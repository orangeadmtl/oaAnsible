from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
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


class MacOSDisplayInfo(BaseModel):
    resolution: Optional[str] = None
    refresh_rate: Optional[float] = None
    connected: bool = False
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None


class DisplayInfo(BaseModel):
    connected_displays: int = 0
    main_display: Optional[MacOSDisplayInfo] = None
    all_displays: Optional[List[MacOSDisplayInfo]] = None
    is_headless: bool = False
    headless_reason: Optional[str] = None


class MacOSSystemInfo(BaseModel):
    os_version: str
    kernel_version: str
    uptime: str
    uptime_human: Optional[str] = None
    boot_time: Optional[float] = None
    hostname: str
    cpu_model: str
    cpu_cores: int
    memory_total: int
    architecture: str
    model: Optional[str] = None
    serial_number: Optional[str] = None


class SecurityFeature(BaseModel):
    enabled: bool
    status: str
    details: Optional[Dict[str, Any]] = None
    raw_output: Optional[str] = None
    error: Optional[str] = None


class SecurityUpdates(BaseModel):
    has_updates: bool
    security_updates_available: bool
    security_updates: Optional[List[str]] = None
    recommended_updates: Optional[List[str]] = None
    last_security_update: Optional[Dict[str, Any]] = None
    update_policy: Optional[Dict[str, bool]] = None
    status: str
    raw_output: Optional[str] = None
    error: Optional[str] = None


class SecurityOverview(BaseModel):
    status: str
    score: int
    max_score: int
    percentage: float
    features: Dict[str, Union[SecurityFeature, SecurityUpdates]]
    recommendations: List[str]


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
    system: Optional[MacOSSystemInfo] = None
    security: Optional[SecurityOverview] = None
    display: Optional[DisplayInfo] = None
    _cache_info: Optional[Dict] = None


class CameraInfo(BaseModel):
    id: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    is_built_in: bool = False
    is_connected: bool = True
    resolution: Optional[str] = None
    location: Optional[str] = None  # e.g., "Built-in", "USB", etc.


class CameraListResponse(BaseModel):
    cameras: List[CameraInfo]
    count: int
    has_camera: bool


class ErrorResponse(BaseModel):
    status: str = "error"
    timestamp: str
    timestamp_epoch: int
    error: str
