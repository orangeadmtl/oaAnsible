#!/usr/bin/env python3
"""
Inventory Validation Script
Validates the new inventory structure for completeness and correctness
"""

import argparse
import sys
import yaml
from pathlib import Path
import re

class InventoryValidator:
    def __init__(self, inventory_dir):
        self.inventory_dir = Path(inventory_dir)
        self.errors = []
        self.warnings = []
        
    def error(self, message):
        self.errors.append(message)
        
    def warning(self, message):
        self.warnings.append(message)
        
    def validate_directory_structure(self):
        """Validate the basic directory structure exists"""
        required_dirs = [
            "00_foundation",
            "10_components", 
            "20_environments",
            "30_projects",
            "40_host_overrides"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.inventory_dir / dir_name
            if not dir_path.exists():
                self.error(f"Missing required directory: {dir_name}")
            elif not dir_path.is_dir():
                self.error(f"Path exists but is not a directory: {dir_name}")
                
    def validate_component_registry(self):
        """Validate the component registry"""
        registry_path = self.inventory_dir / "10_components" / "_registry.yml"
        
        if not registry_path.exists():
            self.error("Missing component registry: 10_components/_registry.yml")
            return None
            
        try:
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.error(f"Invalid YAML in component registry: {e}")
            return None
            
        if 'components' not in registry:
            self.error("Component registry missing 'components' section")
            return None
            
        components = registry['components']
        
        # Check device-api is mandatory
        if 'device-api' not in components:
            self.error("Component registry missing mandatory 'device-api' component")
        elif not components['device-api'].get('mandatory', False):
            self.error("Component 'device-api' must be marked as mandatory")
            
        # Validate component structure
        for comp_name, comp_config in components.items():
            required_fields = ['name', 'description', 'platforms', 'dependencies']
            for field in required_fields:
                if field not in comp_config:
                    self.error(f"Component '{comp_name}' missing required field: {field}")
                    
        return registry
        
    def validate_components(self, registry):
        """Validate individual component files"""
        if not registry:
            return
            
        components_dir = self.inventory_dir / "10_components"
        
        for comp_name in registry['components']:
            comp_file = components_dir / f"{comp_name}.yml"
            if not comp_file.exists():
                self.error(f"Missing component file: 10_components/{comp_name}.yml")
                continue
                
            try:
                with open(comp_file, 'r') as f:
                    comp_config = yaml.safe_load(f)
                    
                # Check basic structure
                expected_key = f"{comp_name.replace('-', '_')}_component"
                if expected_key not in comp_config:
                    self.error(f"Component '{comp_name}' missing '{expected_key}' section")
                    
            except yaml.YAMLError as e:
                self.error(f"Invalid YAML in component file {comp_name}.yml: {e}")
                
    def validate_environments(self):
        """Validate environment configurations"""
        environments_dir = self.inventory_dir / "20_environments"
        required_envs = ['staging.yml', 'preprod.yml', 'production.yml']
        
        for env_file in required_envs:
            env_path = environments_dir / env_file
            if not env_path.exists():
                self.error(f"Missing environment file: 20_environments/{env_file}")
                continue
                
            try:
                with open(env_path, 'r') as f:
                    env_config = yaml.safe_load(f)
                    
                if 'environment' not in env_config:
                    self.error(f"Environment file {env_file} missing 'environment' section")
                    
                # Validate network access rules
                env_name = env_file.replace('.yml', '')
                env_data = env_config.get('environment', {})
                
                if env_name == 'staging':
                    if env_data.get('type') != 'local':
                        self.warning(f"Staging environment should be type 'local'")
                    features = env_config.get('features', {})
                    if not features.get('tailscale_configuration', False):
                        self.warning("Staging should allow Tailscale configuration")
                        
                elif env_name in ['preprod', 'production']:
                    if env_data.get('type') != 'remote':
                        self.warning(f"{env_name.title()} environment should be type 'remote'")
                    features = env_config.get('features', {})
                    if features.get('tailscale_configuration', True):
                        self.error(f"{env_name.title()} must NOT allow Tailscale configuration")
                        
            except yaml.YAMLError as e:
                self.error(f"Invalid YAML in environment file {env_file}: {e}")
                
    def validate_foundation(self):
        """Validate foundation layer"""
        foundation_dir = self.inventory_dir / "00_foundation"
        required_files = ['all.yml', 'base_setup.yml', 'network.yml', 'security.yml']
        
        for file_name in required_files:
            file_path = foundation_dir / file_name
            if not file_path.exists():
                self.error(f"Missing foundation file: 00_foundation/{file_name}")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.error(f"Invalid YAML in foundation file {file_name}: {e}")
                
    def validate_projects(self):
        """Validate project configurations"""
        projects_dir = self.inventory_dir / "30_projects"
        
        if not projects_dir.exists():
            self.error("Missing projects directory: 30_projects")
            return
            
        # Check template exists
        template_dir = projects_dir / "_template"
        if not template_dir.exists():
            self.error("Missing project template: 30_projects/_template")
        else:
            # Validate template structure
            template_files = ['project.yml', 'stack.yml']
            for file_name in template_files:
                if not (template_dir / file_name).exists():
                    self.error(f"Missing template file: _template/{file_name}")
                    
            hosts_dir = template_dir / "hosts"
            if hosts_dir.exists():
                for env in ['staging.yml', 'preprod.yml', 'production.yml']:
                    if not (hosts_dir / env).exists():
                        self.warning(f"Missing template host file: _template/hosts/{env}")
                        
        # Validate existing projects
        for project_dir in projects_dir.iterdir():
            if project_dir.name.startswith('_') or not project_dir.is_dir():
                continue
                
            self.validate_project(project_dir)
            
    def validate_project(self, project_dir):
        """Validate a single project"""
        project_name = project_dir.name
        
        # Check required files
        required_files = ['project.yml', 'stack.yml']
        for file_name in required_files:
            file_path = project_dir / file_name
            if not file_path.exists():
                self.error(f"Project '{project_name}' missing {file_name}")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if file_name == 'stack.yml':
                    self.validate_project_stack(project_name, config)
                    
            except yaml.YAMLError as e:
                self.error(f"Invalid YAML in {project_name}/{file_name}: {e}")
                
        # Check hosts directory
        hosts_dir = project_dir / "hosts"
        if not hosts_dir.exists():
            self.error(f"Project '{project_name}' missing hosts directory")
        else:
            for env in ['staging.yml', 'preprod.yml', 'production.yml']:
                env_file = hosts_dir / env
                if env_file.exists():
                    self.validate_project_hosts(project_name, env.replace('.yml', ''), env_file)
                    
    def validate_project_stack(self, project_name, stack_config):
        """Validate project stack configuration"""
        if 'project_stack' not in stack_config:
            self.error(f"Project '{project_name}' stack.yml missing 'project_stack' section")
            return
            
        stack = stack_config['project_stack']
        
        if 'components' not in stack:
            self.error(f"Project '{project_name}' stack missing 'components' list")
            return
            
        components = stack['components']
        
        # device-api should always be included
        if 'device-api' not in components:
            self.warning(f"Project '{project_name}' should include mandatory 'device-api' component")
            
    def validate_project_hosts(self, project_name, environment, hosts_file):
        """Validate project host configuration"""
        try:
            with open(hosts_file, 'r') as f:
                config = yaml.safe_load(f)
                
            if not config or 'all' not in config:
                self.error(f"Project '{project_name}' {environment} hosts file has invalid structure")
                return
                
            # Check for proper group naming
            expected_group = f"{project_name}_{environment}"
            if 'children' in config['all']:
                if expected_group not in config['all']['children']:
                    self.warning(f"Project '{project_name}' {environment} missing expected group '{expected_group}'")
                    
        except yaml.YAMLError as e:
            self.error(f"Invalid YAML in {project_name} {environment} hosts: {e}")
            
    def validate_host_overrides(self):
        """Validate host override structure"""
        overrides_dir = self.inventory_dir / "40_host_overrides"
        
        if not overrides_dir.exists():
            self.warning("No host overrides directory found")
            return
            
        # Check structure
        for subdir in ['by_hostname', 'by_capability']:
            subdir_path = overrides_dir / subdir
            if not subdir_path.exists():
                self.warning(f"Missing host overrides subdirectory: {subdir}")
                
    def run_validation(self):
        """Run all validations"""
        print("Validating inventory structure...")
        
        self.validate_directory_structure()
        registry = self.validate_component_registry()
        self.validate_components(registry)
        self.validate_environments()
        self.validate_foundation()
        self.validate_projects()
        self.validate_host_overrides()
        
        return len(self.errors) == 0
        
    def print_results(self):
        """Print validation results"""
        if self.warnings:
            print("\\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
                
        if self.errors:
            print("\\nERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")
        else:
            print("\\n✅ Inventory structure validation passed!")
            
        print(f"\\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")

def main():
    parser = argparse.ArgumentParser(description='Validate oaAnsible inventory structure')
    parser.add_argument('--inventory-dir', default=None,
                        help='Path to inventory directory (default: auto-detect)')
    
    args = parser.parse_args()
    
    # Auto-detect inventory directory
    if args.inventory_dir:
        inventory_dir = Path(args.inventory_dir)
    else:
        script_dir = Path(__file__).parent
        inventory_dir = script_dir.parent.parent / "inventory"
        
    if not inventory_dir.exists():
        print(f"ERROR: Inventory directory not found: {inventory_dir}")
        sys.exit(1)
        
    validator = InventoryValidator(inventory_dir)
    success = validator.run_validation()
    validator.print_results()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()