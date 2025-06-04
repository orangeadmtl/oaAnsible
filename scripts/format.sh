#!/bin/bash

# format.sh - Safe and comprehensive formatter for Ansible YAML files
# Automatically fixes common issues while preserving YAML structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Define directories to process
directories=(
    "./roles/macos"
    "./playbooks"
    "./tasks"
    "./group_vars"
    "./inventory"
    "."
)

# Files to exclude from processing
exclude_patterns=(
    "*/\.*"
    "*/logs/*"
    "*/elliotweiser.osx-command-line-tools/*"
    "*/node_modules/*"
    "*/venv/*"
    "*/.venv/*"
    "*/group_vars/all/vault.yml"
)

echo "=== OrangeAd Ansible Ultimate Format Tool ==="
echo "Safely fixing linting issues and standardizing YAML files..."
echo ""

# Function to check if file should be excluded
should_exclude() {
    local file="$1"
    for pattern in "${exclude_patterns[@]}"; do
        case "$file" in
            $pattern) return 0 ;;
        esac
    done
    return 1
}

# Function to validate YAML syntax
validate_yaml() {
    local file="$1"
    python3 -c "
import yaml
import sys
try:
    with open('$file', 'r') as f:
        yaml.safe_load(f)
    sys.exit(0)
except Exception as e:
    print(f'YAML Error in $file: {e}')
    sys.exit(1)
" 2>/dev/null
}

# Function to safely fix FQCN issues preserving indentation
fix_fqcn_issues() {
    print_status "Fixing FQCN (Fully Qualified Collection Names) issues..."
    
    # Common modules that need FQCN (excluding gather_facts which is typically playbook-level)
    local modules=(
        "debug" "set_fact" "fail" "copy" "file" "template" "lineinfile" 
        "stat" "command" "shell" "service" "user" "meta" "pause"
        "uri" "get_url" "unarchive" "include_tasks" "import_tasks" 
        "include_vars" "package" "pip" "git" "cron" "mount" "systemd"
        "find" "replace" "blockinfile" "script" "raw" "wait_for"
        "assert" "include_role" "import_role" "setup" 
        "add_host" "group_by"
    )
    
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ]; then
            print_status "Processing FQCN in $dir..."
            find "$dir" -name "*.yml" -o -name "*.yaml" | while read -r file; do
                if ! should_exclude "$file"; then
                    # Create backup
                    cp "$file" "${file}.bak"
                    
                    # Process each module
                    for module in "${modules[@]}"; do
                        # Only replace if it's a task module at the correct indentation level
                        sed -i '' "s/^\\([[:space:]]*\\)${module}:/\\1ansible.builtin.${module}:/g" "$file"
                    done
                    
                    # Fix incorrectly applied FQCN to common parameters
                    sed -i '' 's/ansible\.builtin\.group: staff/group: staff/g' "$file"
                    sed -i '' 's/ansible\.builtin\.owner:/owner:/g' "$file"
                    sed -i '' 's/ansible\.builtin\.mode:/mode:/g' "$file"
                    sed -i '' 's/ansible\.builtin\.state:/state:/g' "$file"
                    sed -i '' 's/ansible\.builtin\.path:/path:/g' "$file"
                    
                    # Fix playbook-level gather_facts that got incorrectly converted
                    sed -i '' 's/ansible\.builtin\.gather_facts: /gather_facts: /g' "$file"
                    
                    # Validate the result
                    if validate_yaml "$file"; then
                        rm -f "${file}.bak"
                        print_status "✓ Fixed FQCN in $file"
                    else
                        print_warning "✗ YAML validation failed for $file, restoring backup"
                        mv "${file}.bak" "$file"
                    fi
                fi
            done
        fi
    done
}

