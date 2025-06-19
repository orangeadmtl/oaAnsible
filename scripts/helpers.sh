#!/bin/bash

# Get the absolute path to the oaAnsible root directory
# This assumes helpers.sh is in oaAnsible/scripts/
OA_ANSIBLE_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OA_ANSIBLE_ROOT_DIR

# Define other common directories relative to the root
OA_ANSIBLE_SCRIPTS_DIR="$OA_ANSIBLE_ROOT_DIR/scripts"
OA_ANSIBLE_INVENTORY_DIR="$OA_ANSIBLE_ROOT_DIR/inventory"
OA_ANSIBLE_ROLES_DIR="$OA_ANSIBLE_ROOT_DIR/roles"
OA_ANSIBLE_TASKS_DIR="$OA_ANSIBLE_ROOT_DIR/tasks"
OA_ANSIBLE_GROUP_VARS_DIR="$OA_ANSIBLE_ROOT_DIR/group_vars"
OA_ANSIBLE_VAULT_PASSWORD_FILE="$OA_ANSIBLE_ROOT_DIR/vault_password_file"
OA_ANSIBLE_LOG_DIR="$OA_ANSIBLE_ROOT_DIR/logs"       # New log directory
OA_ANSIBLE_LOG_FILE="$OA_ANSIBLE_LOG_DIR/script.log" # New log file path
VAULT_YML_FILE="$OA_ANSIBLE_GROUP_VARS_DIR/all/vault.yml"

export OA_ANSIBLE_SCRIPTS_DIR
export OA_ANSIBLE_INVENTORY_DIR
export OA_ANSIBLE_ROLES_DIR
export OA_ANSIBLE_TASKS_DIR
export OA_ANSIBLE_GROUP_VARS_DIR
export OA_ANSIBLE_VAULT_PASSWORD_FILE
export OA_ANSIBLE_LOG_DIR
export OA_ANSIBLE_LOG_FILE
export VAULT_YML_FILE

# Ensure log directory exists
mkdir -p "$OA_ANSIBLE_LOG_DIR"

# --- Logging ---
# Color codes
_COLOR_RED='\033[0;31m'
_COLOR_GREEN='\033[0;32m'
_COLOR_YELLOW='\033[1;33m'
_COLOR_BLUE='\033[0;34m'
_COLOR_NC='\033[0m' # No Color

# Log levels
_LOG_LEVEL_DEBUG=0
_LOG_LEVEL_INFO=1
_LOG_LEVEL_WARN=2
_LOG_LEVEL_ERROR=3

# Current log level for script execution (default to INFO)
# Can be overridden by scripts: SCRIPT_LOG_LEVEL=$_LOG_LEVEL_DEBUG
SCRIPT_LOG_LEVEL=${SCRIPT_LOG_LEVEL:-$_LOG_LEVEL_INFO}

_log() {
  local level_code=$1
  local level_name=$2
  local color_code=$3
  local message=$4
  local timestamp
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")

  if [ "$level_code" -ge "$SCRIPT_LOG_LEVEL" ]; then
    # Log to terminal with color
    if [ -t 1 ]; then # Check if stdout is a terminal
      echo -e "${color_code}[${timestamp}] [${level_name}] ${message}${_COLOR_NC}"
    else # Log to terminal without color (e.g. when redirecting to a file)
      echo "[${timestamp}] [${level_name}] ${message}"
    fi
  fi

  # Always log to file (respecting SCRIPT_LOG_LEVEL for file content too)
  if [ "$level_code" -ge "$SCRIPT_LOG_LEVEL" ]; then
    echo "[${timestamp}] [${level_name}] ${message}" >>"$OA_ANSIBLE_LOG_FILE"
  fi
}

log_info() {
  _log "$_LOG_LEVEL_INFO" "INFO " "$_COLOR_GREEN" "$1"
}

log_warn() {
  _log "$_LOG_LEVEL_WARN" "WARN " "$_COLOR_YELLOW" "$1"
}

log_error() {
  _log "$_LOG_LEVEL_ERROR" "ERROR" "$_COLOR_RED" "$1"
}

log_debug() {
  _log "$_LOG_LEVEL_DEBUG" "DEBUG" "$_COLOR_BLUE" "$1"
}
# --- End Logging ---

