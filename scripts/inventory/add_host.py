#!/usr/bin/env python3
"""
Host Addition Script for New Inventory Structure
Adds a host to a project environment with proper inheritance
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime

def load_project_metadata(project_dir):
    """Load project metadata"""
    project_file = project_dir / "project.yml"
    if not project_file.exists():
        print(f"ERROR: Project metadata not found at {project_file}")
        return None
        
    with open(project_file, 'r') as f:
        return yaml.safe_load(f)

def load_host_file(host_file_path):
    """Load existing host file"""
    if not host_file_path.exists():
        print(f"ERROR: Host file not found at {host_file_path}")
        return None
        
    with open(host_file_path, 'r') as f:
        return yaml.safe_load(f)

def add_host_to_config(config, project_name, environment, hostname, ip, user, overrides=None):
    """Add host to the configuration"""
    
    # Navigate to the hosts section
    group_name = f"{project_name}_{environment}"
    
    if 'all' not in config:
        config['all'] = {'vars': {}, 'children': {}}
    
    if 'children' not in config['all']:
        config['all']['children'] = {}
        
    if group_name not in config['all']['children']:
        config['all']['children'][group_name] = {'children': {'macos': {'hosts': {}}}}
        
    if 'children' not in config['all']['children'][group_name]:
        config['all']['children'][group_name]['children'] = {'macos': {'hosts': {}}}
        
    if 'macos' not in config['all']['children'][group_name]['children']:
        config['all']['children'][group_name]['children']['macos'] = {'hosts': {}}
        
    if 'hosts' not in config['all']['children'][group_name]['children']['macos']:
        config['all']['children'][group_name]['children']['macos']['hosts'] = {}
    elif config['all']['children'][group_name]['children']['macos']['hosts'] is None:
        config['all']['children'][group_name]['children']['macos']['hosts'] = {}
    
    # Add the host
    host_config = {
        'ansible_host': ip,
        'ansible_user': user,
        'ansible_port': 22,
        'ansible_become_password': f"{{{{ vault_sudo_passwords['{hostname}'] }}}}"
    }
    
    # Add overrides if provided
    if overrides:
        for key, value in overrides.items():
            # Parse nested keys like "player.dual_screen=false"
            if '.' in key:
                parts = key.split('.')
                current = host_config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert string values to proper types
                final_value = value
                if value.lower() == 'true':
                    final_value = True
                elif value.lower() == 'false':
                    final_value = False
                elif value.isdigit():
                    final_value = int(value)
                elif value.replace('.', '').isdigit():
                    final_value = float(value)
                    
                current[parts[-1]] = final_value
            else:
                host_config[key] = value
    
    config['all']['children'][group_name]['children']['macos']['hosts'][hostname] = host_config
    return config

def validate_environment(environment):
    """Validate environment name"""
    valid_environments = ['staging', 'preprod', 'production']
    if environment not in valid_environments:
        print(f"ERROR: Invalid environment '{environment}'")
        print(f"Valid environments: {', '.join(valid_environments)}")
        return False
    return True

def validate_ip_address(ip, environment):
    """Validate IP address based on environment rules"""
    if environment == 'staging':
        # Staging can use local IPs
        if not (ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.')):
            print(f"WARNING: Staging environment typically uses local IP addresses (192.168.x.x, 10.x.x.x, 172.x.x.x)")
    else:
        # Preprod and production should use Tailscale IPs
        if not ip.startswith('100.'):
            print(f"WARNING: {environment.title()} environment should use Tailscale IP addresses (100.x.x.x)")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Add a host to a project environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s yuh staging yuh-staging-001 192.168.1.100 admin
  %(prog)s evenko preprod evenko-ca-001 100.103.229.95 studio --override "player.dual_screen=false"
  %(prog)s f1 production f1-prod-001 100.88.17.33 admin --cam-id "12345-67890" --override "tracker.model=yolo12m.pt"
        """
    )
    
    parser.add_argument('project', help='Project name')
    parser.add_argument('environment', choices=['staging', 'preprod', 'production'], 
                        help='Environment')
    parser.add_argument('hostname', help='Host hostname/identifier')
    parser.add_argument('ip', help='Host IP address')
    parser.add_argument('user', help='Ansible user')
    
    parser.add_argument('--cam-id', help='Camera UUID')
    parser.add_argument('--override', action='append', 
                        help='Host-specific override (format: key=value or nested.key=value)')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show configuration without writing files')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_environment(args.environment):
        sys.exit(1)
        
    if not validate_ip_address(args.ip, args.environment):
        # Warning only, don't exit
        pass
    
    # Get paths
    inventory_dir = Path(__file__).parent.parent.parent / "inventory"
    project_dir = inventory_dir / "30_projects" / args.project
    host_file_path = project_dir / "hosts" / f"{args.environment}.yml"
    
    # Check if project exists
    if not project_dir.exists():
        print(f"ERROR: Project '{args.project}' does not exist")
        print(f"Create it first with: ./scripts/inventory/create_project.py {args.project} <type> --components <components>")
        sys.exit(1)
    
    # Load project metadata
    project_metadata = load_project_metadata(project_dir)
    if not project_metadata:
        sys.exit(1)
    
    # Load existing host configuration
    config = load_host_file(host_file_path)
    if not config:
        sys.exit(1)
    
    # Parse overrides
    overrides = {}
    if args.override:
        for override in args.override:
            if '=' not in override:
                print(f"ERROR: Invalid override format: {override}")
                print("Use format: key=value or nested.key=value")
                sys.exit(1)
            key, value = override.split('=', 1)
            overrides[key.strip()] = value.strip()
    
    if args.cam_id:
        overrides['cam_id'] = args.cam_id
    
    # Check if host already exists
    group_name = f"{args.project}_{args.environment}"
    existing_hosts = []
    try:
        hosts = config['all']['children'][group_name]['children']['macos']['hosts']
        if hosts is not None:
            existing_hosts = list(hosts.keys())
            if args.hostname in existing_hosts:
                print(f"ERROR: Host '{args.hostname}' already exists in {args.project}/{args.environment}")
                print(f"Existing hosts: {', '.join(existing_hosts)}")
                sys.exit(1)
    except (KeyError, TypeError):
        # No existing hosts or incomplete structure, that's fine
        pass
    
    # Add host to configuration
    updated_config = add_host_to_config(
        config, args.project, args.environment, args.hostname, 
        args.ip, args.user, overrides
    )
    
    if args.dry_run:
        print(f"Would add host '{args.hostname}' to {args.project}/{args.environment}:")
        print(f"  IP: {args.ip}")
        print(f"  User: {args.user}")
        if overrides:
            print(f"  Overrides: {overrides}")
        print("\\nResulting configuration:")
        print(yaml.dump(updated_config, default_flow_style=False, sort_keys=False))
        return
    
    # Write updated configuration
    try:
        # Create backup
        backup_path = host_file_path.with_suffix(f'.yml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        with open(host_file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        
        # Write updated config
        with open(host_file_path, 'w') as f:
            f.write("---\n")
            yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"SUCCESS: Added host '{args.hostname}' to {args.project}/{args.environment}")
        print(f"  Configuration: {host_file_path}")
        print(f"  Backup: {backup_path}")
        print(f"  IP: {args.ip}")
        print(f"  User: {args.user}")
        if overrides:
            print(f"  Overrides: {overrides}")
        print(f"\\nNext steps:")
        print(f"  1. Add vault password: ansible-vault edit group_vars/all/vault.yml")
        print(f"  2. Test connection: ansible {args.hostname} -m ping")
        print(f"  3. Deploy components: ./scripts/inventory/deploy_stack.py {args.project} {args.environment}")
        
    except Exception as e:
        print(f"ERROR: Failed to add host: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()