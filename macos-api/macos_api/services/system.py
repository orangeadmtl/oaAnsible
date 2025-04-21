import psutil
import platform
import re
import os
import subprocess
from typing import Dict
from datetime import datetime, timezone
from ..core.config import LAUNCHCTL_CMD, PS_CMD, TRACKER_ROOT
from ..services.utils import run_command


def get_system_metrics() -> Dict:
    """Get comprehensive system metrics including CPU, memory, disk, and network usage."""
    try:
        # Get base metrics (keeping existing structure)
        cpu_metrics = {
            "percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count(),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "per_core": psutil.cpu_percent(interval=1, percpu=True),
        }

        memory = psutil.virtual_memory()
        memory_metrics = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "cached": getattr(memory, "cached", 0),
            "buffers": getattr(memory, "buffers", 0),
        }

        disk = psutil.disk_usage("/")
        disk_metrics = {"total": disk.total, "free": disk.free, "percent": disk.percent, "used": disk.used}

        # Add disk I/O metrics
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_metrics["io"] = {
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count,
                }
        except Exception:
            pass

        # Add network metrics
        try:
            network_metrics = {"interfaces": {}, "connections": len(psutil.net_connections())}

            # Get network interface stats
            net_if_stats = psutil.net_if_stats()
            net_io_counters = psutil.net_io_counters(pernic=True)

            for iface, stats in net_if_stats.items():
                interface_metrics = {"up": stats.isup, "speed": stats.speed, "mtu": stats.mtu}

                # Add IO metrics if available
                if iface in net_io_counters:
                    io_stats = net_io_counters[iface]
                    interface_metrics.update(
                        {
                            "bytes_sent": io_stats.bytes_sent,
                            "bytes_recv": io_stats.bytes_recv,
                            "packets_sent": io_stats.packets_sent,
                            "packets_recv": io_stats.packets_recv,
                            "errors_in": io_stats.errin,
                            "errors_out": io_stats.errout,
                        }
                    )

                network_metrics["interfaces"][iface] = interface_metrics
        except Exception:
            network_metrics = {}

        return {"cpu": cpu_metrics, "memory": memory_metrics, "disk": disk_metrics, "network": network_metrics, "boot_time": psutil.boot_time()}
    except Exception as e:
        return {
            "cpu": {"percent": psutil.cpu_percent(interval=1), "cores": psutil.cpu_count()},
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {"total": psutil.disk_usage("/").total, "free": psutil.disk_usage("/").free, "percent": psutil.disk_usage("/").percent},
            "error": str(e),
        }


def get_service_info(service_name: str) -> Dict:
    """Get detailed information about a launchd service."""
    info = {"status": "unknown", "pid": "unknown", "activestate": "unknown", "substate": "unknown"}

    try:
        # Check if service is running using launchctl
        cmd = [LAUNCHCTL_CMD, "list"]
        output = run_command(cmd)
        
        # Parse the output to find the service
        for line in output.split('\n'):
            if service_name in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[0]
                    if pid != "-":
                        info["pid"] = pid
                        info["status"] = "active"
                        info["activestate"] = "active"
                        info["substate"] = "running"
                    else:
                        info["status"] = "inactive"
                        info["activestate"] = "inactive"
                        info["substate"] = "dead"
                    break
        
        # If service wasn't found in the list, it's not loaded
        if info["status"] == "unknown":
            info["status"] = "inactive"
            info["activestate"] = "inactive"
            info["substate"] = "dead"
            
    except Exception:
        pass

    return info


def get_device_info() -> Dict[str, str]:
    """Get device type and series based on hostname and check if headless."""
    hostname = platform.node().lower()

    # Extract series and number from hostname (e.g., 'mac0001', 'labatt0002')
    series_match = re.match(r"^([a-z]+)(\d+)$", hostname)
    series = series_match.group(1).upper() if series_match else "UNKNOWN"
    
    # Check if the system has a display
    is_headless = False
    try:
        # Try to get display info using system_profiler
        display_cmd = ["system_profiler", "SPDisplaysDataType"]
        display_output = run_command(display_cmd)
        
        # If no displays are found or output is empty, consider it headless
        if not display_output or "No Display Found" in display_output:
            is_headless = True
    except Exception:
        # If command fails, assume it might be headless
        is_headless = True
    
    return {
        "type": "Mac", 
        "series": series, 
        "hostname": hostname,
        "is_headless": is_headless
    }


def get_version_info() -> Dict:
    """Get system and tracker version information."""
    try:
        # Get system info
        system_info = {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

        # Get macOS version using sw_vers
        try:
            product_version = run_command(["sw_vers", "-productVersion"])
            build_version = run_command(["sw_vers", "-buildVersion"])
            if product_version:
                system_info["macos_version"] = product_version
            if build_version:
                system_info["build_version"] = build_version
        except Exception:
            pass

        # Extract series from hostname (e.g., mac0001 -> mac)
        hostname = system_info["hostname"].lower()
        series_match = re.match(r"^([a-zA-Z]+)", hostname)
        if series_match:
            system_info["series"] = series_match.group(1)

        # Get tracker version if available
        tracker_version_file = TRACKER_ROOT / "version.txt"
        if tracker_version_file.exists():
            with open(tracker_version_file) as f:
                system_info["tracker_version"] = f.read().strip()

        # Get Tailscale version
        try:
            # Check both possible locations for Tailscale
            tailscale_paths = [
                "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
                "/usr/local/bin/tailscale"
            ]
            
            for path in tailscale_paths:
                if os.path.exists(path):
                    tailscale_version_output = run_command([path, "version"])
                    if tailscale_version_output:
                        # Extract just the version number from the first line
                        version_number = tailscale_version_output.split("\n")[0].strip()
                        system_info["tailscale_version"] = version_number
                        break
            
            if "tailscale_version" not in system_info:
                system_info["tailscale_version"] = None
        except Exception:
            system_info["tailscale_version"] = None

        return system_info
    except Exception as e:
        return {"error": str(e)}
