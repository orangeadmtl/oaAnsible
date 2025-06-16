#!/usr/bin/env python3
"""
Authentication Manager for oaAnsible Server
Handles token validation and user management integration with oaDashboard
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
import jwt
import httpx

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages authentication and authorization for the server API"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.secret_key = self.config.get("secret_key", "oaansible-default-secret-key")
        self.token_expiry_hours = self.config.get("token_expiry_hours", 24)
        self.dashboard_api_url = self.config.get("dashboard_api_url", "http://localhost:8000")
        self.dashboard_api_key = self.config.get("dashboard_api_key")
        
        # In-memory token cache (in production, use Redis)
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the authentication manager"""
        try:
            # Test connection to dashboard API if configured
            if self.dashboard_api_url and self.dashboard_api_key:
                await self._test_dashboard_connection()
            
            logger.info("Authentication manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize auth manager: {e}")
            # Continue with local-only auth
    
    async def cleanup(self):
        """Cleanup resources"""
        async with self._cache_lock:
            self._token_cache.clear()
        logger.info("Authentication manager cleanup complete")
    
    async def _test_dashboard_connection(self):
        """Test connection to oaDashboard API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.dashboard_api_url}/api/health",
                    headers={"Authorization": f"Bearer {self.dashboard_api_key}"}
                )
                response.raise_for_status()
                logger.info("Successfully connected to oaDashboard API")
        except Exception as e:
            logger.warning(f"Could not connect to oaDashboard API: {e}")
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate authentication token"""
        try:
            # Check cache first
            async with self._cache_lock:
                if token in self._token_cache:
                    cached_user = self._token_cache[token]
                    if cached_user["expires_at"] > datetime.now(timezone.utc):
                        return cached_user["user"]
                    else:
                        # Remove expired token
                        del self._token_cache[token]
            
            # Try dashboard API validation first
            user = await self._validate_with_dashboard(token)
            if user:
                await self._cache_user(token, user)
                return user
            
            # Fall back to local JWT validation
            user = await self._validate_jwt_token(token)
            if user:
                await self._cache_user(token, user)
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    async def _validate_with_dashboard(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token with oaDashboard API"""
        if not self.dashboard_api_url:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.dashboard_api_url}/api/auth/validate",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "id": user_data.get("id"),
                        "username": user_data.get("username"),
                        "email": user_data.get("email"),
                        "is_admin": user_data.get("is_admin", False),
                        "permissions": user_data.get("permissions", []),
                        "source": "dashboard"
                    }
        except Exception as e:
            logger.debug(f"Dashboard token validation failed: {e}")
        
        return None
    
    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate local JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=["HS256"]
            )
            
            # Check expiration
            if payload.get("exp", 0) < time.time():
                return None
            
            return {
                "id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "is_admin": payload.get("is_admin", False),
                "permissions": payload.get("permissions", []),
                "source": "local"
            }
            
        except jwt.InvalidTokenError as e:
            logger.debug(f"JWT validation failed: {e}")
            return None
    
    async def _cache_user(self, token: str, user: Dict[str, Any]):
        """Cache validated user data"""
        async with self._cache_lock:
            self._token_cache[token] = {
                "user": user,
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30)
            }
    
    async def create_local_token(
        self, 
        user_id: str, 
        username: str,
        email: Optional[str] = None,
        is_admin: bool = False,
        permissions: Optional[list] = None
    ) -> str:
        """Create a local JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "is_admin": is_admin,
            "permissions": permissions or [],
            "iat": time.time(),
            "exp": time.time() + (self.token_expiry_hours * 3600)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logger.info(f"Created local token for user {username}")
        return token
    
    async def revoke_token(self, token: str):
        """Revoke a token (remove from cache)"""
        async with self._cache_lock:
            if token in self._token_cache:
                del self._token_cache[token]
                logger.info("Token revoked from cache")
    
    async def cleanup_expired_tokens(self):
        """Clean up expired tokens from cache"""
        now = datetime.now(timezone.utc)
        async with self._cache_lock:
            expired_tokens = [
                token for token, data in self._token_cache.items()
                if data["expires_at"] <= now
            ]
            for token in expired_tokens:
                del self._token_cache[token]
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
    
    def check_permission(self, user: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission"""
        # Admins have all permissions
        if user.get("is_admin", False):
            return True
        
        # Check specific permission
        permissions = user.get("permissions", [])
        return required_permission in permissions
    
    def require_admin(self, user: Dict[str, Any]) -> bool:
        """Check if user is admin"""
        return user.get("is_admin", False)
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from token"""
        return await self.validate_token(token)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt (for local user management)"""
        if salt is None:
            salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        )
        
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        test_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(test_hash, hashed)
    
    async def create_api_key(self, user_id: str, name: str, permissions: Optional[list] = None) -> str:
        """Create an API key for programmatic access"""
        api_key_data = {
            "user_id": user_id,
            "name": name,
            "permissions": permissions or [],
            "created_at": time.time(),
            "type": "api_key"
        }
        
        api_key = jwt.encode(api_key_data, self.secret_key, algorithm="HS256")
        logger.info(f"Created API key '{name}' for user {user_id}")
        return api_key
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        try:
            payload = jwt.decode(api_key, self.secret_key, algorithms=["HS256"])
            
            if payload.get("type") != "api_key":
                return None
            
            return {
                "id": payload.get("user_id"),
                "username": f"api_key_{payload.get('name')}",
                "email": None,
                "is_admin": False,
                "permissions": payload.get("permissions", []),
                "source": "api_key",
                "api_key_name": payload.get("name")
            }
            
        except jwt.InvalidTokenError as e:
            logger.debug(f"API key validation failed: {e}")
            return None