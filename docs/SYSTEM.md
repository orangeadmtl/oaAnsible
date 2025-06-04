# oaPangaea System Sequence Diagrams

This document provides sequence diagrams to illustrate key workflows within the oaPangaea project, focusing on `oaAnsible` deployment and `oaDashboard` interactions.

## 1. `oaAnsible`: macOS Device Onboarding & Application Deployment

This diagram shows the typical flow when `oaAnsible` (via a script like `run-staging.sh` or `onboard-mac.sh`) configures a new macOS device and deploys `macos-api` and `oaTracker`.

```mermaid
sequenceDiagram
    participant User as Operator/Admin
    participant Script as Onboarding Script (e.g., run-staging.sh)
    participant AnsibleController as Ansible Controller Node
    participant TargetMac as Target macOS Host (ansible_user)
    participant PyPI_NPM_Etc as Package Repositories
    participant GitHub_GoProxy as Source Repos (Git, Go Modules)
    participant TailscaleControl as Tailscale Control Plane

    User->>Script: Execute onboarding script (e.g., ./run-staging.sh)
    Script->>AnsibleController: Invoke `ansible-playbook main.yml` with inventory & vault
    AnsibleController->>TargetMac: 0. Establish SSH Connection (as ansible_user)

    %% Phase 1: Core System Setup
    AnsibleController->>TargetMac: 1.1 Install Command Line Tools (Role: osx-command-line-tools)
    TargetMac-->>AnsibleController: CLT Status
    AnsibleController->>TargetMac: 1.2 Install Homebrew & Core Packages (e.g., git, go) (Role: geerlingguy.mac.homebrew)
    TargetMac->>PyPI_NPM_Etc: Download Homebrew packages
    PyPI_NPM_Etc-->>TargetMac: Packages
    TargetMac-->>AnsibleController: Homebrew & Packages Status

    AnsibleController->>TargetMac: 1.3 Configure Base System (sudo, shell) (Role: macos/base)
    TargetMac-->>AnsibleController: Base System Config Status

    AnsibleController->>TargetMac: 1.4 Setup Pyenv & Python versions (Role: macos/python)
    TargetMac->>GitHub_GoProxy: Download Pyenv/Python source
    GitHub_GoProxy-->>TargetMac: Source files
    TargetMac-->>AnsibleController: Pyenv & Python Status
    AnsibleController->>TargetMac: 1.5 Install uv (Python package manager) (Role: macos/python)
    TargetMac->>PyPI_NPM_Etc: Download uv
    PyPI_NPM_Etc-->>TargetMac: uv package
    TargetMac-->>AnsibleController: uv Status

    AnsibleController->>TargetMac: 1.6 Setup NVM & Node.js version (Role: macos/node)
    TargetMac->>GitHub_GoProxy: Download NVM/Node.js source
    GitHub_GoProxy-->>TargetMac: Source files
    TargetMac-->>AnsibleController: NVM & Node.js Status
    AnsibleController->>TargetMac: 1.7 Install Bun (JS runtime) (Role: macos/node)
    TargetMac->>PyPI_NPM_Etc: Download Bun
    PyPI_NPM_Etc-->>TargetMac: Bun package
    TargetMac-->>AnsibleController: Bun Status

    %% Phase 2: Networking & Security
    AnsibleController->>TargetMac: 2.1 Deploy SSH Key for ansible_user (Role: macos/ssh)
    TargetMac-->>AnsibleController: SSH Key Status

    AnsibleController->>TargetMac: 2.2 Install Tailscale from Source & Configure Daemon (Role: macos/network/tailscale)
    TargetMac->>GitHub_GoProxy: Download Tailscale Go modules
    GitHub_GoProxy-->>TargetMac: Tailscale source
    TargetMac-->>TargetMac: Compile tailscale & tailscaled
    TargetMac->>TargetMac: Run `tailscaled install-system-daemon` (creates system LaunchDaemon)
    TargetMac->>TailscaleControl: `tailscale up --authkey=...` (device registers)
    TailscaleControl-->>TargetMac: Auth successful, IP assigned
    TargetMac-->>AnsibleController: Tailscale Daemon & CLI Status

    AnsibleController->>TargetMac: 2.3 Configure DNS (Role: macos/network)
    TargetMac-->>AnsibleController: DNS Config Status

    AnsibleController->>TargetMac: 2.4 Configure macOS Firewall & Security Settings (Role: macos/security)
    TargetMac-->>TargetMac: Grant Camera Access (TCC.db for ansible_user)
    TargetMac-->>AnsibleController: Security Settings Status

    AnsibleController->>TargetMac: 2.5 Configure System Settings (hostname, daily reboot LaunchDaemon) (Role: macos/settings)
    TargetMac-->>TargetMac: Create Daily Reboot system LaunchDaemon
    TargetMac-->>AnsibleController: System Settings Status

    %% Phase 3: Application Deployment (as ansible_user LaunchAgents)
    AnsibleController->>TargetMac: 3.1 Deploy macos-api (Role: macos/api)
    TargetMac-->>TargetMac: Create venv (macos-api)
    TargetMac->>PyPI_NPM_Etc: Download macos-api Python deps (uv)
    PyPI_NPM_Etc-->>TargetMac: Python packages
    TargetMac-->>TargetMac: Install macos-api deps into venv
    TargetMac-->>TargetMac: Create macos-api User LaunchAgent
    TargetMac-->>AnsibleController: macos-api Deployment Status

    AnsibleController->>TargetMac: 3.2 Deploy oaTracker (Role: macos/tracker)
    TargetMac-->>TargetMac: Create venv (oaTracker)
    TargetMac->>PyPI_NPM_Etc: Download oaTracker Python deps (uv)
    PyPI_NPM_Etc-->>TargetMac: Python packages
    TargetMac-->>TargetMac: Install oaTracker deps into venv
    TargetMac-->>TargetMac: Create oaTracker User LaunchAgent
    TargetMac-->>AnsibleController: oaTracker Deployment Status

    %% Phase 4: Verification
    AnsibleController->>TargetMac: 4.1 Run Verification Tasks (tasks/verify.yml)
    TargetMac-->>TargetMac: Check versions, service status (launchctl print ...)
    TargetMac-->>TargetMac: HTTP Health Checks (curl localhost:9090/health, curl localhost:8080/api/stats)
    TargetMac-->>AnsibleController: Verification Results
    AnsibleController-->>Script: Playbook Finished
    Script-->>User: Output log & final status
```

