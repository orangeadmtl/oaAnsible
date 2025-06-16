#!/usr/bin/env python3
"""
oaAnsible Client Library
For integration with oaDashboard and other services
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
import httpx

logger = logging.getLogger(__name__)

class OAAnsibleClientError(Exception):
    """Base exception for oaAnsible client errors"""
    pass

class OAAnsibleClient:
    """Async client for oaAnsible server API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_token: Optional[str] = None,
        timeout: float = 60.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """Initialize the HTTP client"""
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _ensure_client(self):
        """Ensure client is initialized"""
        if not self._client:
            raise OAAnsibleClientError("Client not connected. Use async context manager or call connect()")
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and handle errors"""
        self._ensure_client()
        
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)
            
            raise OAAnsibleClientError(f"HTTP {e.response.status_code}: {error_detail}")
        except httpx.RequestError as e:
            raise OAAnsibleClientError(f"Request failed: {str(e)}")
    
    # Health and Status
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        return await self._request("GET", "/api/health")
    
    async def get_environments(self) -> List[Dict[str, Any]]:
        """Get available deployment environments"""
        result = await self._request("GET", "/api/environments")
        return result["environments"]
    
    async def get_components(self) -> Dict[str, Any]:
        """Get available components"""
        result = await self._request("GET", "/api/components")
        return result["components"]
    
    # Deployment Management
    async def deploy_components(
        self,
        environment: str,
        components: List[str],
        target_hosts: Optional[List[str]] = None,
        execution_mode: str = "normal",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deploy components to environment"""
        
        payload = {
            "environment": environment,
            "components": components,
            "target_hosts": target_hosts or [],
            "execution_mode": execution_mode,
            "options": options or {}
        }
        
        return await self._request("POST", "/api/deploy/components", json=payload)
    
    async def dry_run_deployment(
        self,
        environment: str,
        components: List[str],
        target_hosts: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform dry-run deployment"""
        
        return await self.deploy_components(
            environment=environment,
            components=components,
            target_hosts=target_hosts,
            execution_mode="dry-run",
            options=options
        )
    
    # Job Management
    async def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List deployment jobs"""
        
        params = {"page": page, "page_size": page_size}
        if status_filter:
            params["status_filter"] = status_filter
        
        return await self._request("GET", "/api/jobs", params=params)
    
    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get specific job details"""
        return await self._request("GET", f"/api/jobs/{job_id}")
    
    async def get_job_logs(self, job_id: str) -> List[str]:
        """Get job execution logs"""
        result = await self._request("GET", f"/api/jobs/{job_id}/logs")
        return result["logs"]
    
    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running job"""
        return await self._request("DELETE", f"/api/jobs/{job_id}")
    
    async def wait_for_job(
        self, 
        job_id: str, 
        timeout: Optional[float] = None,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """Wait for job completion"""
        
        start_time = datetime.now()
        
        while True:
            job = await self.get_job(job_id)
            status = job["status"]
            
            if status in ["completed", "failed", "cancelled"]:
                return job
            
            if timeout:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    raise OAAnsibleClientError(f"Job {job_id} timeout after {timeout}s")
            
            await asyncio.sleep(poll_interval)
    
    async def stream_job_logs(
        self, 
        job_id: str, 
        poll_interval: float = 1.0
    ) -> AsyncIterator[str]:
        """Stream job logs in real-time"""
        
        last_log_count = 0
        
        while True:
            try:
                job = await self.get_job(job_id)
                status = job["status"]
                
                logs = await self.get_job_logs(job_id)
                
                # Yield new log entries
                for log_entry in logs[last_log_count:]:
                    yield log_entry
                
                last_log_count = len(logs)
                
                # Stop if job is finished
                if status in ["completed", "failed", "cancelled"]:
                    break
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error streaming logs for job {job_id}: {e}")
                break
    
    # Convenience Methods
    async def deploy_and_wait(
        self,
        environment: str,
        components: List[str],
        target_hosts: Optional[List[str]] = None,
        execution_mode: str = "normal",
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Deploy components and wait for completion"""
        
        # Start deployment
        deployment_result = await self.deploy_components(
            environment=environment,
            components=components,
            target_hosts=target_hosts,
            execution_mode=execution_mode,
            options=options
        )
        
        job_id = deployment_result["job_id"]
        
        # Wait for completion
        final_job = await self.wait_for_job(job_id, timeout)
        
        # Return combined result
        return {
            "deployment": deployment_result,
            "job": final_job,
            "success": final_job["status"] == "completed"
        }
    
    async def get_recent_deployments(
        self,
        environment: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent deployments"""
        
        jobs_result = await self.list_jobs(page_size=limit)
        jobs = jobs_result["jobs"]
        
        if environment:
            jobs = [
                job for job in jobs
                if job.get("details", {}).get("environment") == environment
            ]
        
        return jobs
    
    async def get_deployment_status(self, environment: str) -> Dict[str, Any]:
        """Get current deployment status for environment"""
        
        # Get recent jobs for this environment
        recent_jobs = await self.get_recent_deployments(environment, limit=5)
        
        # Get environment info
        environments = await self.get_environments()
        env_info = next((e for e in environments if e["name"] == environment), None)
        
        # Check for running deployments
        running_jobs = [j for j in recent_jobs if j["status"] == "running"]
        
        return {
            "environment": environment,
            "environment_info": env_info,
            "active_deployments": len(running_jobs),
            "recent_jobs": recent_jobs,
            "last_deployment": recent_jobs[0] if recent_jobs else None,
            "status": "busy" if running_jobs else "ready"
        }

# Factory function for easy usage
async def create_client(
    base_url: str = "http://localhost:8001",
    api_token: Optional[str] = None,
    timeout: float = 60.0
) -> OAAnsibleClient:
    """Create and connect an oaAnsible client"""
    client = OAAnsibleClient(base_url, api_token, timeout)
    await client.connect()
    return client

# Sync wrapper for simple operations
def create_sync_client(
    base_url: str = "http://localhost:8001",
    api_token: Optional[str] = None,
    timeout: float = 60.0
) -> "SyncOAAnsibleClient":
    """Create synchronous client wrapper"""
    return SyncOAAnsibleClient(base_url, api_token, timeout)

class SyncOAAnsibleClient:
    """Synchronous wrapper for oaAnsible client"""
    
    def __init__(self, base_url: str, api_token: Optional[str], timeout: float):
        self.base_url = base_url
        self.api_token = api_token
        self.timeout = timeout
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def health_check(self) -> Dict[str, Any]:
        """Sync health check"""
        async def _health():
            async with OAAnsibleClient(self.base_url, self.api_token, self.timeout) as client:
                return await client.health_check()
        
        return self._run_async(_health())
    
    def deploy_components(
        self,
        environment: str,
        components: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Sync component deployment"""
        async def _deploy():
            async with OAAnsibleClient(self.base_url, self.api_token, self.timeout) as client:
                return await client.deploy_components(environment, components, **kwargs)
        
        return self._run_async(_deploy())
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Sync get job"""
        async def _get_job():
            async with OAAnsibleClient(self.base_url, self.api_token, self.timeout) as client:
                return await client.get_job(job_id)
        
        return self._run_async(_get_job())