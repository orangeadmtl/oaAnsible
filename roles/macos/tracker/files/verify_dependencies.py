#!/usr/bin/env python3
"""
Verify that critical dependencies for the OrangeAd Tracker are properly installed.
This script checks that key packages like OpenCV, PyTorch, and Ultralytics are available
and reports their versions.
"""
import sys
import importlib.util
import platform

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
    """Check critical dependencies and report their status."""
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("Checking critical dependencies...")
    
    # List of critical dependencies to check
    dependencies = [
        "cv2",  # OpenCV
        "torch",  # PyTorch
        "ultralytics",  # YOLO
        "fastapi",  # API framework
        "numpy",  # Numerical computing
        "duckdb",  # Database
        "pyarrow"  # Data processing
    ]
    
    success = True
    
    for dep in dependencies:
        installed, version = check_dependency(dep)
        status = "✓" if installed else "✗"
        version_str = f"v{version}" if version and version != "unknown" else ""
        
        if not installed:
            success = False
            print(f"[{status}] {dep:<15} {version_str} - MISSING")
        else:
            print(f"[{status}] {dep:<15} {version_str}")
    
    # Special check for OpenCV camera access
    if check_dependency("cv2")[0]:
        try:
            import cv2
            print("\nTesting OpenCV camera access...")
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                print("Camera opened successfully")
                ret, frame = cap.read()
                if ret:
                    print(f"Frame read successfully: {frame.shape}")
                else:
                    print("WARNING: Camera opened but could not read frame")
                cap.release()
            else:
                print("WARNING: Could not open camera")
        except Exception as e:
            print(f"ERROR testing camera: {str(e)}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
