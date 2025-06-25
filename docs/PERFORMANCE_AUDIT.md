# Performance Optimization Audit Checklist

_Spectra Deployment - Make it run first, then make it run better_

## Overview

This checklist helps identify performance bottlenecks and optimization opportunities in the OrangeAd Spectra deployment pipeline and runtime services.

## 🚀 Deployment Pipeline Performance

### Role Execution Order

- [ ] **Sequential vs Parallel Role Execution**

  - Check `playbooks/universal.yml` for role dependencies
  - Identify roles that can run in parallel (e.g., `python` + `node` setup)
  - Consider `strategy: linear` vs `strategy: free` for faster execution

- [ ] **Service Restart Coordination**

  - Review `tasks/restart_services.yml` for unnecessary service restarts
  - Check if services are restarted multiple times during deployment
  - Batch service operations where possible

- [ ] **Network Operations**
  - Minimize repeated Tailscale connectivity checks
  - Cache DNS resolution results
  - Reduce redundant network calls in roles

### Resource-Intensive Operations

- [ ] **Python Environment Setup**

  - `pyenv` installation and Python compilation time
  - Virtual environment creation with `uv` - check for redundant deps
  - Large package downloads (PyTorch, OpenCV, Ultralytics models)

- [ ] **Package Manager Operations**

  - Homebrew package installation parallelization
  - `brew` cache optimization and cleanup
  - Node.js/npm package installation efficiency

- [ ] **File Operations**
  - Large file transfers (AI models, binaries)
  - Recursive directory operations
  - Symlink creation vs copying

## 🔧 Service Runtime Performance

### Resource Utilization

- [ ] **Memory Usage**

  - AI model loading in `oaTracker` (check model size and RAM usage)
  - Python virtual environment memory footprint
  - Concurrent service memory allocation

- [ ] **CPU Performance**

  - AI inference optimization in tracker
  - Video processing pipeline efficiency
  - Background service CPU usage (API polling intervals)

- [ ] **Disk I/O**
  - Log file rotation and cleanup frequency
  - Temporary file management
  - Database/cache write patterns

### Service Dependencies

- [ ] **Startup Order**

  - Service interdependencies (API → Tracker → Player)
  - LaunchAgent `RunAtLoad` vs on-demand loading
  - Health check intervals and timeouts

- [ ] **Network Services**
  - API request/response optimization
  - Internal service communication (localhost calls)
  - External dependencies (Tailscale, DNS)

## 📊 Monitoring & Observability

### Health Monitoring

- [ ] **Check Intervals**

  - `health_monitoring.yml` check frequencies
  - Service status polling rates
  - Resource monitoring overhead

- [ ] **Logging Performance**
  - Log level optimization (DEBUG vs INFO in production)
  - Log rotation frequency
  - Centralized vs distributed logging impact

## 🔍 Specific File Analysis

### Critical Performance Files to Review

1. **`playbooks/universal.yml`**

   - Role execution strategy
   - Task parallelization opportunities
   - Conditional execution optimization

2. **`roles/macos/*/tasks/main.yml`**

   - Task idempotency checks
   - Redundant system calls
   - File operation optimization

3. **Service Health Monitoring Files:**

   - `roles/macos/player/tasks/health_monitoring.yml`
   - `roles/macos/api/tasks/main.yml`
   - Check intervals and resource usage

4. **Package Management:**
   - `roles/macos/python/tasks/main.yml`
   - `roles/macos/node/tasks/main.yml`
   - Dependency resolution optimization

## 🎯 Optimization Priorities

### High Impact (Do First)

1. **Reduce AI Model Download Time**

   - Pre-built containers with models
   - Model caching strategies
   - Smaller/quantized models for development

2. **Optimize Python Environment Setup**

   - Pre-compiled Python versions
   - Shared virtual environments
   - Dependency caching

3. **Service Restart Batching**
   - Consolidate service operations
   - Reduce unnecessary restarts
   - Parallel service management

### Medium Impact

1. **Network Call Optimization**

   - Reduce redundant connectivity checks
   - Cache API responses where appropriate
   - Connection pooling for internal APIs

2. **Log Management**
   - Optimize log levels for production
   - Implement efficient log rotation
   - Reduce logging overhead

### Low Impact (Optimize Later)

1. **UI/Display Optimizations**
   - Player display performance
   - API response formatting
   - Debug output optimization

## 🛠️ Performance Testing Commands

### Deployment Performance

```bash
# Time full deployment
time ./scripts/run spectra-preprod

# Profile specific components
./scripts/run spectra-preprod -t player --verbose

# Validate before optimization
./scripts/check spectra-preprod
```

### Runtime Performance

```bash
# Check service resource usage
ssh spectra-ca-001 "top -l 1 -pid \$(pgrep -f 'orangead')"

# Monitor service startup times
ssh spectra-ca-001 "tail -f ~/orangead/*/logs/*.log"

# Check LaunchAgent performance
ssh spectra-ca-001 "launchctl list | grep orangead"
```

### System Resource Monitoring

```bash
# Disk usage analysis
ssh spectra-ca-001 "du -sh ~/orangead/*"

# Memory usage by service
ssh spectra-ca-001 "ps aux | grep orangead"

# Network connection monitoring
ssh spectra-ca-001 "lsof -i -P | grep orangead"
```

## 📈 Performance Metrics to Track

### Deployment Metrics

- [ ] Total deployment time (baseline: current duration)
- [ ] Role execution time breakdown
- [ ] Network transfer time for large assets
- [ ] Service startup time post-deployment

### Runtime Metrics

- [ ] API response times (health endpoints)
- [ ] Memory usage per service
- [ ] CPU utilization during AI processing
- [ ] Disk I/O for logging and caching

### Success Criteria

- [ ] Deployment time reduced by 25%
- [ ] Service startup time < 30 seconds
- [ ] Memory usage optimized for Mac Mini specs
- [ ] Zero failed deployments due to resource constraints

## 🔄 Continuous Optimization

### Regular Review Schedule

- [ ] **Weekly**: Review deployment logs for bottlenecks
- [ ] **Monthly**: Analyze service performance metrics
- [ ] **Quarterly**: Full performance audit and optimization

### Automation Opportunities

- [ ] Automated performance regression testing
- [ ] Deployment time monitoring and alerting
- [ ] Resource usage trending and optimization recommendations

---

_This checklist should be updated as optimizations are implemented and new performance insights are discovered._
