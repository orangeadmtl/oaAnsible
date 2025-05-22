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
  if ! command -v ansible-playbook &>/dev/null; then
    log_error "ansible-playbook command not found. Please install Ansible first."
    log_error "You can install it with: pip install ansible"
    exit 1
  fi
}

# Function to check if vault password file exists
check_vault_password_file() {
  if [ ! -f "$OA_ANSIBLE_VAULT_PASSWORD_FILE" ]; then
    log_error "Ansible vault password file not found at $OA_ANSIBLE_VAULT_PASSWORD_FILE"
    log_error "Please create it and add your vault password."
    exit 1
  fi
}

# Example of setting a different log level for a specific script:
# At the top of your script, after sourcing helpers.sh:
# SCRIPT_LOG_LEVEL=$_LOG_LEVEL_DEBUG # To see debug messages for this script