## 2. `oaDashboard`: Monitoring & Interacting with a macOS Device

This diagram illustrates how `oaDashboard` (Frontend and Backend) interacts with a Mac Mini managed by `oaAnsible`.

```mermaid
sequenceDiagram
    participant User as Dashboard User
    participant OADashboardFE as oaDashboard Frontend (Next.js)
    participant OADashboardBE as oaDashboard Backend (FastAPI)
    participant TailscaleControl as Tailscale Control Plane
    participant MacOSAPI as macOS API (on Mac Mini, port 9090)
    participant OATracker as oaTracker (on Mac Mini, port 8080)
    participant TargetMacSSH as Target Mac SSH Daemon

    %% Device Discovery and Health Monitoring (Periodic)
    OADashboardBE->>TailscaleControl: GET /api/v2/tailnet/.../devices (TailscaleService)
    TailscaleControl-->>OADashboardBE: List of devices (includes Mac Minis with 'tag:oa-macos')
    OADashboardBE->>OADashboardBE: Filter for managed Mac Minis
    loop For each managed Mac Mini
        OADashboardBE->>MacOSAPI: GET /health (via Tailscale IP:9090)
        MacOSAPI-->>OADashboardBE: Health data (system, tracker status, security, display, etc.)
        OADashboardBE->>MacOSAPI: GET /cameras (via Tailscale IP:9090)
        MacOSAPI-->>OADashboardBE: Camera list
        OADashboardBE->>OADashboardBE: Store/Cache device status & health (DB & Redis)
    end

    %% User Views Device List
    User->>OADashboardFE: Navigate to Devices Page
    OADashboardFE->>OADashboardBE: GET /api/v1/devices
    OADashboardBE-->>OADashboardFE: List of all devices (including Macs from cache/DB)
    OADashboardFE-->>User: Display Device Table

    %% User Views Mac Mini Details
    User->>OADashboardFE: Click on a Mac Mini
    OADashboardFE->>OADashboardBE: GET /api/v1/devices/{mac_mini_id}
    OADashboardBE-->>OADashboardBE: Retrieve Mac Mini data from DB/cache
    OADashboardBE-->>OADashboardFE: Mac Mini details (includes macos_tracker_info, macos_system_details etc.)
    OADashboardFE-->>User: Display Mac Mini Detail Page (Tracker Info, System Info, Security Info, No Live Camera Feed)

    %% User Initiates SSH Connection
    User->>OADashboardFE: Open SSH Terminal for Mac Mini
    OADashboardFE->>OADashboardBE: WebSocket /api/v1/devices/{mac_mini_id}/ssh
    OADashboardBE->>OADashboardBE: SSHSessionManager.create_session()
    OADashboardBE->>TargetMacSSH: Establish SSH connection (Paramiko, Tailscale IP:22)
    TargetMacSSH-->>OADashboardBE: SSH channel established
    OADashboardBE-->>OADashboardFE: WebSocket connection open, auth prompt if needed
    User->>OADashboardFE: Enter SSH credentials (if prompted)
    OADashboardFE->>OADashboardBE: Send credentials over WebSocket
    OADashboardBE-->>TargetMacSSH: Authenticate SSH
    loop SSH Session Active
        User->>OADashboardFE: Type command in terminal
        OADashboardFE->>OADashboardBE: Send command data (WebSocket)
        OADashboardBE->>TargetMacSSH: Send command data (SSH channel)
        TargetMacSSH-->>OADashboardBE: Command output (SSH channel)
        OADashboardBE->>OADashboardFE: Send output data (WebSocket)
        OADashboardFE-->>User: Display output in terminal
    end

    %% User Initiates Action (e.g., Restart Tracker)
    User->>OADashboardFE: Click "Restart Tracker" button
    OADashboardFE->>OADashboardBE: POST /api/v1/devices/{mac_mini_id}/actions/restart-tracker
    OADashboardBE->>OADashboardBE: DeviceActionsService.restart_player_or_tracker()
    OADashboardBE->>MacOSAPI: POST /actions/restart-tracker (via Tailscale IP:9090)
    MacOSAPI->>MacOSAPI: `launchctl kickstart -k gui/.../com.orangead.tracker`
    MacOSAPI-->>OADashboardBE: Action status
    OADashboardBE-->>OADashboardFE: Action status
    OADashboardFE-->>User: Display action result (toast)

    %% (Optional) Dashboard requests Tracker Stream (if a specific UI element triggers it, e.g., a debug view)
    User->>OADashboardFE: Request Tracker MJPEG Stream (e.g., via a special debug button/link)
    OADashboardFE->>OADashboardBE: GET /api/v1/devices/{mac_mini_id}/cameras/{tracker_cam_id}/stream (or similar endpoint)
    OADashboardBE->>MacOSAPI: GET /tracker/stream (or /cameras/.../stream if macos-api proxies specific camera)
    MacOSAPI->>OATracker: GET /cam.jpg (or /mjpeg) (localhost:8080)
    OATracker-->>MacOSAPI: MJPEG Stream Chunks
    MacOSAPI-->>OADashboardBE: MJPEG Stream Chunks
    OADashboardBE-->>OADashboardFE: MJPEG Stream Chunks
    OADashboardFE-->>User: Display Stream
```

