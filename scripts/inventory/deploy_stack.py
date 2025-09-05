#!/usr/bin/env python3
"""
Stack Deployment Script for New Inventory Structure
Deploys component stacks to project environments
"""

import argparse
import sys
import yaml
from pathlib import Path
import subprocess

def load_component_registry():
    """Load the component registry"""
    inventory_dir = Path(__file__).parent.parent.parent / "inventory"
    registry_path = inventory_dir / "10_components" / "_registry.yml"
    
    with open(registry_path, 'r') as f:
        return yaml.safe_load(f)

def load_project_stack(project_dir):
    """Load project stack configuration"""
    stack_file = project_dir / "stack.yml"
    if not stack_file.exists():
        print(f"ERROR: Project stack not found at {stack_file}")
        return None
        
    with open(stack_file, 'r') as f:
        return yaml.safe_load(f)

def get_deployment_order(components, registry):
    """Get components in proper deployment order based on dependencies"""
    deployment_order = registry.get('deployment_order', [])
    
    # Filter to only requested components, maintaining order
    ordered_components = []
    for component in deployment_order:
        if component in components:
            ordered_components.append(component)
    
    # Add any components not in deployment_order
    for component in components:
        if component not in ordered_components:
            ordered_components.append(component)
    
    return ordered_components

def build_ansible_command(project, environment, components, limit_hosts=None, dry_run=False):
    """Build the ansible-playbook command"""
    
    # Base command
    cmd = [
        'ansible-playbook',
        '../main.yml',  # Main playbook
        '-i', f'inventory/30_projects/{project}/hosts/{environment}.yml',  # Inventory
        '--limit', f'{project}_{environment}',  # Limit to project group
    ]
    
    # Add component tags
    if components:
        component_tags = []
        for component in components:
            # Map component names to tags
            if component == 'device-api':
                component_tags.extend(['device-api', 'api'])
            elif component == 'parking-monitor':
                component_tags.append('parking-monitor')
            elif component == 'player':
                component_tags.append('player')
            elif component == 'tracker':
                component_tags.append('tracker')
            elif component == 'camguard':
                component_tags.append('camguard')
            elif component == 'alpr':
                component_tags.append('alpr')
        
        if component_tags:
            cmd.extend(['--tags', ','.join(component_tags)])
    
    # Limit to specific hosts if requested
    if limit_hosts:
        current_limit = f'{project}_{environment}'
        host_limit = f'{current_limit}:&{limit_hosts}'
        cmd[cmd.index('--limit') + 1] = host_limit
    
    # Add dry run flag
    if dry_run:
        cmd.append('--check')
        cmd.append('--diff')
    
    return cmd

def main():
    parser = argparse.ArgumentParser(
        description='Deploy component stack to project environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s yhu staging                    # Deploy all components to yhu staging
  %(prog)s evenko production --components player,camguard  # Deploy specific components
  %(prog)s f1 preprod --hosts f1-ca-001   # Deploy to specific host only
  %(prog)s acme staging --dry-run         # Show what would be deployed
        """
    )
    
    parser.add_argument('project', help='Project name')
    parser.add_argument('environment', choices=['staging', 'preprod', 'production'], 
                        help='Environment')
    
    parser.add_argument('--components', 
                        help='Comma-separated list of components to deploy (default: all from stack)')
    parser.add_argument('--hosts', 
                        help='Comma-separated list of hosts to limit deployment to')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be deployed without making changes')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increase verbosity (use multiple times: -v, -vv, -vvv)')
    
    args = parser.parse_args()
    
    # Get paths
    inventory_dir = Path(__file__).parent.parent.parent / "inventory"
    project_dir = inventory_dir / "30_projects" / args.project
    
    # Check if project exists
    if not project_dir.exists():
        print(f"ERROR: Project '{args.project}' does not exist")
        sys.exit(1)
    
    # Load registry and project stack
    registry = load_component_registry()
    project_stack = load_project_stack(project_dir)
    
    if not project_stack:
        sys.exit(1)
    
    # Determine components to deploy
    if args.components:
        components = [c.strip() for c in args.components.split(',')]
    else:
        components = project_stack['project_stack']['components']
    
    # Validate components
    available_components = set(registry['components'].keys())
    invalid_components = set(components) - available_components
    if invalid_components:
        print(f"ERROR: Invalid components: {', '.join(invalid_components)}")
        print(f"Available components: {', '.join(sorted(available_components))}")
        sys.exit(1)
    
    # Get deployment order
    ordered_components = get_deployment_order(components, registry)
    
    print(f"Deploying to {args.project}/{args.environment}")
    print(f"Components (in deployment order): {' -> '.join(ordered_components)}")
    if args.hosts:
        print(f"Limited to hosts: {args.hosts}")
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
    print()
    
    # Change to oaAnsible directory for ansible-playbook execution
    oaansible_dir = Path(__file__).parent.parent.parent
    
    try:
        # Build and execute ansible command
        cmd = build_ansible_command(
            args.project, 
            args.environment, 
            ordered_components,
            args.hosts,
            args.dry_run
        )
        
        # Add verbosity flags
        if args.verbose >= 1:
            cmd.append('-v')
        if args.verbose >= 2:
            cmd.append('-v')
        if args.verbose >= 3:
            cmd.append('-v')
        
        print(f"Executing: {' '.join(cmd)}")
        print(f"Working directory: {oaansible_dir}")
        print("-" * 80)
        
        # Execute the command
        result = subprocess.run(
            cmd,
            cwd=oaansible_dir,
            check=False,  # Don't raise exception on non-zero exit
            text=True
        )
        
        print("-" * 80)
        if result.returncode == 0:
            print(f"SUCCESS: Deployment completed for {args.project}/{args.environment}")
            print(f"Components deployed: {', '.join(ordered_components)}")
            if not args.dry_run:
                print(f"\\nNext steps:")
                print(f"  1. Verify services: ansible {args.project}_{args.environment} -m shell -a 'launchctl list | grep orangead'")
                print(f"  2. Check health: curl http://<host-ip>:9090/health")
                print(f"  3. View logs: ssh <host> 'tail -f ~/orangead/*/logs/*.log'")
        else:
            print(f"ERROR: Deployment failed with exit code {result.returncode}")
            print("Check the ansible output above for details")
            sys.exit(result.returncode)
            
    except KeyboardInterrupt:
        print("\\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to execute deployment: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()