# TODO - oaAnsible: Project-Based Multi-Platform Orchestration System

**Overall Goal:** Complete the transformation of oaAnsible into a flexible, project-based orchestration system with streamlined tooling, video player
capabilities, and modern inventory management.

**Key:**

- `[ ]` ToDo
- `[P]` Priority Task
- `[✓]` Complete
- `[S]` Structure/Architecture Task
- `[F]` Feature Task
- `[T]` Testing Task
- `[D]` Documentation Task

---

## Phase 1: Core Infrastructure Modernization - COMPLETE ✅

### 1.1. Project-Based Inventory System - COMPLETE ✅

- `[S]` `[P]` `[✓]` **New Inventory Structure:**
  - `[✓]` Created `inventory/f1-staging.yml` for F1 project staging environment
  - `[✓]` Created `inventory/f1-preprod.yml` for F1 project pre-production environment
  - `[✓]` Created `inventory/f1-prod.yml` for F1 project production environment
  - `[✓]` Added project-specific configuration variables (project_name, video_player settings)
  - `[✓]` Maintained backward compatibility with existing environment structure

### 1.2. Enhanced Helper System - COMPLETE ✅

- `[S]` `[P]` `[✓]` **Flexible Inventory Management:**
  - `[✓]` Added `discover_inventories()` function for dynamic inventory detection
  - `[✓]` Added `get_inventory_path()` function supporting both old and new formats
  - `[✓]` Updated `select_target_host()` to work with any inventory structure
  - `[✓]` Enhanced `find_host_by_name()` with multi-group and multi-platform support
  - `[✓]` Updated `list_all_hosts()` and `run_environment_playbook()` for new structure

### 1.3. Streamlined Script System - COMPLETE ✅

- `[S]` `[P]` `[✓]` **Essential Scripts Only:**
  - `[✓]` Enhanced `reboot` script with flexible inventory support and production safety
  - `[✓]` Maintained `genSSH` script with improved multi-group support
  - `[✓]` Kept `format` script for code quality and linting
  - `[✓]` Created `sync` script for inventory management and validation
  - `[✓]` Created unified `run` script replacing multiple `run-*` scripts

### 1.4. Documentation Cleanup - COMPLETE ✅

- `[D]` `[✓]` **Streamlined Documentation:**
  - `[✓]` Evaluated all documentation files in `docs/` directory
  - `[✓]` Kept essential docs: SCRIPT_USAGE.md, QUICK_REFERENCE.md, WIFI_SETUP.md, components.md, server-api.md, README.md
  - `[✓]` Removed redundant/missing documentation files
  - `[✓]` Maintained documentation quality and usefulness

---

## Phase 2: Video Player Component Implementation - COMPLETE ✅

### 2.1. Video Player Role Development - COMPLETE ✅

- `[F]` `[P]` `[✓]` **Adaptive Video Player:**
  - `[✓]` Created `roles/macos/player` role structure  
  - `[✓]` Implemented adaptive video playback with single-screen fallback and dual-screen optimization
  - `[✓]` Added configurable video sources and dynamic display management
  - `[✓]` Created health monitoring and automatic restart capabilities
  - `[✓]` Integrated with LaunchAgent for service management

### 2.2. Video Player Configuration - COMPLETE ✅

- `[F]` `[✓]` **Advanced Configuration Options:**
  - `[✓]` Added support for different video files per screen
  - `[✓]` Implemented volume, loop mode, and display positioning controls
  - `[✓]` Created sample video generation for testing
  - `[✓]` Added backup and video file management capabilities
  - `[✓]` Configured F1 project-specific video settings in inventories

### 2.3. Service Integration - COMPLETE ✅

- `[F]` `[✓]` **Robust Service Management:**
  - `[✓]` Created comprehensive LaunchAgent configuration
  - `[✓]` Implemented health monitoring with automatic restart
  - `[✓]` Added logging and verification systems
  - `[✓]` Created handlers for service restart and management
  - `[✓]` Integrated with existing oaAnsible component framework

---

## Phase 3: Testing & Validation - PLANNED 🧪

### 3.1. Inventory Migration Testing