# Function to check if a command is installed
check_command_installed() {
  local command_name=$1
  local install_instructions=$2
  local exit_on_error=${3:-true}

  if ! command -v "$command_name" &>/dev/null; then
    log_error "$command_name command not found."
    if [ -n "$install_instructions" ]; then
      log_error "$install_instructions"
    fi
    if [ "$exit_on_error" = true ]; then
      exit 1
    fi
    return 1
  fi
  return 0
}

# Function to ensure scripts are run from oaAnsible root
ensure_ansible_root_dir() {
  if [ "$PWD" != "$OA_ANSIBLE_ROOT_DIR" ]; then
    log_debug "Currently in $PWD, changing to Ansible root directory: $OA_ANSIBLE_ROOT_DIR"
    cd "$OA_ANSIBLE_ROOT_DIR" || {
      log_error "Could not change to Ansible root directory $OA_ANSIBLE_ROOT_DIR"
      exit 1
    }
  fi
}

# Function to check if Ansible is installed
check_ansible_installed() {
  check_command_installed "ansible-playbook" "Please install Ansible first.\nYou can install it with: pip install ansible"
}

# Function to check if ansible-vault is installed
check_ansible_vault_installed() {
  check_command_installed "ansible-vault" "Please ensure Ansible is installed correctly.\nYou can install it with: pip install ansible"
}

# Function to check if yq is installed
check_yq_installed() {
  check_command_installed "yq" "Please install yq (https://github.com/mikefarah/yq/).\nYou can install it with: brew install yq (macOS) or follow instructions at https://github.com/mikefarah/yq/#install"
}

# Function to check if ssh is installed
check_ssh_installed() {
  check_command_installed "ssh" "Please ensure OpenSSH client is installed."
}

# Function to check if vault password file exists
check_vault_password_file() {
  if [ ! -f "$OA_ANSIBLE_VAULT_PASSWORD_FILE" ]; then
    log_error "Ansible vault password file not found at $OA_ANSIBLE_VAULT_PASSWORD_FILE"
    log_error "Please create it and add your vault password."
    exit 1
  fi
}

