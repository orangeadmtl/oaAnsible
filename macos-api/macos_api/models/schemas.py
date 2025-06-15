from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field


class TemperatureMetrics(BaseModel):
    timestamp: str
    cpu_temperature: Optional[float] = None
    thermal_state: Dict
    thermal_health: str = "unknown"
    thermal_issues: Optional[List[str]] = None
    temperature_unit: str = "celsius"
    method: str = "cpu_usage_estimation"
    capabilities: Dict[str, bool]


class SystemMetrics(BaseModel):
    cpu: Dict
    memory: Dict
    disk: Dict
    network: Optional[Dict] = None
    boot_time: Optional[float] = None
    temperature: Optional[TemperatureMetrics] = None


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


class HealthScore(BaseModel):
    cpu: float
    memory: float
    disk: float
    tracker: float  # Changed from "player" to "tracker"
    display: float
    network: float
    overall: float
    status: Dict[str, bool]


class HealthResponse(BaseModel):
    status: str
    hostname: str
    timestamp: str
    timestamp_epoch: int
    version: VersionInfo
    metrics: SystemMetrics
    deployment: Dict
    tracker: TrackerStatus  # Using tracker instead of player for Mac devices
    health_scores: HealthScore
    device_info: DeviceInfo
    system: Optional[MacOSSystemInfo] = None
    display: Optional[DisplayInfo] = None
    _cache_info: Optional[Dict] = None

    class Config:
        # Allow extra fields to be compatible with oaDashboard
        extra = "allow"


class CameraInfo(BaseModel):
    id: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    is_built_in: bool = False
    is_connected: bool = True
    is_available: bool = True  # Added to match oaDashboard schema
    resolution: Optional[Dict[str, int]] = None  # Changed to match oaDashboard schema
    location: Optional[str] = None  # e.g., "Built-in", "USB", etc.

    class Config:
        extra = "allow"


class CameraListResponse(BaseModel):
    cameras: List[CameraInfo]
    count: int
    device_has_camera_support: bool = True  # Changed to match oaDashboard schema

    class Config:
        extra = "allow"


class ErrorResponse(BaseModel):
    status: str = "error"
    timestamp: str
    timestamp_epoch: int
    error: str
