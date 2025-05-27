from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from macos_api.core.config import APP_VERSION, TAILSCALE_SUBNET
from macos_api.middleware import TailscaleSubnetMiddleware
from macos_api.routers import health, camera, actions, tracker

# Initialize FastAPI app
app = FastAPI(
    title="macOS Health Check API",
    version=APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Tailscale subnet restriction middleware
app.add_middleware(TailscaleSubnetMiddleware, tailscale_subnet_str=TAILSCALE_SUBNET)

# No screenshot directory needed

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(camera.router, tags=["camera"])
app.include_router(actions.router, tags=["actions"])
app.include_router(tracker.router, tags=["tracker"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "macOS Device API",
        "version": APP_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "health_summary": "/health/summary",
            "camera": {
                "list": "/cameras",
                "status": "/cameras/status",
                "stream": "/cameras/{camera_id}/stream"
            },
            "actions": {
                "reboot": "/actions/reboot",
                "restart_tracker": "/actions/restart-tracker"
            },
            "tracker": {
                "stats": "/tracker/stats",
                "status": "/tracker/status",
                "stream": "/tracker/stream",
                "mjpeg": "/tracker/mjpeg"
            }
        }
    }
