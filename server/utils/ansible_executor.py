#!/usr/bin/env python3
"""
Ansible Executor for oaAnsible Server
Executes Ansible playbooks and integrates with the component framework
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class AnsibleExecutor:
    """Executes Ansible deployments using the advanced component framework"""
    
    def __init__(self, ansible_root: Optional[str] = None):
        self.ansible_root = Path(ansible_root or os.getcwd())
        self.playbook_path = self.ansible_root / "playbooks" / "universal.yml"
        self.inventory_dir = self.ansible_root / "inventory"
        self.scripts_dir = self.ansible_root / "scripts"
        
        # Component definitions (from our framework)
        self.available_components = {
            "macos-api": {
                "platform": "macos",
                "description": "macOS API service",
                "requires": ["python", "base-system"]
            },
            "macos-tracker": {
                "platform": "macos", 
                "description": "oaTracker AI tracking service",
                "requires": ["python", "base-system", "macos-api"]
            },
            "alpr": {
                "platform": "macos",
                "description": "ALPR license plate recognition",
                "requires": ["python", "base-system"]
            },
            "base-system": {
                "platform": "universal",
                "description": "Foundation system configuration",
                "requires": []
            },
            "python": {
                "platform": "universal",
                "description": "Python runtime environment",
                "requires": ["base-system"]
            },
            "node": {
                "platform": "universal",
                "description": "Node.js runtime environment", 
                "requires": ["base-system"]
            },
            "network-stack": {
                "platform": "universal",
                "description": "Network configuration including Tailscale",
                "requires": ["base-system"]
            },
            "ubuntu-docker": {
                "platform": "ubuntu",
                "description": "Docker environment for Ubuntu",
                "requires": ["base-system"]
            },
            "opi-player": {
                "platform": "orangepi",
                "description": "Media player service for OrangePi",
                "requires": ["base-system", "python"]
            }
        }
        
        self.environments = ["staging", "production", "preprod"]
    
    async def initialize(self):
        """Initialize the Ansible executor"""
        try:
            # Verify Ansible installation
            result = await self._run_command(["ansible", "--version"])
            if result["returncode"] != 0:
                raise Exception("Ansible not found or not working")
            
            # Verify playbook exists
            if not self.playbook_path.exists():
                raise Exception(f"Universal playbook not found: {self.playbook_path}")
            
            # Verify inventory directory
            if not self.inventory_dir.exists():
                raise Exception(f"Inventory directory not found: {self.inventory_dir}")
            
            logger.info(f"Ansible executor initialized (root: {self.ansible_root})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ansible executor: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Ansible executor cleanup complete")
    
    async def get_available_environments(self) -> List[Dict[str, Any]]:
        """Get list of available deployment environments"""
        environments = []
        
        for env in self.environments:
            env_dir = self.inventory_dir / env
            hosts_file = env_dir / "hosts.yml"
            
            if hosts_file.exists():
                try:
                    with open(hosts_file, 'r') as f:
                        inventory_data = yaml.safe_load(f)
                    
                    # Count hosts
                    host_count = 0
                    if inventory_data and 'all' in inventory_data:
                        for group_name, group_data in inventory_data['all'].get('children', {}).items():
                            if 'hosts' in group_data:
                                host_count += len(group_data['hosts'])
                    
                    environments.append({
                        "name": env,
                        "description": f"{env.title()} environment",
                        "host_count": host_count,
                        "available": True
                    })
                except Exception as e:
                    logger.warning(f"Error reading inventory for {env}: {e}")
                    environments.append({
                        "name": env,
                        "description": f"{env.title()} environment",
                        "host_count": 0,
                        "available": False,
                        "error": str(e)
                    })
        
        return environments
    
    async def get_available_components(self) -> Dict[str, Any]:
        """Get list of available components organized by platform"""
        components_by_platform = {}
        
        for component_name, component_info in self.available_components.items():
            platform = component_info["platform"]
            if platform not in components_by_platform:
                components_by_platform[platform] = []
            
            components_by_platform[platform].append({
                "name": component_name,
                "description": component_info["description"],
                "requires": component_info["requires"]
            })
        
        return {
            "by_platform": components_by_platform,
            "all_components": list(self.available_components.keys())
        }
    
    async def execute_component_deployment(
        self,
        environment: str,
        components: List[str],
        target_hosts: Optional[List[str]] = None,
        execution_mode: str = "normal",
        options: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute component deployment using the universal playbook"""
        
        try:
            # Validate environment
            if environment not in self.environments:
                raise ValueError(f"Invalid environment: {environment}")
            
            # Validate components
            invalid_components = [c for c in components if c not in self.available_components]
            if invalid_components:
                raise ValueError(f"Invalid components: {invalid_components}")
            
            # Build inventory path
            inventory_path = self.inventory_dir / environment / "hosts.yml"
            if not inventory_path.exists():
                raise ValueError(f"Inventory not found for environment: {environment}")
            
            # Prepare execution command
            cmd = [
                "ansible-playbook",
                str(self.playbook_path),
                "-i", str(inventory_path),
                "--extra-vars", f"execution_mode=components",
                "--extra-vars", f"selected_components={json.dumps(components)}"
            ]
            
            # Add execution mode options
            if execution_mode != "normal":
                cmd.extend(["--extra-vars", f"execution_mode={execution_mode}"])
            
            # Add additional options
            if options:
                for key, value in options.items():
                    cmd.extend(["--extra-vars", f"{key}={json.dumps(value) if isinstance(value, (dict, list)) else value}"])
            
            # Add target host limit if specified
            if target_hosts:
                cmd.extend(["--limit", ",".join(target_hosts)])
            
            # Add verbose flag for debugging
            if options and options.get("verbose", False):
                cmd.append("-vv")
            
            # Execute the deployment
            logger.info(f"Executing deployment: {' '.join(cmd)}")
            
            start_time = datetime.now(timezone.utc)
            result = await self._run_command_with_logging(cmd, job_id)
            end_time = datetime.now(timezone.utc)
            
            duration = (end_time - start_time).total_seconds()
            
            # Parse results
            success = result["returncode"] == 0
            
            return {
                "success": success,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "command": " ".join(cmd),
                "returncode": result["returncode"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "environment": environment,
                "components": components,
                "execution_mode": execution_mode,
                "target_hosts": target_hosts,
                "job_id": job_id,
                "error": result["stderr"] if not success else None
            }
            
        except Exception as e:
            logger.error(f"Deployment execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "environment": environment,
                "components": components,
                "execution_mode": execution_mode,
                "job_id": job_id
            }
    
    async def validate_deployment_request(
        self,
        environment: str,
        components: List[str],
        target_hosts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate deployment request without executing"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "resolved_components": [],
            "estimated_duration": 0
        }
        
        try:
            # Validate environment
            if environment not in self.environments:
                validation_result["errors"].append(f"Invalid environment: {environment}")
                validation_result["valid"] = False
            
            # Validate components
            invalid_components = [c for c in components if c not in self.available_components]
            if invalid_components:
                validation_result["errors"].append(f"Invalid components: {invalid_components}")
                validation_result["valid"] = False
            
            # Check inventory exists
            inventory_path = self.inventory_dir / environment / "hosts.yml"
            if not inventory_path.exists():
                validation_result["errors"].append(f"No inventory found for environment: {environment}")
                validation_result["valid"] = False
            
            # Simulate dependency resolution (basic implementation)
            if validation_result["valid"]:
                resolved = await self._resolve_component_dependencies(components)
                validation_result["resolved_components"] = resolved
                validation_result["estimated_duration"] = len(resolved) * 3  # 3 minutes per component
            
            # Validate target hosts if specified
            if target_hosts and validation_result["valid"]:
                available_hosts = await self._get_inventory_hosts(environment)
                invalid_hosts = [h for h in target_hosts if h not in available_hosts]
                if invalid_hosts:
                    validation_result["warnings"].append(f"Unknown hosts: {invalid_hosts}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    async def _resolve_component_dependencies(self, components: List[str]) -> List[str]:
        """Simple dependency resolution (matches our framework logic)"""
        resolved = set()
        to_process = list(components)
        
        while to_process:
            component = to_process.pop(0)
            if component in resolved:
                continue
            
            if component not in self.available_components:
                continue
            
            # Add dependencies to processing queue
            deps = self.available_components[component]["requires"]
            for dep in deps:
                if dep not in resolved:
                    to_process.insert(0, dep)
            
            resolved.add(component)
        
        # Sort by priority (base-system first, then by dependency order)
        priority_order = ["base-system", "python", "node", "network-stack"]
        
        def get_priority(comp):
            if comp in priority_order:
                return priority_order.index(comp)
            return 100
        
        return sorted(resolved, key=get_priority)
    
    async def _get_inventory_hosts(self, environment: str) -> List[str]:
        """Get list of hosts from inventory"""
        inventory_path = self.inventory_dir / environment / "hosts.yml"
        hosts = []
        
        try:
            with open(inventory_path, 'r') as f:
                inventory_data = yaml.safe_load(f)
            
            if inventory_data and 'all' in inventory_data:
                for group_name, group_data in inventory_data['all'].get('children', {}).items():
                    if 'hosts' in group_data:
                        hosts.extend(group_data['hosts'].keys())
        
        except Exception as e:
            logger.error(f"Error reading inventory hosts: {e}")
        
        return hosts
    
    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run a command and return result"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.ansible_root
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    async def _run_command_with_logging(self, cmd: List[str], job_id: Optional[str] = None) -> Dict[str, Any]:
        """Run command with real-time logging to job manager"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # Combine streams
                cwd=self.ansible_root
            )
            
            output_lines = []
            
            # Read output line by line
            async for line in process.stdout:
                line_str = line.decode('utf-8', errors='replace').rstrip()
                output_lines.append(line_str)
                
                # Log to job if job_id provided
                if job_id:
                    # Import here to avoid circular imports
                    from jobs.job_manager import JobManager
                    job_manager = JobManager()
                    await job_manager.add_job_log(job_id, line_str)
            
            await process.wait()
            
            return {
                "returncode": process.returncode,
                "stdout": "\n".join(output_lines),
                "stderr": ""  # Combined with stdout
            }
            
        except Exception as e:
            error_msg = str(e)
            if job_id:
                from jobs.job_manager import JobManager
                job_manager = JobManager()
                await job_manager.add_job_log(job_id, f"ERROR: {error_msg}")
            
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": error_msg
            }
    
    async def get_deployment_status(self, environment: str) -> Dict[str, Any]:
        """Get current deployment status for an environment"""
        try:
            # This would typically check running processes, recent deployments, etc.
            # For now, return basic status
            
            inventory_path = self.inventory_dir / environment / "hosts.yml"
            
            return {
                "environment": environment,
                "inventory_exists": inventory_path.exists(),
                "last_deployment": None,  # Would track this in a database
                "active_deployments": 0,  # Would track running jobs
                "status": "ready"
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            return {
                "environment": environment,
                "status": "error",
                "error": str(e)
            }