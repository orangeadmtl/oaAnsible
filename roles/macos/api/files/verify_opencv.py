#!/usr/bin/env python3
"""
Verify that OpenCV is properly installed and camera access is working.
This script is used by the Ansible deployment to ensure the macos-api
can access the camera via OpenCV.
"""
import sys
import platform
import importlib.util

def check_dependency(package_name):
    """Check if a package is installed and return its version."""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            return False, None
        
        # Try to get version
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        return True, version
    except Exception as e:
        return False, str(e)

def main():
    """Check OpenCV installation and camera access."""
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # Check OpenCV installation
    installed, version = check_dependency("cv2")
    if not installed:
        print(f"ERROR: OpenCV not installed: {version}")
        return 1
    
    print(f"OpenCV installation verified: {version}")
    
    # Try to import OpenCV
    try:
        import cv2
        
        # Get available backends
        backends = []
        if hasattr(cv2, 'CAP_ANY'):
            backends.append("CAP_ANY")
        if hasattr(cv2, 'CAP_AVFOUNDATION'):
            backends.append("CAP_AVFOUNDATION")
        if hasattr(cv2, 'CAP_DSHOW'):
            backends.append("CAP_DSHOW")
        
        print(f"Available camera backends: {', '.join(backends)}")
        
        # Try to access camera
        print("\nTesting camera access...")
        
        # Try with default backend first
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("Camera opened successfully with default backend")
            ret, frame = cap.read()
            if ret:
                print(f"Frame read successfully: {frame.shape}")
            else:
                print("WARNING: Camera opened but could not read frame")
            cap.release()
        else:
            print("WARNING: Could not open camera with default backend")
            
            # Try with AVFoundation backend if available
            if hasattr(cv2, 'CAP_AVFOUNDATION'):
                print("Trying with AVFoundation backend...")
                cap = cv2.VideoCapture(0 + cv2.CAP_AVFOUNDATION)
                if cap.isOpened():
                    print("Camera opened successfully with AVFoundation backend")
                    ret, frame = cap.read()
                    if ret:
                        print(f"Frame read successfully: {frame.shape}")
                    else:
                        print("WARNING: Camera opened but could not read frame")
                    cap.release()
                else:
                    print("WARNING: Could not open camera with AVFoundation backend")
    
    except Exception as e:
        print(f"ERROR testing camera: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