## Notes on Diagrams

- **User Context**:
  - In Diagram 1 (`oaAnsible`), `ansible_user` is the user account on the `Target macOS Host` under which Ansible performs most operations and deploys applications.
  - The `Operator/Admin` is the human running the Ansible playbook from the `Ansible Controller Node`.
- **LaunchAgents vs. LaunchDaemons**:
  - `macos-api` and `oaTracker` are deployed as **User LaunchAgents** (`~/Library/LaunchAgents/`) and run as `ansible_user`.
  - `tailscaled` (Tailscale daemon) and the daily reboot task are configured as **System LaunchDaemons** (`/Library/LaunchDaemons/`) and run as `root`.
- **Installation Paths**:
  - Applications (`macos-api`, `oaTracker`) are installed under `{{ ansible_user_dir }}/orangead/`.
  - Core tools like `pyenv`, `nvm`, `go binaries` are typically installed in `ansible_user`'s home directory (e.g., `~/.pyenv`, `~/.nvm`, `~/go/bin`). Symlinks might be created in `/usr/local/bin` for system-wide CLI access.
- **API Interactions**:
  - `oaDashboard Backend` communicates with `macos-api` over Tailscale.
  - `macos-api` communicates with `oaTracker`'s API typically on `localhost` on the Mac Mini.

These diagrams should provide a clear overview of the system's architecture and key operational flows.
