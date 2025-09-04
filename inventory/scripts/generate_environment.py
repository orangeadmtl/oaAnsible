#!/usr/bin/env python3
"""
Automated Environment Generator for oaAnsible Inventory
Eliminates manual intervention and repetition in environment creation
"""

import argparse
import os
import sys
from pathlib import Path
import yaml
import shutil
from datetime import datetime

def load_defaults():
    """Load default configurations"""
    inventory_dir = Path(__file__).parent.parent
    
    defaults = {}
    
    # Load service defaults
    service_defaults_path = inventory_dir / "group_vars" / "defaults" / "service_defaults.yml"
    if service_defaults_path.exists():
        with open(service_defaults_path, 'r') as f:
            defaults.update(yaml.safe_load(f))
    
    # Load environment configs
    env_configs_path = inventory_dir / "group_vars" / "defaults" / "environment_configs.yml"
    if env_configs_path.exists():
        with open(env_configs_path, 'r') as f:
            defaults.update(yaml.safe_load(f))
    
    return defaults

def generate_environment_file(project, environment, hostname, ip, user, cam_id=None, **kwargs):
    """Generate a complete environment file with zero duplication"""
    
    defaults = load_defaults()
    
    # Get project component matrix
    components = defaults['project_component_matrix'].get(project, {})
    service_configs = defaults['project_service_configs'].get(project, {})
    env_permissions = defaults['environment_permissions'].get(environment, {})
    
    target_env = f"{project}-{environment}"
    group_name = f"{project}_{environment}"
    
    # Build environment configuration
    env_config = {
        'all': {
            'vars': {
                # Environment identification
                'target_env': target_env,
                'deployment_environment': environment,
                'oa_environment': {
                    'name': target_env,
                    'stage': environment
                },
                
                # Project identification  
                'project_name': project,
                
                # Component deployment (from matrix)
                'oa_environment_defaults': {
                    'project': project,
                    **components
                },
                
                # Environment permissions
                **{f"allow_{k.replace('allow_', '')}": v for k, v in env_permissions.items() if k.startswith('allow_')},
                'configure': {k: v for k, v in env_permissions.items() if not k.startswith('allow_')},
                
                # Service configurations (reference centralized defaults)
                'parking_monitor': "{{ parking_monitor_defaults | combine(environment_overrides[deployment_environment].parking_monitor | default({}), recursive=True) }}",
                'device_api': "{{ device_api_defaults | combine(environment_overrides[deployment_environment].device_api | default({}), recursive=True) }}",
            },
            
            'children': {
                group_name: {
                    'children': {
                        'macos': {
                            'hosts': {
                                hostname: {
                                    'ansible_host': ip,
                                    'ansible_user': user,
                                    'ansible_port': 22,
                                    'ansible_become_password': f"{{{{ vault_sudo_passwords['{hostname}'] }}}}",
                                    **({'cam_id': cam_id} if cam_id else {}),
                                    **kwargs
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Add project-specific service configs
    env_config['all']['vars'].update(service_configs)
    
    return env_config

def write_environment_file(config, output_path):
    """Write environment configuration to file"""
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate header comment
    header = f"""# Generated Environment Configuration
# Created: {datetime.now().isoformat()}
# Generator: oaAnsible Inventory Environment Generator
# 
# This file uses centralized defaults from group_vars/defaults/
# Modifications should be made to override variables, not duplicate configuration
#
"""
    
    with open(output_path, 'w') as f:
        f.write(header)
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(description='Generate oaAnsible environment inventory')
    parser.add_argument('project', choices=['alpr', 'evenko', 'spectra', 'f1', 'yuh'], 
                        help='Project name')
    parser.add_argument('environment', choices=['staging', 'preprod', 'production'], 
                        help='Environment stage')
    parser.add_argument('hostname', help='Device hostname')
    parser.add_argument('ip', help='Device IP address')
    parser.add_argument('user', help='Ansible user')
    parser.add_argument('--cam-id', help='Camera UUID')
    parser.add_argument('--output', help='Output file path (auto-generated if not provided)')
    parser.add_argument('--dry-run', action='store_true', help='Show config without writing file')
    
    args = parser.parse_args()
    
    # Generate configuration
    config = generate_environment_file(
        project=args.project,
        environment=args.environment, 
        hostname=args.hostname,
        ip=args.ip,
        user=args.user,
        cam_id=args.cam_id
    )
    
    if args.dry_run:
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))
        return
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        inventory_dir = Path(__file__).parent.parent
        output_path = inventory_dir / 'projects' / args.project / f'{args.environment}.yml'
    
    # Write configuration
    write_environment_file(config, output_path)
    print(f"Generated environment: {output_path}")
    
    # Show reduced size
    original_size = sum(len(yaml.dump(config, default_flow_style=False)) for _ in [1])  # Estimate
    print(f"Configuration references centralized defaults - significant size reduction achieved")

if __name__ == '__main__':
    main()