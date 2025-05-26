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

export OA_ANSIBLE_SCRIPTS_DIR
export OA_ANSIBLE_INVENTORY_DIR
export OA_ANSIBLE_ROLES_DIR
export OA_ANSIBLE_TASKS_DIR
export OA_ANSIBLE_GROUP_VARS_DIR
export OA_ANSIBLE_VAULT_PASSWORD_FILE
export OA_ANSIBLE_LOG_DIR
export OA_ANSIBLE_LOG_FILE

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

# Function to select a target host from an inventory
# Returns 0 on success, 1 on failure
# Sets global variables: TARGET_INVENTORY_PATH, TARGET_HOST_ALIAS
# If extract_connection_details is true, also sets: TARGET_CONNECT_HOST, TARGET_CONNECT_USER, TARGET_CONNECT_PORT
select_target_host() {
  local extract_connection_details=${1:-false}
  
  log_debug "Starting host selection process."
  local inventories=("staging" "production")
  local selected_inventory_name
  local selected_inventory_path
  local host_aliases=() # Initialize as an empty array
  local selected_host_alias

  # Select inventory
  log_info "Please select an inventory environment:"
  select inv_choice in "${inventories[@]}"; do
    if [[ -n "$inv_choice" ]]; then
      selected_inventory_name="$inv_choice"
      selected_inventory_path="$OA_ANSIBLE_INVENTORY_DIR/$selected_inventory_name/hosts.yml"
      if [ ! -f "$selected_inventory_path" ]; then
        log_error "Inventory file not found: $selected_inventory_path"
        return 1
      fi
      log_info "Selected inventory: $selected_inventory_name"
      break
    else
      log_warn "Invalid selection. Please try again."
    fi
  done

  # List hosts from selected inventory
  log_debug "Fetching hosts from $selected_inventory_path"
  # Portable way to read lines into an array
  while IFS= read -r line; do
    host_aliases+=("$line")
  done < <(yq e '.all.children.macos.hosts | keys | .[]' "$selected_inventory_path" 2>/dev/null)

  if [ ${#host_aliases[@]} -eq 0 ]; then
    log_error "No hosts found in the '.all.children.macos.hosts' group of $selected_inventory_path, or error parsing inventory."
    return 1
  fi

  log_info "Please select a target host from '$selected_inventory_name':"
  select host_choice in "${host_aliases[@]}"; do
    if [[ -n "$host_choice" ]]; then
      selected_host_alias="$host_choice"
      log_info "Selected host: $selected_host_alias"
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
    # Get ansible_host and ansible_user for the selected host alias
    TARGET_CONNECT_HOST=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_host" "$selected_inventory_path")
    TARGET_CONNECT_USER=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_user" "$selected_inventory_path")
    # Query for ansible_port, default to 22 if not found
    TARGET_CONNECT_PORT=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_port // 22" "$selected_inventory_path")

    if [ -z "$TARGET_CONNECT_HOST" ] || [ "$TARGET_CONNECT_HOST" == "null" ]; then
      log_error "Could not determine 'ansible_host' for '$selected_host_alias' in $selected_inventory_path."
      return 1
    fi
    if [ -z "$TARGET_CONNECT_USER" ] || [ "$TARGET_CONNECT_USER" == "null" ]; then
      log_error "Could not determine 'ansible_user' for '$selected_host_alias' in $selected_inventory_path."
      return 1
    fi

    log_debug "Target connection host: $TARGET_CONNECT_HOST"
    log_debug "Target connection user: $TARGET_CONNECT_USER"
    log_debug "Target connection port: $TARGET_CONNECT_PORT"
  fi
  
  return 0
}

# Function to list all available hosts from all inventories
list_all_hosts() {
  local inventories=("staging" "production")
  
  echo "Available hosts:"
  echo "---------------"
  
  for inv in "${inventories[@]}"; do
    local inventory_path="$OA_ANSIBLE_INVENTORY_DIR/$inv/hosts.yml"
    if [ ! -f "$inventory_path" ]; then
      log_warn "Inventory file not found: $inventory_path"
      continue
    fi
    
    echo "[$inv]"
    yq e '.all.children.macos.hosts | keys | .[]' "$inventory_path" 2>/dev/null | while read -r host; do
      local host_ip=$(yq e ".all.children.macos.hosts.\"$host\".ansible_host" "$inventory_path")
      echo "  $host ($host_ip)"
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
  local inventories
  
  if [ -n "$specified_inventory" ]; then
    inventories=("$specified_inventory")
  else
    inventories=("staging" "production")
  fi
  
  local found_hosts=()
  local found_inventories=()
  
  for inv in "${inventories[@]}"; do
    local inventory_path="$OA_ANSIBLE_INVENTORY_DIR/$inv/hosts.yml"
    if [ ! -f "$inventory_path" ]; then
      log_warn "Inventory file not found: $inventory_path"
      continue
    fi
    
    while IFS= read -r host; do
      if [[ "$host" == *"$search_term"* ]]; then
        found_hosts+=("$host")
        found_inventories+=("$inv")
      fi
    done < <(yq e '.all.children.macos.hosts | keys | .[]' "$inventory_path" 2>/dev/null)
  done
  
  if [ ${#found_hosts[@]} -eq 0 ]; then
    log_error "No hosts matching '$search_term' found in any inventory."
    return 1
  elif [ ${#found_hosts[@]} -gt 1 ]; then
    log_warn "Multiple hosts match '$search_term':"
    for i in "${!found_hosts[@]}"; do
      echo "$((i+1)). ${found_hosts[$i]} (${found_inventories[$i]})"
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
  else
    selected_host_alias="${found_hosts[0]}"
    selected_inventory_name="${found_inventories[0]}"
  fi
  
  selected_inventory_path="$OA_ANSIBLE_INVENTORY_DIR/$selected_inventory_name/hosts.yml"
  
  # Set the global variables
  TARGET_HOST_ALIAS="$selected_host_alias"
  TARGET_INVENTORY_PATH="$selected_inventory_path"
  
  # Optionally extract connection details
  if [ "$extract_connection_details" = true ]; then
    # Get connection details
    TARGET_CONNECT_HOST=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_host" "$selected_inventory_path")
    TARGET_CONNECT_USER=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_user" "$selected_inventory_path")
    TARGET_CONNECT_PORT=$(yq e ".all.children.macos.hosts.\"$selected_host_alias\".ansible_port // 22" "$selected_inventory_path")
    
    if [ -z "$TARGET_CONNECT_HOST" ] || [ "$TARGET_CONNECT_HOST" == "null" ]; then
      log_error "Could not determine 'ansible_host' for '$selected_host_alias' in $selected_inventory_path."
      return 1
    fi
    if [ -z "$TARGET_CONNECT_USER" ] || [ "$TARGET_CONNECT_USER" == "null" ]; then
      log_error "Could not determine 'ansible_user' for '$selected_host_alias' in $selected_inventory_path."
      return 1
    fi
    
    log_debug "Target connection host: $TARGET_CONNECT_HOST"
    log_debug "Target connection user: $TARGET_CONNECT_USER"
    log_debug "Target connection port: $TARGET_CONNECT_PORT"
  fi
  
  log_info "Found host: $selected_host_alias in $selected_inventory_name"
  return 0
}

# Example of setting a different log level for a specific script:
# At the top of your script, after sourcing helpers.sh:
# SCRIPT_LOG_LEVEL=$_LOG_LEVEL_DEBUG # To see debug messages for this script
