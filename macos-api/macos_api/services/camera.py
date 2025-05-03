"""
macOS Camera Services Module

This module provides functions to detect and stream from macOS cameras.
It uses system_profiler to detect cameras and opencv for streaming.
"""

import subprocess
import re
import json
import uuid
from typing import Dict, List, Optional
import logging
from datetime import datetime
import shlex

from ..models.schemas import CameraInfo

# Configure logger
logger = logging.getLogger(__name__)


def get_camera_list() -> List[CameraInfo]:
    """
    Get a list of all available cameras on the macOS system.
    
    Uses system_profiler to detect cameras and their properties.
    
    Returns:
        List[CameraInfo]: List of camera information objects
    """
    try:
        # Run system_profiler to get camera information
        cmd = ["system_profiler", "SPCameraDataType", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the JSON output
        camera_data = json.loads(result.stdout)
        
        # Extract camera information
        cameras = []
        
        # Check if Camera section exists
        if "SPCameraDataType" in camera_data and camera_data["SPCameraDataType"]:
            for camera_entry in camera_data["SPCameraDataType"]:
                # Each camera might have different property names
                # Extract common properties
                camera_name = camera_entry.get("_name", "Unknown Camera")
                
                # Generate a unique ID for the camera
                camera_id = str(uuid.uuid4())[:8]
                
                # Check if it's a built-in camera
                is_built_in = "FaceTime" in camera_name or "Built-in" in camera_name
                
                # Create camera info object
                camera_info = CameraInfo(
                    id=camera_id,
                    name=camera_name,
                    model=camera_entry.get("model_id", None),
                    manufacturer=camera_entry.get("manufacturer", None),
                    is_built_in=is_built_in,
                    is_connected=True,  # Assume connected if detected
                    location="Built-in" if is_built_in else "External"
                )
                
                cameras.append(camera_info)
        
        return cameras
    
    except subprocess.SubprocessError as e:
        logger.error(f"Error running system_profiler: {str(e)}")
        return []
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing system_profiler output: {str(e)}")
        return []
    
    except Exception as e:
        logger.error(f"Unexpected error detecting cameras: {str(e)}")
        return []


def get_camera_by_id(camera_id: str) -> Optional[CameraInfo]:
    """
    Get a specific camera by its ID.
    
    Args:
        camera_id: The ID of the camera to retrieve
        
    Returns:
        CameraInfo: Camera information if found, None otherwise
    """
    cameras = get_camera_list()
    
    for camera in cameras:
        if camera.id == camera_id:
            return camera
    
    return None


def check_camera_availability() -> Dict:
    """
    Check if any cameras are available on the system.
    
    Returns:
        Dict: Status information about camera availability
    """
    cameras = get_camera_list()
    
    return {
        "has_camera": len(cameras) > 0,
        "camera_count": len(cameras),
        "cameras": cameras,
        "timestamp": datetime.now().isoformat()
    }
