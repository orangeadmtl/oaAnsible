#!/usr/bin/env python3
"""
Job Management System for oaAnsible Server
Handles job queuing, status tracking, and persistence
"""

import asyncio
import json
import sqlite3
import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    """Job data structure"""
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    logs: List[str] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []

class JobManager:
    """Manages deployment jobs with persistence and tracking"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "/tmp/oaansible_jobs.db"
        self.db_path = Path(self.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._jobs_cache: Dict[str, Job] = {}
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the job manager and database"""
        try:
            await self._create_database()
            await self._load_jobs_cache()
            logger.info(f"Job manager initialized with database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize job manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        async with self._lock:
            self._jobs_cache.clear()
        logger.info("Job manager cleanup complete")
    
    async def _create_database(self):
        """Create job database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    data TEXT NOT NULL,
                    message TEXT,
                    result TEXT,
                    logs TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)
            """)
            conn.commit()
    
    async def _load_jobs_cache(self):
        """Load recent jobs into cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM jobs 
                    WHERE created_at > datetime('now', '-24 hours')
                    ORDER BY created_at DESC
                    LIMIT 1000
                """)
                
                async with self._lock:
                    for row in cursor.fetchall():
                        job = self._row_to_job(row)
                        self._jobs_cache[job.job_id] = job
                        
            logger.info(f"Loaded {len(self._jobs_cache)} jobs into cache")
        except Exception as e:
            logger.error(f"Error loading jobs cache: {e}")
    
    def _row_to_job(self, row: sqlite3.Row) -> Job:
        """Convert database row to Job object"""
        return Job(
            job_id=row["job_id"],
            status=JobStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            data=json.loads(row["data"]),
            message=row["message"],
            result=json.loads(row["result"]) if row["result"] else None,
            logs=json.loads(row["logs"]) if row["logs"] else []
        )
    
    def _job_to_row(self, job: Job) -> Dict[str, Any]:
        """Convert Job object to database row"""
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "data": json.dumps(job.data),
            "message": job.message,
            "result": json.dumps(job.result) if job.result else None,
            "logs": json.dumps(job.logs)
        }
    
    async def create_job(self, job_id: str, job_data: Dict[str, Any]) -> Job:
        """Create a new job"""
        now = datetime.now(timezone.utc)
        job = Job(
            job_id=job_id,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
            data=job_data,
            message="Job created and queued"
        )
        
        # Save to database
        row_data = self._job_to_row(job)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO jobs (job_id, status, created_at, updated_at, data, message, result, logs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row_data["job_id"], row_data["status"], row_data["created_at"],
                row_data["updated_at"], row_data["data"], row_data["message"],
                row_data["result"], row_data["logs"]
            ))
            conn.commit()
        
        # Add to cache
        async with self._lock:
            self._jobs_cache[job_id] = job
        
        logger.info(f"Created job {job_id}")
        return job
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        # Check cache first
        async with self._lock:
            if job_id in self._jobs_cache:
                return self._jobs_cache[job_id]
        
        # Check database
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            
            if row:
                job = self._row_to_job(row)
                async with self._lock:
                    self._jobs_cache[job_id] = job
                return job
        
        return None
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: JobStatus, 
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ):
        """Update job status and message"""
        job = await self.get_job(job_id)
        if not job:
            logger.error(f"Cannot update non-existent job {job_id}")
            return
        
        job.status = status
        job.updated_at = datetime.now(timezone.utc)
        if message:
            job.message = message
        if result:
            job.result = result
        
        # Update database
        row_data = self._job_to_row(job)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = ?, updated_at = ?, message = ?, result = ?
                WHERE job_id = ?
            """, (
                row_data["status"], row_data["updated_at"], 
                row_data["message"], row_data["result"], job_id
            ))
            conn.commit()
        
        # Update cache
        async with self._lock:
            self._jobs_cache[job_id] = job
        
        logger.info(f"Updated job {job_id} status to {status.value}")
    
    async def add_job_log(self, job_id: str, log_entry: str):
        """Add log entry to job"""
        job = await self.get_job(job_id)
        if not job:
            logger.error(f"Cannot add log to non-existent job {job_id}")
            return
        
        timestamp = datetime.now(timezone.utc).isoformat()
        log_with_timestamp = f"[{timestamp}] {log_entry}"
        job.logs.append(log_with_timestamp)
        job.updated_at = datetime.now(timezone.utc)
        
        # Update database
        row_data = self._job_to_row(job)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE jobs 
                SET logs = ?, updated_at = ?
                WHERE job_id = ?
            """, (row_data["logs"], row_data["updated_at"], job_id))
            conn.commit()
        
        # Update cache
        async with self._lock:
            self._jobs_cache[job_id] = job
    
    async def get_job_logs(self, job_id: str) -> List[str]:
        """Get job logs"""
        job = await self.get_job(job_id)
        return job.logs if job else []
    
    async def list_jobs(
        self, 
        page: int = 1, 
        page_size: int = 20,
        status_filter: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[Job], int]:
        """List jobs with pagination and filtering"""
        offset = (page - 1) * page_size
        
        # Build query
        where_conditions = []
        params = []
        
        if status_filter:
            where_conditions.append("status = ?")
            params.append(status_filter)
        
        if user_id:
            where_conditions.append("json_extract(data, '$.user_id') = ?")
            params.append(user_id)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM jobs {where_clause}", params)
            total = cursor.fetchone()[0]
            
            # Get jobs
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"""
                SELECT * FROM jobs {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [page_size, offset])
            
            jobs = [self._row_to_job(row) for row in cursor.fetchall()]
        
        return jobs, total
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if possible"""
        job = await self.get_job(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False  # Cannot cancel finished jobs
        
        await self.update_job_status(
            job_id, 
            JobStatus.CANCELLED, 
            "Job cancelled by user"
        )
        
        return True
    
    async def cleanup_old_jobs(self, days_old: int = 7):
        """Clean up old completed jobs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM jobs 
                    WHERE status IN ('completed', 'failed', 'cancelled')
                    AND created_at < datetime('now', '-{} days')
                """.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
            # Clear relevant entries from cache
            async with self._lock:
                cutoff_date = datetime.now(timezone.utc).replace(day=datetime.now().day - days_old)
                to_remove = [
                    job_id for job_id, job in self._jobs_cache.items()
                    if job.created_at < cutoff_date and job.status in [
                        JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED
                    ]
                ]
                for job_id in to_remove:
                    del self._jobs_cache[job_id]
            
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
            return 0
    
    async def get_job_statistics(self) -> Dict[str, Any]:
        """Get job execution statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        AVG(CASE 
                            WHEN status IN ('completed', 'failed') 
                            THEN (julianday(updated_at) - julianday(created_at)) * 24 * 60
                            ELSE NULL 
                        END) as avg_duration_minutes
                    FROM jobs 
                    WHERE created_at > datetime('now', '-24 hours')
                    GROUP BY status
                """)
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = {
                        "count": row[1],
                        "avg_duration_minutes": round(row[2], 2) if row[2] else None
                    }
                
                # Get total counts
                cursor = conn.execute("SELECT COUNT(*) FROM jobs")
                total_jobs = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM jobs 
                    WHERE created_at > datetime('now', '-24 hours')
                """)
                jobs_24h = cursor.fetchone()[0]
                
                return {
                    "status_breakdown": stats,
                    "total_jobs": total_jobs,
                    "jobs_last_24h": jobs_24h
                }
                
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}")
            return {}