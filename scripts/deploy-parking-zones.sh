#!/bin/bash
# Deploy parking zone configuration to specific machines
# Usage: ./scripts/deploy-parking-zones.sh yhu-preprod

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_usage() {
    cat << EOF
Deploy Parking Zone Configuration

Usage: $0 <environment>

Available environments:
  yhu-preprod    - Deploy to f1-ca-014 (yhu preprod machine)

This script:
  1. Deploys parking zone configuration via Ansible
  2. Restarts the parking monitor service
  3. Verifies the deployment

Examples:
  $0 yhu-preprod

EOF
}

deploy_yhu_preprod() {
    echo "=== Deploying Parking Zones to YHU Preprod ==="
    echo "Target: f1-ca-014"
    echo
    
    cd "$PROJECT_ROOT"
    
    # Deploy via Ansible
    echo "🔄 Running Ansible deployment..."
    ./scripts/run projects/yhu/preprod -t parking-monitor --extra-vars "parking_monitor_config_template=yhu-preprod-config.yaml"
    
    # Verify deployment
    echo "🔍 Verifying deployment..."
    if curl -sf http://f1-ca-014:9091/health > /dev/null 2>&1; then
        echo "✅ Parking monitor is running successfully!"
        echo
        echo "🎯 Access points:"
        echo "  Dashboard: ssh admin@f1-ca-014 -L 9091:localhost:9091"
        echo "  Then open: http://localhost:9091/dashboard"
        echo "  API Stats: curl http://f1-ca-014:9091/api/stats"
    else
        echo "❌ Service verification failed"
        echo "Check logs: ssh admin@f1-ca-014 'cd ~/orangead/parking-monitor && ./scripts/logs.sh'"
        exit 1
    fi
}

# Main execution
main() {
    if [[ $# -ne 1 ]]; then
        show_usage
        exit 1
    fi
    
    case "$1" in
        yhu-preprod)
            deploy_yhu_preprod
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "❌ Unknown environment: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"