- `[T]` `[ ]` **Migration Validation:**
  - `[T]` `[ ]` Test migration from old inventory structure to new project-based format
  - `[T]` `[ ]` Validate `sync migrate` command functionality
  - `[T]` `[ ]` Test backward compatibility with existing scripts
  - `[T]` `[ ]` Verify all inventory validation features work correctly

### 3.2. Video Player Testing

- `[T]` `[ ]` **Component Validation:**
  - `[T]` `[ ]` Test video player deployment on F1 project devices
  - `[T]` `[ ]` Validate adaptive display functionality on single and multi-monitor setups
  - `[T]` `[ ]` Test health monitoring and automatic restart features
  - `[T]` `[ ]` Verify video file management and backup systems

### 3.3. Script System Testing

- `[T]` `[ ]` **Unified Script Validation:**
  - `[T]` `[ ]` Test new `run` script with various inventory and component combinations
  - `[T]` `[ ]` Validate `sync` script inventory management features
  - `[T]` `[ ]` Test enhanced `reboot` script with project-based inventories
  - `[T]` `[ ]` Verify `genSSH` functionality across all inventory formats

---

## Phase 4: Enhanced Features & Integration - PLANNED 🚀

### 4.1. Component Framework Integration

- `[F]` `[ ]` **Video Player Component:**
  - `[F]` `[P]` `[ ]` Add video-player component to component framework system
  - `[F]` `[ ]` Update component compatibility matrix for video player requirements
  - `[F]` `[ ]` Add video player to component-specific playbooks
  - `[F]` `[ ]` Create component health validation for video player

### 4.2. Advanced Inventory Features

- `[F]` `[ ]` **Multi-Project Support:**
  - `[F]` `[ ]` Add support for additional projects beyond F1 (e.g., spectra-staging.yml)
  - `[F]` `[ ]` Create project templates for quick new project setup
  - `[F]` `[ ]` Add project-specific variable inheritance and validation
  - `[F]` `[ ]` Implement project-based deployment workflows

### 4.3. Enhanced Video Player Features

- `[F]` `[ ]` **Advanced Video Management:**
  - `[F]` `[ ]` Add video content synchronization from remote sources
  - `[F]` `[ ]` Implement video playlist management for multiple content rotation
  - `[F]` `[ ]` Add video quality adaptation based on display capabilities
  - `[F]` `[ ]` Create video content validation and integrity checking

### 4.4. Monitoring & Analytics

- `[F]` `[ ]` **System Monitoring:**
  - `[F]` `[ ]` Add video player metrics collection for oaDashboard integration
  - `[F]` `[ ]` Create video playback health status reporting
  - `[F]` `[ ]` Implement display status monitoring and alerting
  - `[F]` `[ ]` Add performance metrics for video playback optimization

---

## Phase 5: Production Hardening & Optimization - PLANNED 🛡️

### 5.1. Security Enhancements

- `[S]` `[ ]` **Security Hardening:**
  - `[S]` `[ ]` Add video player security controls and sandboxing
  - `[S]` `[ ]` Implement secure video content delivery and validation
  - `[S]` `[ ]` Add inventory access controls and permissions
  - `[S]` `[ ]` Create security auditing for video player deployments

### 5.2. Performance Optimization

- `[S]` `[ ]` **Performance Tuning:**
  - `[S]` `[ ]` Optimize video player resource usage and GPU acceleration
  - `[S]` `[ ]` Add deployment performance monitoring and optimization
  - `[S]` `[ ]` Implement smart caching for video content and configurations
  - `[S]` `[ ]` Create performance benchmarking and regression testing

### 5.3. Reliability & Resilience

- `[S]` `[ ]` **High Availability:**
  - `[S]` `[✓]` Add graceful degradation for single-screen fallback (adaptive display mode)
  - `[S]` `[ ]` Implement video content failover and redundancy
  - `[S]` `[ ]` Create disaster recovery procedures for video player systems
  - `[S]` `[ ]` Add comprehensive logging and debugging capabilities

---

## Phase 6: Documentation & User Experience - PLANNED 📚

### 6.1. Comprehensive Documentation

- `[D]` `[ ]` **User Guides:**
  - `[D]` `[ ]` Create video player deployment and management guide
  - `[D]` `[ ]` Document project-based inventory management workflows
  - `[D]` `[ ]` Add troubleshooting guide for video player issues
  - `[D]` `[ ]` Create best practices guide for multi-project deployments

