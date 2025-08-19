#!/bin/bash

# Storage Server Health Check Script
# Usage: ./scripts/check-storage-server.sh [hostname_or_ip]

set -e

# Configuration
STORAGE_HOST="${1:-100.67.244.94}"
SSH_KEY="$HOME/.ssh/kampus-rig_ed25519"
SSH_USER="kai"
STORAGE_PATH="/data/orangead"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test SSH connectivity
test_connectivity() {
    log_info "Testing SSH connectivity to $STORAGE_HOST..."
    if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$SSH_USER@$STORAGE_HOST" "echo 'Connected successfully'" >/dev/null 2>&1; then
        log_success "SSH connectivity: OK"
        return 0
    else
        log_error "SSH connectivity: FAILED"
        return 1
    fi
}

# Check storage directories
check_directories() {
    log_info "Checking storage directories..."
    
    local dirs_output
    dirs_output=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "ls -la $STORAGE_PATH/" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        log_success "Storage directories accessible"
        echo "$dirs_output"
        
        # Check specific directories
        local required_dirs=("camguard" "camguard/recordings" "camguard/logs" "temp" "backups" "scripts")
        for dir in "${required_dirs[@]}"; do
            if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "test -d $STORAGE_PATH/$dir" 2>/dev/null; then
                log_success "Directory exists: $STORAGE_PATH/$dir"
            else
                log_error "Directory missing: $STORAGE_PATH/$dir"
            fi
        done
    else
        log_error "Cannot access storage directories"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log_info "Checking disk space..."
    
    local disk_info
    disk_info=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "df -h $STORAGE_PATH" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        echo "$disk_info"
        
        # Extract usage percentage
        local usage_percent
        usage_percent=$(echo "$disk_info" | tail -1 | awk '{print $5}' | sed 's/%//')
        
        if [[ $usage_percent -lt 80 ]]; then
            log_success "Disk usage: ${usage_percent}% (OK)"
        elif [[ $usage_percent -lt 90 ]]; then
            log_warning "Disk usage: ${usage_percent}% (Warning)"
        else
            log_error "Disk usage: ${usage_percent}% (Critical)"
        fi
    else
        log_error "Cannot check disk space"
        return 1
    fi
}

# Check services
check_services() {
    log_info "Checking system services..."
    
    local services=("ssh" "fail2ban" "ufw")
    for service in "${services[@]}"; do
        if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "systemctl is-active $service" >/dev/null 2>&1; then
            log_success "Service $service: ACTIVE"
        else
            log_error "Service $service: INACTIVE"
        fi
    done
}

# Check firewall rules
check_firewall() {
    log_info "Checking firewall configuration..."
    
    local ufw_status
    ufw_status=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "sudo ufw status" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        echo "$ufw_status"
        
        # Check for required rules
        if echo "$ufw_status" | grep -q "100.64.0.0/10"; then
            log_success "Tailscale network access: CONFIGURED"
        else
            log_warning "Tailscale network access: NOT CONFIGURED"
        fi
        
        if echo "$ufw_status" | grep -q "22/tcp"; then
            log_success "SSH access: CONFIGURED"
        else
            log_error "SSH access: NOT CONFIGURED"
        fi
    else
        log_error "Cannot check firewall status"
    fi
}

# Test file transfer
test_file_transfer() {
    log_info "Testing file transfer functionality..."
    
    local test_file="/tmp/storage_test_$(date +%s).txt"
    local remote_path="$STORAGE_PATH/camguard/recordings/"
    
    # Create test file
    echo "Storage test $(date)" > "$test_file"
    
    # Transfer file
    if scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$test_file" "$SSH_USER@$STORAGE_HOST:$remote_path" >/dev/null 2>&1; then
        log_success "File transfer: OK"
        
        # Verify file exists and cleanup
        if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "test -f $remote_path$(basename $test_file)" 2>/dev/null; then
            log_success "File verification: OK"
            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "rm -f $remote_path$(basename $test_file)" 2>/dev/null
        else
            log_error "File verification: FAILED"
        fi
    else
        log_error "File transfer: FAILED"
    fi
    
    # Cleanup local test file
    rm -f "$test_file"
}

# Check monitoring scripts
check_monitoring() {
    log_info "Checking monitoring scripts..."
    
    # Check if scripts exist
    local scripts=("storage_monitor.sh" "storage_cleanup.sh")
    for script in "${scripts[@]}"; do
        if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "test -f $STORAGE_PATH/scripts/$script" 2>/dev/null; then
            log_success "Script exists: $script"
        else
            log_error "Script missing: $script"
        fi
    done
    
    # Check cron jobs
    local cron_output
    cron_output=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "crontab -l | grep storage" 2>/dev/null)
    
    if [[ -n "$cron_output" ]]; then
        log_success "Cron jobs configured:"
        echo "$cron_output"
    else
        log_warning "No storage-related cron jobs found"
    fi
    
    # Test monitoring script
    log_info "Testing monitoring script execution..."
    if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$STORAGE_HOST" "$STORAGE_PATH/scripts/storage_monitor.sh" >/dev/null 2>&1; then
        log_success "Monitoring script: EXECUTABLE"
    else
        log_error "Monitoring script: FAILED TO EXECUTE"
    fi
}

# Main execution
main() {
    echo "=================================="
    echo "Storage Server Health Check"
    echo "Host: $STORAGE_HOST"
    echo "Time: $(date)"
    echo "=================================="
    echo
    
    local exit_code=0
    
    # Run all checks
    test_connectivity || exit_code=1
    echo
    
    check_directories || exit_code=1
    echo
    
    check_disk_space || exit_code=1
    echo
    
    check_services || exit_code=1
    echo
    
    check_firewall || exit_code=1
    echo
    
    test_file_transfer || exit_code=1
    echo
    
    check_monitoring || exit_code=1
    echo
    
    # Summary
    echo "=================================="
    if [[ $exit_code -eq 0 ]]; then
        log_success "Storage server health check: ALL TESTS PASSED"
    else
        log_error "Storage server health check: SOME TESTS FAILED"
    fi
    echo "=================================="
    
    exit $exit_code
}

# Run main function
main "$@"