# Function to discover available inventories dynamically
discover_inventories() {
  local inventories=()
  
  # Look for both old format (directory-based) and new format (file-based)
  
  # Old format: inventory/staging/hosts.yml, inventory/production/hosts.yml, etc.
  for dir in "$OA_ANSIBLE_INVENTORY_DIR"/*; do
    if [ -d "$dir" ] && [ -f "$dir/hosts.yml" ]; then
      inventories+=($(basename "$dir"))
    fi
  done
  
  # New format: inventory/f1-staging.yml, inventory/f1-preprod.yml, etc.
  for file in "$OA_ANSIBLE_INVENTORY_DIR"/*.yml; do
    if [ -f "$file" ]; then
      local basename=$(basename "$file" .yml)
      # Skip if this is inside a directory (already handled above)
      if [[ ! "$basename" =~ ^(staging|production|pre-prod)$ ]]; then
        inventories+=("$basename")
      fi
    fi
  done
  
  # Remove duplicates and sort
  printf '%s\n' "${inventories[@]}" | sort -u
}

# Function to get inventory file path from inventory name
get_inventory_path() {
  local inventory_name="$1"
  
  # Check new format first: inventory/f1-staging.yml
  if [ -f "$OA_ANSIBLE_INVENTORY_DIR/$inventory_name.yml" ]; then
    echo "$OA_ANSIBLE_INVENTORY_DIR/$inventory_name.yml"
    return 0
  fi
  
  # Check old format: inventory/staging/hosts.yml
  if [ -f "$OA_ANSIBLE_INVENTORY_DIR/$inventory_name/hosts.yml" ]; then
    echo "$OA_ANSIBLE_INVENTORY_DIR/$inventory_name/hosts.yml"
    return 0
  fi
  
  return 1
}

# Function to select a target host from an inventory
# Returns 0 on success, 1 on failure
# Sets global variables: TARGET_INVENTORY_PATH, TARGET_HOST_ALIAS
# If extract_connection_details is true, also sets: TARGET_CONNECT_HOST, TARGET_CONNECT_USER, TARGET_CONNECT_PORT
select_target_host() {
  local extract_connection_details=${1:-false}
  
  log_debug "Starting host selection process."
  local inventories=()
  local selected_inventory_name
  local selected_inventory_path
  local host_aliases=() # Initialize as an empty array
  local selected_host_alias

  # Discover available inventories dynamically
  # Use a different approach for older bash versions
  inventories=()
  while IFS= read -r inv; do
    inventories+=("$inv")
  done < <(discover_inventories)
  
  if [ ${#inventories[@]} -eq 0 ]; then
    log_error "No inventories found in $OA_ANSIBLE_INVENTORY_DIR"
    return 1
  fi

  # Select inventory
  log_info "Please select an inventory environment:"
  select inv_choice in "${inventories[@]}"; do
    if [[ -n "$inv_choice" ]]; then
      selected_inventory_name="$inv_choice"
      selected_inventory_path=$(get_inventory_path "$selected_inventory_name")
      if [ $? -ne 0 ] || [ ! -f "$selected_inventory_path" ]; then
        log_error "Inventory file not found for: $selected_inventory_name"
        return 1
      fi
      log_info "Selected inventory: $selected_inventory_name"
      break
    else
      log_warn "Invalid selection. Please try again."
    fi
  done

  # List hosts from selected inventory - check both macOS and Ubuntu groups
  log_debug "Fetching hosts from $selected_inventory_path"
  
  # Get hosts from macOS group
  while IFS= read -r line; do
    if [ -n "$line" ]; then
      host_aliases+=("$line [macOS]")
    fi
  done < <(yq e '.all.children.macos.hosts | keys | .[]' "$selected_inventory_path" 2>/dev/null)
  
  # Get hosts from ubuntu_servers group
  while IFS= read -r line; do
    if [ -n "$line" ]; then
      host_aliases+=("$line [Ubuntu]")
    fi
  done < <(yq e '.all.children.ubuntu_servers.hosts | keys | .[]' "$selected_inventory_path" 2>/dev/null)

  if [ ${#host_aliases[@]} -eq 0 ]; then
    log_error "No hosts found in any supported groups of $selected_inventory_path, or error parsing inventory."
    return 1
  fi

  log_info "Please select a target host from '$selected_inventory_name':"
  select host_choice in "${host_aliases[@]}"; do
    if [[ -n "$host_choice" ]]; then
      # Extract hostname and group from the display format "hostname [group]"
      if [[ "$host_choice" =~ ^(.+)\ \[(macOS|Ubuntu)\]$ ]]; then
        selected_host_alias="${BASH_REMATCH[1]}"
        TARGET_HOST_GROUP_DISPLAY="${BASH_REMATCH[2]}"
        case "$TARGET_HOST_GROUP_DISPLAY" in
          "macOS") TARGET_HOST_GROUP="macos" ;;
          "Ubuntu") TARGET_HOST_GROUP="ubuntu_servers" ;;
        esac
        log_info "Selected host: $selected_host_alias [$TARGET_HOST_GROUP_DISPLAY]"
      else
        selected_host_alias="$host_choice"
        TARGET_HOST_GROUP="macos"  # fallback for backward compatibility
        log_info "Selected host: $selected_host_alias"
      fi
      break
    else
      log_warn "Invalid selection. Please try again."
    fi
  done

  # Export variables for use by the caller
  TARGET_INVENTORY_PATH="$selected_inventory_path"
  TARGET_HOST_ALIAS="$selected_host_alias"

  log_debug "Selected inventory path: $TARGET_INVENTORY_PATH"
  log_debug "Selected host alias: $TARGET_HOST_ALIAS"
  
  # Optionally extract connection details (for SSH)
  if [ "$extract_connection_details" = true ]; then
    # Get ansible_host and ansible_user for the selected host alias from the correct group
    TARGET_CONNECT_HOST=$(yq e ".all.children.${TARGET_HOST_GROUP}.hosts.\"$selected_host_alias\".ansible_host" "$selected_inventory_path")
    TARGET_CONNECT_USER=$(yq e ".all.children.${TARGET_HOST_GROUP}.hosts.\"$selected_host_alias\".ansible_user" "$selected_inventory_path")
    # Query for ansible_port, default to 22 if not found
    TARGET_CONNECT_PORT=$(yq e ".all.children.${TARGET_HOST_GROUP}.hosts.\"$selected_host_alias\".ansible_port // 22" "$selected_inventory_path")

    if [ -z "$TARGET_CONNECT_HOST" ] || [ "$TARGET_CONNECT_HOST" == "null" ]; then
      log_error "Could not determine 'ansible_host' for '$selected_host_alias' in group '$TARGET_HOST_GROUP' from $selected_inventory_path."
      return 1
    fi
    if [ -z "$TARGET_CONNECT_USER" ] || [ "$TARGET_CONNECT_USER" == "null" ]; then
      log_error "Could not determine 'ansible_user' for '$selected_host_alias' in group '$TARGET_HOST_GROUP' from $selected_inventory_path."
      return 1
    fi

    log_debug "Target connection host: $TARGET_CONNECT_HOST"
    log_debug "Target connection user: $TARGET_CONNECT_USER"
    log_debug "Target connection port: $TARGET_CONNECT_PORT"
    log_debug "Target host group: $TARGET_HOST_GROUP"
  fi
  
  return 0
}

# Function to list all available hosts from all inventories
list_all_hosts() {
  local inventories=()
  # Use a different approach for older bash versions
  inventories=()
  while IFS= read -r inv; do
    inventories+=("$inv")
  done < <(discover_inventories)
  
  echo "Available hosts:"
  echo "---------------"
  
  for inv in "${inventories[@]}"; do
    local inventory_path=$(get_inventory_path "$inv")
    if [ $? -ne 0 ] || [ ! -f "$inventory_path" ]; then
      log_warn "Inventory file not found for: $inv"
      continue
    fi
    
    echo "[$inv]"
    # List macOS hosts
    yq e '.all.children.macos.hosts | keys | .[]' "$inventory_path" 2>/dev/null | while read -r host; do
      local host_ip=$(yq e ".all.children.macos.hosts.\"$host\".ansible_host" "$inventory_path")
      echo "  $host ($host_ip) [macOS]"
    done
    # List Ubuntu hosts
    yq e '.all.children.ubuntu_servers.hosts | keys | .[]' "$inventory_path" 2>/dev/null | while read -r host; do
      local host_ip=$(yq e ".all.children.ubuntu_servers.hosts.\"$host\".ansible_host" "$inventory_path")
      echo "  $host ($host_ip) [Ubuntu]"
    done
    echo ""
  done
}

# Function to find a host by name or partial name
# Returns 0 on success, 1 on failure
# Sets global variables: TARGET_INVENTORY_PATH, TARGET_HOST_ALIAS
# If extract_connection_details is true, also sets: TARGET_CONNECT_HOST, TARGET_CONNECT_USER, TARGET_CONNECT_PORT
find_host_by_name() {
  local search_term="$1"
  local specified_inventory="$2"
  local extract_connection_details=${3:-false}
  local inventories=()
  
  if [ -n "$specified_inventory" ]; then
    inventories=("$specified_inventory")
  else
    # Use a different approach for older bash versions
  inventories=()
  while IFS= read -r inv; do
    inventories+=("$inv")
  done < <(discover_inventories)
  fi
  
  local found_hosts=()
  local found_inventories=()
  local found_groups=()
  
  for inv in "${inventories[@]}"; do
    local inventory_path=$(get_inventory_path "$inv")
    if [ $? -ne 0 ] || [ ! -f "$inventory_path" ]; then
      log_warn "Inventory file not found for: $inv"
      continue
    fi
    
    # Search in macOS hosts
    while IFS= read -r host; do
      if [[ "$host" == *"$search_term"* ]]; then
        found_hosts+=("$host")
        found_inventories+=("$inv")
        found_groups+=("macos")
      fi
    done < <(yq e '.all.children.macos.hosts | keys | .[]' "$inventory_path" 2>/dev/null)
    
    # Search in Ubuntu hosts
    while IFS= read -r host; do
      if [[ "$host" == *"$search_term"* ]]; then
        found_hosts+=("$host")
        found_inventories+=("$inv")
        found_groups+=("ubuntu_servers")
      fi
    done < <(yq e '.all.children.ubuntu_servers.hosts | keys | .[]' "$inventory_path" 2>/dev/null)
  done
  
  if [ ${#found_hosts[@]} -eq 0 ]; then
    log_error "No hosts matching '$search_term' found in any inventory."
    return 1
  elif [ ${#found_hosts[@]} -gt 1 ]; then
    log_warn "Multiple hosts match '$search_term':"
    for i in "${!found_hosts[@]}"; do
      echo "$((i+1)). ${found_hosts[$i]} (${found_inventories[$i]}) [${found_groups[$i]}]"
    done
    
    echo "Please select a host:"
    local selection
    read -r selection
    
    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#found_hosts[@]} ]; then
      log_error "Invalid selection."
      return 1
    fi
    
    selected_index=$((selection-1))
    selected_host_alias="${found_hosts[$selected_index]}"
    selected_inventory_name="${found_inventories[$selected_index]}"
    selected_host_group="${found_groups[$selected_index]}"
  else
    selected_host_alias="${found_hosts[0]}"
    selected_inventory_name="${found_inventories[0]}"
    selected_host_group="${found_groups[0]}"
  fi
  
  selected_inventory_path=$(get_inventory_path "$selected_inventory_name")
  
  # Set the global variables
  TARGET_HOST_ALIAS="$selected_host_alias"
  TARGET_INVENTORY_PATH="$selected_inventory_path"
  TARGET_HOST_GROUP="$selected_host_group"
  
  # Optionally extract connection details
  if [ "$extract_connection_details" = true ]; then
    # Get connection details based on the group
    TARGET_CONNECT_HOST=$(yq e ".all.children.${selected_host_group}.hosts.\"$selected_host_alias\".ansible_host" "$selected_inventory_path")
    TARGET_CONNECT_USER=$(yq e ".all.children.${selected_host_group}.hosts.\"$selected_host_alias\".ansible_user" "$selected_inventory_path")
    TARGET_CONNECT_PORT=$(yq e ".all.children.${selected_host_group}.hosts.\"$selected_host_alias\".ansible_port // 22" "$selected_inventory_path")
    
    if [ -z "$TARGET_CONNECT_HOST" ] || [ "$TARGET_CONNECT_HOST" == "null" ]; then
      log_error "Could not determine 'ansible_host' for '$selected_host_alias' in group '$selected_host_group' from $selected_inventory_path."
      return 1
    fi
    if [ -z "$TARGET_CONNECT_USER" ] || [ "$TARGET_CONNECT_USER" == "null" ]; then
      log_error "Could not determine 'ansible_user' for '$selected_host_alias' in group '$selected_host_group' from $selected_inventory_path."
      return 1
    fi
    
    log_debug "Target connection host: $TARGET_CONNECT_HOST"
    log_debug "Target connection user: $TARGET_CONNECT_USER"
    log_debug "Target connection port: $TARGET_CONNECT_PORT"
    log_debug "Target host group: $selected_host_group"
  fi
  
  log_info "Found host: $selected_host_alias in $selected_inventory_name"
  return 0
}

# Function to find the closest virtual environment starting from a given directory
# Searches upward in the directory tree until it finds a .venv directory with a valid Python executable
# Returns 0 on success and echoes the path to the .venv directory
# Returns 1 on failure (no .venv found)
find_closest_venv() {
    local current_dir="${1:-$PWD}"
    
    # Check if .venv exists in the current directory
    if [ -d "$current_dir/.venv" ] && [ -f "$current_dir/.venv/bin/python" ]; then
        echo "$current_dir/.venv"
        return 0
    fi
    
    # If not found and we're not at root, check parent directory
    if [ "$current_dir" != "/" ]; then
        local parent_dir="$(dirname "$current_dir")"
        if [ "$parent_dir" != "$current_dir" ]; then
            find_closest_venv "$parent_dir"
            return $?
        fi
    fi
    
    return 1
}

# Function to get the appropriate Python executable
# First tries to find a virtual environment, then falls back to system Python
# Sets global variables: VENV_PATH and PYTHON_BIN
# Returns 0 on success, 1 on failure
get_python_executable() {
    local start_dir="${1:-$OA_ANSIBLE_ROOT_DIR}"
    
    # Try to find venv starting from the specified directory
    VENV_PATH=$(find_closest_venv "$start_dir")
    
    if [ -n "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/python" ]; then
        log_info "Using Python from virtual environment at $VENV_PATH"
        PYTHON_BIN="$VENV_PATH/bin/python"
        export VENV_PATH
        export PYTHON_BIN
        return 0
    else
        log_warn "No virtual environment found in $start_dir or parent directories, using system Python"
        VENV_PATH=""
        PYTHON_BIN="python3"
        export VENV_PATH
        export PYTHON_BIN
        return 0
    fi
}

# SSH Key Management Functions
# Load SSH private key from Ansible Vault into ssh-agent
load_ssh_key_from_vault() {
    local context="${1:-deployment}"
    
    log_info "Checking and loading SSH key into agent for $context..."
    
    # Ensure ssh-agent is running for this script's execution context
    # Using >/dev/null to suppress the agent's output unless debugging
    if ! ssh-add -l >/dev/null 2>&1; then # Check if agent has any keys / is reachable
        log_info "ssh-agent not running or no keys loaded. Starting agent..."
        eval "$(ssh-agent -s)" >/dev/null
        if [ $? -ne 0 ]; then
            log_error "Failed to start ssh-agent. Please start it manually."
            exit 1
        fi
    fi
    
    # Use the exported VAULT_YML_FILE variable
    local vault_yml_file="$VAULT_YML_FILE"
    
    # Check for required dependencies
    check_vault_password_file
    check_yq_installed
    check_ansible_vault_installed
    
    log_info "Loading SSH private key from vault..."
    if ansible-vault view "$vault_yml_file" --vault-password-file "$OA_ANSIBLE_VAULT_PASSWORD_FILE" |
        yq -re '.vault_ssh_private_key // ""' |
        ssh-add - >/dev/null 2>&1; then
        log_info "SSH key successfully loaded into ssh-agent."
    else
        if ssh-add -l >/dev/null 2>&1; then
            log_warn "Could not add vault key (may already be loaded, or requires passphrase). An identity is present in the agent."
        else
            log_error "Failed to add SSH key from vault to ssh-agent AND no keys are present in the agent."
            log_error "Make sure 'vault_ssh_private_key' exists in '$vault_yml_file' and is a valid private key."
            log_error "SSH authentication for Ansible may fail."
            return 1
        fi
    fi
    
    return 0
}

# Enhanced deployment function with SSH key loading
run_ansible_playbook_with_ssh() {
    local playbook="$1"
    local inventory="$2"
    local context="${3:-deployment}"
    shift 3  # Remove first 3 arguments, rest are passed to ansible-playbook
    
    # Load SSH key from vault
    if ! load_ssh_key_from_vault "$context"; then
        log_error "SSH key loading failed. Deployment may not work properly."
        # Continue anyway in case there are other keys available
    fi
    
    log_info "Loading vault variables for inventory template resolution..."
    
    # Ensure we're in the correct directory
    ensure_ansible_root_dir
    
    log_info "Running Ansible playbook: $playbook"
    log_info "Inventory: $inventory"
    log_info "Context: $context"
    
    # Run the playbook with all remaining arguments
    # Add explicit vault loading to ensure inventory templates can resolve vault variables
    ANSIBLE_CONFIG=ansible.cfg ansible-playbook "$playbook" -i "$inventory" --vault-password-file "$OA_ANSIBLE_VAULT_PASSWORD_FILE" --extra-vars "@$VAULT_YML_FILE" "$@"
    
    return $?
}

# Simplified function for running playbooks with environment-specific defaults
run_environment_playbook() {
    local environment="$1"
    shift  # Remove environment argument, rest are passed through
    
    local inventory=$(get_inventory_path "$environment")
    local context="$environment deployment"
    
    # Check if inventory exists
    if [[ $? -ne 0 ]] || [[ ! -f "$inventory" ]]; then
        log_error "Inventory file not found for environment: $environment"
        log_error "Available inventories: $(discover_inventories | tr '\n' ' ')"
        return 1
    fi
    
    run_ansible_playbook_with_ssh "main.yml" "$inventory" "$context" "$@"
}

# Function for running any playbook with proper vault and SSH setup
run_playbook_with_vault() {
    local playbook="$1"
    local inventory="$2"
    local context="${3:-playbook execution}"
    shift 3  # Remove first 3 arguments, rest are passed to ansible-playbook
    
    # Load SSH key from vault
    if ! load_ssh_key_from_vault "$context"; then
        log_error "SSH key loading failed. Playbook execution may not work properly."
        # Continue anyway in case there are other keys available
    fi
    
    log_info "Loading vault variables for inventory template resolution..."
    
    # Ensure we're in the correct directory
    ensure_ansible_root_dir
    
    log_info "Running Ansible playbook: $playbook"
    log_info "Inventory: $inventory"
    log_info "Context: $context"
    
    # Check for required dependencies
    check_vault_password_file
    check_ansible_installed
    
    # Run the playbook with all remaining arguments
    # Add explicit vault loading to ensure inventory templates can resolve vault variables
    ANSIBLE_CONFIG=ansible.cfg ansible-playbook "$playbook" -i "$inventory" --vault-password-file "$OA_ANSIBLE_VAULT_PASSWORD_FILE" --extra-vars "@$VAULT_YML_FILE" "$@"
    
    return $?
}

# Example of setting a different log level for a specific script:
# At the top of your script, after sourcing helpers.sh:
# SCRIPT_LOG_LEVEL=$_LOG_LEVEL_DEBUG # To see debug messages for this script
