#!/usr/bin/env python3
"""
oaAnsible Server Startup Script
Main entry point for the oaAnsible server API
"""

import asyncio
import logging
import os
import sys
import signal
from pathlib import Path

# Add server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

import uvicorn
from api.deployment_api import app
from config.server_config import ServerConfig

# Configure logging
def setup_logging(config: ServerConfig):
    """Setup logging configuration"""
    log_config = config.get_logging_config()
    
    logging.basicConfig(
        level=getattr(logging, log_config["level"]),
        format=log_config["format"],
        filename=log_config["file"] if log_config["file"] else None
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    return logger

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

async def run_server():
    """Run the server with proper startup and shutdown"""
    # Load configuration
    config = ServerConfig()
    logger = setup_logging(config)
    
    try:
        # Display startup banner
        print("\n" + "="*60)
        print("🚀 OrangeAd Ansible Server Starting")
        print("="*60)
        print(f"API Host: {config.api_host}:{config.api_port}")
        print(f"Ansible Root: {config.ansible_root}")
        print(f"Debug Mode: {config.debug_mode}")
        print(f"Dashboard Integration: {'Enabled' if config.dashboard_api_key else 'Disabled'}")
        print("="*60 + "\n")
        
        # Configure the FastAPI app
        api_config = config.get_api_config()
        
        # Add CORS middleware if needed
        if api_config["cors_origins"]:
            from fastapi.middleware.cors import CORSMiddleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=api_config["cors_origins"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Add security middleware if enabled
        if api_config["security_headers"]:
            from fastapi.middleware.security import SecurityHeadersMiddleware
            app.add_middleware(SecurityHeadersMiddleware)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Start the server
        uvicorn_config = uvicorn.Config(
            app,
            host=api_config["host"],
            port=api_config["port"],
            reload=api_config["debug"],
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

def main():
    """Main entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("ERROR: Python 3.8 or higher is required")
            sys.exit(1)
        
        # Check if we're in the right directory
        if not Path("../playbooks/universal.yml").exists():
            print("ERROR: Must be run from oaAnsible/server directory")
            print("Current directory:", os.getcwd())
            sys.exit(1)
        
        # Run the server
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()