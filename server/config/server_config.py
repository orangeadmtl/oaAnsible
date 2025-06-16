#!/usr/bin/env python3
"""
Server Configuration for oaAnsible Server
Handles configuration management with environment variables and defaults
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ServerConfig:
    """Configuration management for oaAnsible server"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and defaults"""
        
        # API Configuration
        self.api_host = os.getenv("OAANSIBLE_API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("OAANSIBLE_API_PORT", "8001"))
        self.debug_mode = os.getenv("OAANSIBLE_DEBUG", "false").lower() == "true"
        
        # Security Configuration
        self.secret_key = os.getenv("OAANSIBLE_SECRET_KEY", "oaansible-change-this-secret-key")
        self.token_expiry_hours = int(os.getenv("OAANSIBLE_TOKEN_EXPIRY_HOURS", "24"))
        
        # oaDashboard Integration
        self.dashboard_api_url = os.getenv("OADASHBOARD_API_URL", "http://localhost:8000")
        self.dashboard_api_key = os.getenv("OADASHBOARD_API_KEY")
        
        # Database Configuration
        self.database_url = os.getenv("OAANSIBLE_DATABASE_URL", "/tmp/oaansible.db")
        
        # Ansible Configuration
        ansible_root = os.getenv("OAANSIBLE_ROOT")
        if ansible_root:
            self.ansible_root = Path(ansible_root)
        else:
            # Auto-detect ansible root
            current_dir = Path(__file__).parent
            while current_dir.parent != current_dir:
                if (current_dir / "playbooks").exists() and (current_dir / "inventory").exists():
                    self.ansible_root = current_dir
                    break
                current_dir = current_dir.parent
            else:
                self.ansible_root = Path.cwd()
        
        # Job Management
        self.max_concurrent_jobs = int(os.getenv("OAANSIBLE_MAX_CONCURRENT_JOBS", "5"))
        self.job_timeout_minutes = int(os.getenv("OAANSIBLE_JOB_TIMEOUT_MINUTES", "60"))
        self.job_cleanup_days = int(os.getenv("OAANSIBLE_JOB_CLEANUP_DAYS", "7"))
        
        # Logging Configuration
        self.log_level = os.getenv("OAANSIBLE_LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("OAANSIBLE_LOG_FILE")
        
        # CORS Configuration
        self.cors_origins = os.getenv("OAANSIBLE_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
        
        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("OAANSIBLE_RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window_minutes = int(os.getenv("OAANSIBLE_RATE_LIMIT_WINDOW", "15"))
        
        # WebSocket Configuration (for real-time updates)
        self.websocket_enabled = os.getenv("OAANSIBLE_WEBSOCKET_ENABLED", "true").lower() == "true"
        self.websocket_port = int(os.getenv("OAANSIBLE_WEBSOCKET_PORT", "8002"))
        
        # Monitoring & Health Checks
        self.health_check_interval = int(os.getenv("OAANSIBLE_HEALTH_CHECK_INTERVAL", "30"))
        self.metrics_enabled = os.getenv("OAANSIBLE_METRICS_ENABLED", "true").lower() == "true"
        
        # Security Headers
        self.security_headers_enabled = os.getenv("OAANSIBLE_SECURITY_HEADERS", "true").lower() == "true"
        
        # Development/Testing
        self.testing_mode = os.getenv("OAANSIBLE_TESTING", "false").lower() == "true"
        self.mock_ansible = os.getenv("OAANSIBLE_MOCK_ANSIBLE", "false").lower() == "true"
        
        # Validate critical configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration and warn about issues"""
        warnings = []
        errors = []
        
        # Check secret key
        if self.secret_key == "oaansible-change-this-secret-key":
            warnings.append("Using default secret key - change OAANSIBLE_SECRET_KEY in production")
        
        # Check ansible root
        if not self.ansible_root.exists():
            errors.append(f"Ansible root directory does not exist: {self.ansible_root}")
        elif not (self.ansible_root / "playbooks").exists():
            errors.append(f"Playbooks directory not found in: {self.ansible_root}")
        elif not (self.ansible_root / "inventory").exists():
            errors.append(f"Inventory directory not found in: {self.ansible_root}")
        
        # Check dashboard integration
        if not self.dashboard_api_key and not self.testing_mode:
            warnings.append("No dashboard API key configured - dashboard integration disabled")
        
        # Log warnings and errors
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
        
        for error in errors:
            logger.error(f"Configuration error: {error}")
        
        if errors:
            raise ValueError(f"Configuration errors found: {errors}")
    
    def get_ansible_config(self) -> Dict[str, Any]:
        """Get Ansible-specific configuration"""
        return {
            "root": str(self.ansible_root),
            "playbooks_dir": str(self.ansible_root / "playbooks"),
            "inventory_dir": str(self.ansible_root / "inventory"),
            "scripts_dir": str(self.ansible_root / "scripts"),
            "universal_playbook": str(self.ansible_root / "playbooks" / "universal.yml")
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration"""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "debug": self.debug_mode,
            "cors_origins": self.cors_origins,
            "security_headers": self.security_headers_enabled
        }
    
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        return {
            "secret_key": self.secret_key,
            "token_expiry_hours": self.token_expiry_hours,
            "dashboard_api_url": self.dashboard_api_url,
            "dashboard_api_key": self.dashboard_api_key
        }
    
    def get_job_config(self) -> Dict[str, Any]:
        """Get job management configuration"""
        return {
            "max_concurrent": self.max_concurrent_jobs,
            "timeout_minutes": self.job_timeout_minutes,
            "cleanup_days": self.job_cleanup_days,
            "database_url": self.database_url
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.log_level,
            "file": self.log_file,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return {
            "api": self.get_api_config(),
            "auth": self.get_auth_config(),
            "ansible": self.get_ansible_config(),
            "jobs": self.get_job_config(),
            "logging": self.get_logging_config(),
            "websocket": {
                "enabled": self.websocket_enabled,
                "port": self.websocket_port
            },
            "monitoring": {
                "health_check_interval": self.health_check_interval,
                "metrics_enabled": self.metrics_enabled
            },
            "rate_limiting": {
                "requests": self.rate_limit_requests,
                "window_minutes": self.rate_limit_window_minutes
            },
            "development": {
                "testing_mode": self.testing_mode,
                "mock_ansible": self.mock_ansible
            }
        }
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration values"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated configuration: {key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        import json
        
        config_path = file_path or self.config_file or "oaansible_config.json"
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.get_all_config(), f, indent=2, default=str)
            
            logger.info(f"Configuration saved to: {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def load_config_file(self, file_path: str):
        """Load configuration from JSON file"""
        import json
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Flatten nested config for attribute setting
            flat_config = {}
            for section, values in config_data.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        flat_config[key] = value
                else:
                    flat_config[section] = values
            
            self.update_config(flat_config)
            logger.info(f"Configuration loaded from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ServerConfig(api={self.api_host}:{self.api_port}, ansible_root={self.ansible_root})"
    
    def __repr__(self) -> str:
        return self.__str__()