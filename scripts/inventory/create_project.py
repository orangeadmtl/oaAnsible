#!/usr/bin/env python3
"""
Project Creation Script for New Inventory Structure
Creates a new project with proper component stack selection
"""

import argparse
import os
import sys
import shutil
from pathlib import Path
import yaml
from datetime import datetime

def load_component_registry():
    """Load the component registry to validate component selections"""
    inventory_dir = Path(__file__).parent.parent.parent / "inventory"
    registry_path = inventory_dir / "10_components" / "_registry.yml"
    
    if not registry_path.exists():
        print(f"ERROR: Component registry not found at {registry_path}")
        sys.exit(1)
        
    with open(registry_path, 'r') as f:
        registry = yaml.safe_load(f)
    
    return registry['components']

def validate_components(components, registry):
    """Validate that all requested components exist in the registry"""
    available_components = set(registry.keys())
    requested_components = set(components)
    
    invalid_components = requested_components - available_components
    if invalid_components:
        print(f"ERROR: Invalid components: {', '.join(invalid_components)}")
        print(f"Available components: {', '.join(sorted(available_components))}")
        return False
        
    # Always include device-api (mandatory)
    if 'device-api' not in requested_components:
        components.insert(0, 'device-api')
        print("INFO: Added mandatory 'device-api' component")
        
    return True

def create_project_directory(inventory_dir, project_name):
    """Create the project directory structure"""
    project_dir = inventory_dir / "30_projects" / project_name
    
    if project_dir.exists():
        print(f"ERROR: Project '{project_name}' already exists")
        return None
        
    # Create directory structure
    project_dir.mkdir(parents=True)
    (project_dir / "hosts").mkdir()
    
    return project_dir

def generate_project_metadata(project_name, project_type, description, location):
    """Generate project.yml content"""
    return {
        'project_metadata': {
            'name': project_name,
            'type': project_type,
            'description': description,
            'location': location,
            'contacts': {
                'primary': "REPLACE_WITH_PRIMARY_CONTACT",
                'technical': "REPLACE_WITH_TECHNICAL_CONTACT"
            },
            'configuration': {
                'timezone': "UTC",
                'locale': "en_US.UTF-8"
            },
            'custom_vars': {}
        }
    }

def generate_project_stack(components, component_configs=None):
    """Generate stack.yml content"""
    stack = {
        'project_stack': {
            'components': components,
            'component_configs': component_configs or {},
            'host_roles': {},
            'environment_overrides': {
                'staging': {},
                'preprod': {},
                'production': {}
            }
        }
    }
    return stack

def create_host_files(project_dir, project_name):
    """Create host files for each environment"""
    template_dir = project_dir.parent / "_template" / "hosts"
    
    for env in ['staging', 'preprod', 'production']:
        template_file = template_dir / f"{env}.yml"
        target_file = project_dir / "hosts" / f"{env}.yml"
        
        if template_file.exists():
            # Copy template and replace placeholders
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Replace template placeholders
            content = content.replace('{{ project_metadata.name }}', project_name)
            
            with open(target_file, 'w') as f:
                f.write(content)
        else:
            print(f"WARNING: Template {env}.yml not found, creating basic structure")
            basic_host_config = {
                'all': {
                    'vars': {
                        'target_env': f"{project_name}-{env}",
                        'deployment_environment': env,
                        'project_name': project_name
                    },
                    'children': {
                        f"{project_name}_{env}": {
                            'children': {
                                'macos': {
                                    'hosts': {
                                        # Placeholder - add hosts manually
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            with open(target_file, 'w') as f:
                f.write("# Generated host file - add your hosts here\n")
                yaml.dump(basic_host_config, f, default_flow_style=False, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(
        description='Create a new project in the oaAnsible inventory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s yuh airport --components parking-monitor --description "YUH Airport parking monitoring"
  %(prog)s evenko venue --components player,camguard --description "Evenko events video display"
  %(prog)s acme demo --components device-api,tracker --location "ACME Corp Demo Site"
        """
    )
    
    parser.add_argument('name', help='Project name (lowercase, no spaces)')
    parser.add_argument('type', choices=['airport', 'venue', 'sports', 'demo', 'ml'], 
                        help='Project type')
    parser.add_argument('--components', 
                        help='Comma-separated list of components (device-api is automatic)')
    parser.add_argument('--description', default='', 
                        help='Project description')
    parser.add_argument('--location', default='', 
                        help='Project location')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be created without creating files')
    
    args = parser.parse_args()
    
    # Validate project name
    if not args.name.replace('-', '').replace('_', '').isalnum():
        print("ERROR: Project name must be alphanumeric (with - or _ allowed)")
        sys.exit(1)
    
    # Load component registry
    registry = load_component_registry()
    
    # Parse and validate components
    components = []
    if args.components:
        components = [c.strip() for c in args.components.split(',')]
    
    if not validate_components(components, registry):
        sys.exit(1)
    
    if args.dry_run:
        print(f"Would create project '{args.name}' with:")
        print(f"  Type: {args.type}")
        print(f"  Components: {', '.join(components)}")
        print(f"  Description: {args.description}")
        print(f"  Location: {args.location}")
        return
    
    # Get inventory directory
    inventory_dir = Path(__file__).parent.parent.parent / "inventory"
    
    # Create project directory
    project_dir = create_project_directory(inventory_dir, args.name)
    if not project_dir:
        sys.exit(1)
    
    # Generate and write project files
    try:
        # Create project.yml
        project_metadata = generate_project_metadata(
            args.name, args.type, args.description, args.location
        )
        with open(project_dir / "project.yml", 'w') as f:
            f.write("---\n")
            yaml.dump(project_metadata, f, default_flow_style=False, sort_keys=False)
        
        # Create stack.yml
        project_stack = generate_project_stack(components)
        with open(project_dir / "stack.yml", 'w') as f:
            f.write("---\n")
            yaml.dump(project_stack, f, default_flow_style=False, sort_keys=False)
        
        # Create host files
        create_host_files(project_dir, args.name)
        
        print(f"SUCCESS: Created project '{args.name}'")
        print(f"  Location: {project_dir}")
        print(f"  Components: {', '.join(components)}")
        print(f"  Next steps:")
        print(f"    1. Edit {project_dir}/hosts/staging.yml to add your hosts")
        print(f"    2. Customize {project_dir}/stack.yml for component configurations")
        print(f"    3. Run: ./scripts/inventory/add_host.py {args.name} staging <hostname> <ip> <user>")
        
    except Exception as e:
        print(f"ERROR: Failed to create project: {e}")
        # Cleanup on failure
        if project_dir.exists():
            shutil.rmtree(project_dir)
        sys.exit(1)

if __name__ == '__main__':
    main()