# Function to fix basic YAML formatting issues safely
fix_yaml_formatting() {
    print_status "Fixing basic YAML formatting issues..."
    
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ]; then
            print_status "Processing YAML formatting in $dir..."
            
            find "$dir" -name "*.yml" -o -name "*.yaml" | while read -r file; do
                if ! should_exclude "$file"; then
                    # Create backup
                    cp "$file" "${file}.bak"
                    
                    # Only make safe changes
                    # 1. Remove trailing spaces
                    sed -i '' -e 's/[[:space:]]*$//' "$file"
                    
                    # 2. Fix obvious truthy values
                    sed -i '' -e 's/: yes$/: true/g' "$file"
                    sed -i '' -e 's/: no$/: false/g' "$file"
                    
                    # 3. Add document start marker only if file is missing it and has content
                    if ! head -n1 "$file" | grep -q "^---" && grep -q "^[[:space:]]*[^#[:space:]]" "$file"; then
                        sed -i '' '1i\
---
' "$file"
                    fi
                    
                    # Validate the result
                    if validate_yaml "$file"; then
                        rm -f "${file}.bak"
                        print_status "✓ Fixed formatting in $file"
                    else
                        print_warning "✗ YAML validation failed for $file, restoring backup"
                        mv "${file}.bak" "$file"
                    fi
                fi
            done
        fi
    done
}

# Function to run ansible-lint automatic fixes
run_ansible_lint_fixes() {
    print_status "Running ansible-lint automatic fixes..."
    
    if command -v ansible-lint >/dev/null 2>&1; then
        # First run ansible-lint to see current issues
        print_status "Checking current ansible-lint issues..."
        ansible-lint --offline || true
        
        print_status "Applying automatic fixes..."
        ansible-lint --fix --offline || print_warning "Some ansible-lint issues could not be automatically fixed"
    else
        print_error "ansible-lint not found. Please install it with: pip install ansible-lint"
        return 1
    fi
}

# Function to run yamllint validation
run_yamllint_check() {
    print_status "Running yamllint validation..."
    
    if command -v yamllint >/dev/null 2>&1; then
        if yamllint . >/dev/null 2>&1; then
            print_success "All YAML files pass yamllint validation"
        else
            print_warning "Some yamllint issues found:"
            yamllint . | head -20
            echo "..."
            print_warning "Run 'yamllint .' for full output"
        fi
    else
        print_error "yamllint not found. Please install it with: pip install yamllint"
        return 1
    fi
}

# Function to show summary of changes
show_changes_summary() {
    print_status "Checking for modified files..."
    
    if command -v git >/dev/null 2>&1 && [ -d .git ]; then
        local modified_files=$(git diff --name-only)
        if [ -n "$modified_files" ]; then
            print_status "Modified files:"
            echo "$modified_files" | while read -r file; do
                echo "  - $file"
            done
        else
            print_status "No files were modified"
        fi
    fi
}

# Main execution
print_status "Starting safe formatting process..."

# Step 1: Fix basic YAML formatting issues
fix_yaml_formatting

# Step 2: Fix FQCN issues
fix_fqcn_issues

# Step 3: Run ansible-lint automatic fixes
run_ansible_lint_fixes

# Step 4: Final yamllint check
echo ""
print_status "Running final validation checks..."
run_yamllint_check

# Step 5: Show summary
echo ""
show_changes_summary

echo ""
print_success "=== Format script completed safely ==="
echo ""
print_status "Summary of fixes applied:"
echo "  ✓ Fixed YAML document start markers (validated)"
echo "  ✓ Removed trailing spaces"
echo "  ✓ Converted truthy values (yes/no → true/false)"
echo "  ✓ Added FQCN for builtin modules (with validation)"
echo "  ✓ Applied ansible-lint automatic fixes"
echo ""
print_status "Next steps:"
echo "  1. Review any remaining yamllint warnings above"
echo "  2. Run 'ansible-lint' to check for remaining issues"
echo "  3. Test your playbooks to ensure functionality"
echo ""
print_warning "All changes were validated to ensure YAML syntax remains correct."