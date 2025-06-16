#!/usr/bin/env python3
"""
oaAnsible Server API for oaDashboard Integration
Provides REST endpoints for remote Ansible deployment management
"""

import asyncio
import json
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

from jobs.job_manager import JobManager, JobStatus
from auth.auth_manager import AuthManager
from utils.ansible_executor import AnsibleExecutor
from config.server_config import ServerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="oaAnsible Server API",
    description="Remote Ansible deployment management for oaDashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security
security = HTTPBearer()

# Global instances
config = ServerConfig()
job_manager = JobManager()
auth_manager = AuthManager()
ansible_executor = AnsibleExecutor()

# Pydantic Models
class ComponentRequest(BaseModel):
    """Request model for component deployment"""
    environment: str = Field(..., description="Target environment (staging, production, preprod)")
    components: List[str] = Field(..., description="List of components to deploy")
    target_hosts: List[str] = Field(default=[], description="Specific hosts to target (empty = all)")
    execution_mode: str = Field(default="normal", description="Execution mode (normal, dry-run, check, force)")
    options: Dict[str, Any] = Field(default={}, description="Additional execution options")

class JobResponse(BaseModel):
    """Response model for job operations"""
    job_id: str
    status: str
    message: str
    created_at: datetime
    updated_at: datetime
    details: Optional[Dict[str, Any]] = None

class JobListResponse(BaseModel):
    """Response model for job listing"""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int

class HealthResponse(BaseModel):
    """Response model for health checks"""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]

# Dependency injection
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate authentication token"""
    try:
        user = await auth_manager.validate_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# API Endpoints

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        components={
            "job_manager": "ready",
            "ansible_executor": "ready",
            "auth_manager": "ready"
        }
    )

@app.post("/api/deploy/components", response_model=JobResponse)
async def deploy_components(
    request: ComponentRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Deploy selected components to target environment"""
    try:
        # Validate request
        if not request.components:
            raise HTTPException(status_code=400, detail="No components specified")
        
        if request.environment not in ["staging", "production", "preprod"]:
            raise HTTPException(status_code=400, detail="Invalid environment")
        
        # Create deployment job
        job_id = str(uuid.uuid4())
        job_data = {
            "type": "component_deployment",
            "environment": request.environment,
            "components": request.components,
            "target_hosts": request.target_hosts,
            "execution_mode": request.execution_mode,
            "options": request.options,
            "user": user["username"],
            "user_id": user["id"]
        }
        
        # Queue the job
        job = await job_manager.create_job(job_id, job_data)
        
        # Execute in background
        background_tasks.add_task(
            execute_deployment_job,
            job_id,
            job_data
        )
        
        logger.info(f"Component deployment job {job_id} queued by user {user['username']}")
        
        return JobResponse(
            job_id=job_id,
            status=job.status.value,
            message="Deployment job queued successfully",
            created_at=job.created_at,
            updated_at=job.updated_at,
            details={
                "environment": request.environment,
                "components": request.components,
                "execution_mode": request.execution_mode
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating deployment job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create deployment job")

@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """List deployment jobs"""
    try:
        jobs, total = await job_manager.list_jobs(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            user_id=user["id"]
        )
        
        job_responses = [
            JobResponse(
                job_id=job.job_id,
                status=job.status.value,
                message=job.message or "",
                created_at=job.created_at,
                updated_at=job.updated_at,
                details=job.data
            )
            for job in jobs
        ]
        
        return JobListResponse(
            jobs=job_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, user: dict = Depends(get_current_user)):
    """Get specific job details"""
    try:
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check access permissions
        if job.data.get("user_id") != user["id"] and not user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JobResponse(
            job_id=job.job_id,
            status=job.status.value,
            message=job.message or "",
            created_at=job.created_at,
            updated_at=job.updated_at,
            details=job.data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job")

@app.get("/api/jobs/{job_id}/logs")
async def get_job_logs(job_id: str, user: dict = Depends(get_current_user)):
    """Get job execution logs"""
    try:
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check access permissions
        if job.data.get("user_id") != user["id"] and not user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logs = await job_manager.get_job_logs(job_id)
        return {"job_id": job_id, "logs": logs}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job logs")

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str, user: dict = Depends(get_current_user)):
    """Cancel a running job"""
    try:
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check access permissions
        if job.data.get("user_id") != user["id"] and not user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await job_manager.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled")
        
        return {"message": "Job cancelled successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel job")

@app.get("/api/environments")
async def list_environments(user: dict = Depends(get_current_user)):
    """List available deployment environments"""
    try:
        environments = await ansible_executor.get_available_environments()
        return {"environments": environments}
        
    except Exception as e:
        logger.error(f"Error listing environments: {e}")
        raise HTTPException(status_code=500, detail="Failed to list environments")

@app.get("/api/components")
async def list_components(user: dict = Depends(get_current_user)):
    """List available components for deployment"""
    try:
        components = await ansible_executor.get_available_components()
        return {"components": components}
        
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail="Failed to list components")

# Background task functions
async def execute_deployment_job(job_id: str, job_data: Dict[str, Any]):
    """Execute deployment job in background"""
    try:
        await job_manager.update_job_status(job_id, JobStatus.RUNNING, "Starting deployment...")
        
        # Execute the deployment
        result = await ansible_executor.execute_component_deployment(
            environment=job_data["environment"],
            components=job_data["components"],
            target_hosts=job_data.get("target_hosts", []),
            execution_mode=job_data.get("execution_mode", "normal"),
            options=job_data.get("options", {}),
            job_id=job_id
        )
        
        if result["success"]:
            await job_manager.update_job_status(
                job_id, 
                JobStatus.COMPLETED, 
                "Deployment completed successfully",
                result
            )
        else:
            await job_manager.update_job_status(
                job_id, 
                JobStatus.FAILED, 
                f"Deployment failed: {result.get('error', 'Unknown error')}",
                result
            )
            
    except Exception as e:
        logger.error(f"Error executing deployment job {job_id}: {e}")
        await job_manager.update_job_status(
            job_id, 
            JobStatus.FAILED, 
            f"Job execution error: {str(e)}"
        )

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Initialize server components"""
    logger.info("Starting oaAnsible Server API...")
    await job_manager.initialize()
    await auth_manager.initialize()
    await ansible_executor.initialize()
    logger.info("oaAnsible Server API started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup server components"""
    logger.info("Shutting down oaAnsible Server API...")
    await job_manager.cleanup()
    await auth_manager.cleanup()
    await ansible_executor.cleanup()
    logger.info("oaAnsible Server API shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "deployment_api:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug_mode,
        log_level="info"
    )