### 6.2. Developer Documentation

- `[D]` `[ ]` **Technical Documentation:**
  - `[D]` `[ ]` Document video player role architecture and customization
  - `[D]` `[ ]` Create component integration guide for new features
  - `[D]` `[ ]` Add API documentation for video player management
  - `[D]` `[ ]` Document inventory migration and management procedures

### 6.3. Training Materials

- `[D]` `[ ]` **Learning Resources:**
  - `[D]` `[ ]` Create video tutorials for common deployment scenarios
  - `[D]` `[ ]` Add interactive examples and walkthroughs
  - `[D]` `[ ]` Create quick-start guides for new projects
  - `[D]` `[ ]` Develop troubleshooting decision trees

---

## Current Status: Phase 2 Complete 🎯

**✅ Phase 1 Complete**: Core infrastructure modernization with project-based inventories, enhanced helpers, and streamlined scripts **✅ Phase 2 Complete**:
Video player component implementation with dual-screen support, health monitoring, and F1 project integration **🔄 Phase 3 Ready**: Testing and validation of
new systems **📋 Phases 4-6**: Detailed roadmap for enhanced features, production hardening, and documentation

### Phase 2 Achievements

1. **✅ Project-Based Inventories**: Created F1 project inventories (staging, preprod, prod) with video player configuration
2. **✅ Enhanced Helper System**: Dynamic inventory discovery, flexible path resolution, multi-platform host management
3. **✅ Streamlined Scripts**: Essential scripts only (run, reboot, genSSH, format, sync) with unified functionality
4. **✅ Video Player Role**: Complete dual-screen video player with health monitoring and service management
5. **✅ Documentation Cleanup**: Maintained essential documentation, removed redundant files

### Immediate Next Actions

1. **Start Phase 3.1**: Test inventory migration and validation features
2. **Video Player Testing**: Deploy and validate video player on F1 project devices
3. **Script Integration**: Test unified `run` script with video player component
4. **Component Framework**: Integrate video player into existing component system

### Key Features Delivered

- **Flexible Inventory Management**: Support for both old and new inventory structures
- **Project-Based Configuration**: F1 project with video player settings and environment-specific controls
- **Adaptive Video Player**: Complete MPV-based video player with dynamic display detection and health monitoring
- **Unified Deployment**: Single `run` script for all deployment scenarios
- **Inventory Management**: `sync` script for validation, migration, and backup operations

---

## Success Metrics

- **Phase 1**: ✅ 100% inventory structure modernization with backward compatibility
- **Phase 2**: ✅ Complete video player role implementation with F1 project integration
- **Phase 3**: Comprehensive testing framework with validation coverage
- **Phase 4**: Enhanced features with multi-project support and advanced monitoring
- **Phase 5**: Production-ready deployment with security and performance optimization
- **Phase 6**: Complete documentation and user experience package

**🎉 OrangeAd Ansible - Modern Project-Based Orchestration System with Video Player Support!** 🚀

### Project Component Matrix

| Project     | Components                       | Description                                    |
| ----------- | -------------------------------- | ---------------------------------------------- |
| **F1**      | macos-api, tracker               | Formula 1 project with camera tracking         |
| **Spectra** | macos-api, tracker, player       | Spectra project with adaptive video display (single-screen fallback, dual-screen optimal) |
| **ALPR**    | macos-api, alpr                  | License plate recognition project              |

### Usage Examples

```bash
# List all available inventories and hosts
./scripts/sync list

# Deploy F1 project (macos-api + tracker)
./scripts/run f1-staging
./scripts/run f1-prod -l f1-ca-001

# Deploy Spectra project (macos-api + tracker + player)
./scripts/run spectra-staging
./scripts/run spectra-prod --dry-run

# Deploy ALPR project (macos-api + alpr)
./scripts/run alpr-staging
./scripts/run alpr-prod -l alpr-device-001

# Deploy specific components
./scripts/run f1-staging macos-api
./scripts/run spectra-staging player
./scripts/run alpr-staging alpr

# Reboot machines with production safety
./scripts/reboot f1-prod
./scripts/reboot spectra-staging f1-ca-001

# Validate all inventory files
./scripts/sync validate
```
