#!/bin/bash
# Ethernet Optimization Validation Script
# Verifies that ethernet optimizations have been properly applied

set -euo pipefail

echo "🔍 Validating Ethernet Optimization Configuration"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Validation counters
PASSED=0
FAILED=0
WARNINGS=0

# 1. Check for Realtek controllers
echo
echo "1. Hardware Detection"
echo "───────────────────"
if lspci | grep -qi "realtek.*ethernet"; then
    CONTROLLER=$(lspci | grep -i "realtek.*ethernet")
    check_pass "Realtek ethernet controller detected: $CONTROLLER"
    PASSED=$((PASSED + 1))
    HAS_REALTEK=true
else
    check_warn "No Realtek ethernet controller detected - optimizations may not be needed"
    WARNINGS=$((WARNINGS + 1))
    HAS_REALTEK=false
fi

# 2. Check driver configuration
echo
echo "2. Driver Configuration"
echo "─────────────────────"
if [ -f /etc/modprobe.d/r8169-orangead.conf ]; then
    check_pass "Driver configuration file exists: /etc/modprobe.d/r8169-orangead.conf"
    PASSED=$((PASSED + 1))
    
    if grep -q "use_dac=1" /etc/modprobe.d/r8169-orangead.conf; then
        check_pass "use_dac=1 option configured"
        PASSED=$((PASSED + 1))
    else
        check_fail "use_dac=1 option missing"
        FAILED=$((FAILED + 1))
    fi
    
    if grep -q "eee_enable=0" /etc/modprobe.d/r8169-orangead.conf; then
        check_pass "eee_enable=0 option configured (Energy Efficient Ethernet disabled)"
        PASSED=$((PASSED + 1))
    else
        check_fail "eee_enable=0 option missing"
        FAILED=$((FAILED + 1))
    fi
else
    if [ "$HAS_REALTEK" = true ]; then
        check_fail "Driver configuration file missing: /etc/modprobe.d/r8169-orangead.conf"
        FAILED=$((FAILED + 1))
    else
        check_warn "Driver configuration not needed (no Realtek controller)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 3. Check power management service
echo
echo "3. Power Management"
echo "─────────────────"
if systemctl is-enabled ethernet-pm-disable >/dev/null 2>&1; then
    check_pass "ethernet-pm-disable service is enabled"
    PASSED=$((PASSED + 1))
    
    if systemctl is-active ethernet-pm-disable >/dev/null 2>&1; then
        check_pass "ethernet-pm-disable service is active"
        PASSED=$((PASSED + 1))
    else
        check_fail "ethernet-pm-disable service is not active"
        FAILED=$((FAILED + 1))
    fi
else
    check_fail "ethernet-pm-disable service is not enabled"
    FAILED=$((FAILED + 1))
fi

# 4. Check ethernet interfaces
echo
echo "4. Ethernet Interfaces"
echo "────────────────────"
ETH_INTERFACES=$(ls /sys/class/net/ | grep -E '^en' | head -5)
if [ -n "$ETH_INTERFACES" ]; then
    for iface in $ETH_INTERFACES; do
        if [ -f "/sys/class/net/$iface/operstate" ]; then
            STATE=$(cat "/sys/class/net/$iface/operstate")
            if [ "$STATE" = "up" ]; then
                check_pass "Interface $iface is up"
                PASSED=$((PASSED + 1))
                
                # Check speed if ethtool is available
                if command -v ethtool >/dev/null 2>&1; then
                    SPEED=$(ethtool "$iface" 2>/dev/null | grep "Speed:" | awk '{print $2}' || echo "unknown")
                    if [ "$SPEED" = "1000Mb/s" ]; then
                        check_pass "Interface $iface running at Gigabit speed: $SPEED"
                        PASSED=$((PASSED + 1))
                    elif [ "$SPEED" = "100Mb/s" ]; then
                        check_warn "Interface $iface running at 100Mbps (check cable/switch)"
                        WARNINGS=$((WARNINGS + 1))
                    else
                        check_warn "Interface $iface speed: $SPEED"
                        WARNINGS=$((WARNINGS + 1))
                    fi
                    
                    # Check Wake-on-LAN
                    WOL=$(ethtool "$iface" 2>/dev/null | grep "Wake-on:" | awk '{print $2}' || echo "unknown")
                    if [ "$WOL" = "d" ]; then
                        check_pass "Wake-on-LAN disabled for $iface"
                        PASSED=$((PASSED + 1))
                    else
                        check_warn "Wake-on-LAN status for $iface: $WOL"
                        WARNINGS=$((WARNINGS + 1))
                    fi
                fi
            else
                check_warn "Interface $iface is $STATE"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    done
else
    check_fail "No ethernet interfaces found"
    FAILED=$((FAILED + 1))
fi

# 5. Check monitoring setup
echo
echo "5. Monitoring Configuration"
echo "─────────────────────────"
MONITOR_DIRS=(
    "/home/*/orangead/network-monitor"
    "/opt/orangead/network-monitor"
    "/var/lib/orangead/network-monitor"
)

MONITOR_FOUND=false
for dir_pattern in "${MONITOR_DIRS[@]}"; do
    for dir in $dir_pattern; do
        if [ -d "$dir" ]; then
            check_pass "Monitoring directory found: $dir"
            PASSED=$((PASSED + 1))
            MONITOR_FOUND=true
            
            if [ -x "$dir/monitor.sh" ]; then
                check_pass "Monitoring script exists and is executable"
                PASSED=$((PASSED + 1))
            else
                check_fail "Monitoring script missing or not executable: $dir/monitor.sh"
                FAILED=$((FAILED + 1))
            fi
            
            if [ -f "$dir/network.log" ]; then
                LOG_LINES=$(wc -l < "$dir/network.log" 2>/dev/null || echo "0")
                if [ "$LOG_LINES" -gt 0 ]; then
                    check_pass "Monitoring log has data ($LOG_LINES lines)"
                    PASSED=$((PASSED + 1))
                else
                    check_warn "Monitoring log is empty"
                    WARNINGS=$((WARNINGS + 1))
                fi
            else
                check_warn "Monitoring log not yet created: $dir/network.log"
                WARNINGS=$((WARNINGS + 1))
            fi
            break
        fi
    done
    if [ "$MONITOR_FOUND" = true ]; then
        break
    fi
done

if [ "$MONITOR_FOUND" = false ]; then
    check_fail "No monitoring directory found"
    FAILED=$((FAILED + 1))
fi

# 6. Check cron job
echo
echo "6. Cron Job Configuration"
echo "───────────────────────"
if crontab -l 2>/dev/null | grep -q "network-monitor\|OrangeAd.*Monitor"; then
    check_pass "Network monitoring cron job configured"
    PASSED=$((PASSED + 1))
else
    check_fail "Network monitoring cron job not found"
    FAILED=$((FAILED + 1))
fi

# Summary
echo
echo "Validation Summary"
echo "===================="
echo -e "[OK] Passed: ${GREEN}$PASSED${NC}"
echo -e "[FAIL] Failed: ${RED}$FAILED${NC}"
echo -e "[WARNING] Warnings: ${YELLOW}$WARNINGS${NC}"

if [ $FAILED -eq 0 ]; then
    echo
    echo -e "${GREEN}[OK] Ethernet optimization validation PASSED!${NC}"
    echo "All critical components are properly configured."
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Note: There are $WARNINGS warnings that may need attention.${NC}"
    fi
    exit 0
else
    echo
    echo -e "${RED}[FAIL] Ethernet optimization validation FAILED!${NC}"
    echo "Please review the failed checks and re-run the optimization playbook."
    exit 1
fi