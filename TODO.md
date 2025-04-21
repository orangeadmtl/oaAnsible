# TODO: Enhance oaAnsible for macOS Management and Dashboard Integration

This plan outlines the steps to evolve `oaAnsible` into a comprehensive macOS configuration management tool and integrate Macs into the `oaDashboard`.

## Phase 1: Foundation and Restructuring

- [ ] **Branching:** Create a new feature branch from `dev` (e.g., `feat/macos-management-api`).

  ```bash
  # In oaAnsible directory
  git checkout dev
  git pull origin dev
  git checkout -b feat/macos-management-api
  ```

- [ ] **Project Restructuring (Ansible Roles):**
  - [ ] Move `roles/local/tasks/dns.yml` to a dedicated role, e.g., `roles/macos_network`.
  - [ ] Move `roles/local/tasks/tailscale.yml` into the new `roles/macos_network` role or its own `roles/tailscale` role.
  - [ ] Move `roles/local/tasks/pyenv.yml` to `roles/macos_python`.
  - [ ] Move `roles/local/tasks/node.yml` to `roles/macos_node`.
  - [ ] Rename `roles/local` to `roles/macos_base` or similar, keeping only shell configuration (`main.yml`).
  - [ ] Update `main.yml` to import tasks/roles from their new locations.
- [ ] **Ansible Configuration (`ansible.cfg`):**
  - [ ] Review and potentially configure `inventory` path/script setting.
  - [ ] Consider setting `retry_files_enabled = False` to avoid `.retry` files.
  - [ ] Ensure `roles_path` includes the restructured `roles/` directory.
- [ ] **Secrets Management:**
  - [ ] Introduce **Ansible Vault** for sensitive data (e.g., SSH keys if not using agent forwarding, potential future API keys).
  - [ ] Create `group_vars/all/vault.yml` (or similar) encrypted file.
  - [ ] Document vault usage (`ansible-playbook --ask-vault-pass` or vault password file).

## Phase 2: macOS Status API Development (Mirroring `opi-setup/api`)

- [ ] **Decision:** Reuse `opi-setup/api` codebase or create a new, similar project?
  - _Recommendation:_ Create a new directory `macos-api` within `oaAnsible` (or potentially as a separate submodule later). Copy relevant parts of `opi-setup/api` as a starting point.
- [ ] **Create Project Structure (`macos-api`):**
  - [ ] Basic FastAPI structure: `main.py`, `routers/`, `services/`, `models/`, `core/`, `requirements.txt`.
- [ ] **Adapt Services (`macos-api/services/`):**
  - [ ] **`system.py`:**
    - Keep `get_system_metrics` (leverages cross-platform `psutil`).
    - Adapt `get_device_info` for macOS (use `sysctl` or other macOS commands to determine model/series if needed, maybe default to "Mac").
    - Adapt `get_version_info` (use `platform`, `sw_vers`, check Tailscale version path `/Applications/Tailscale.app/Contents/MacOS/Tailscale`).
    - Adapt `get_service_info` to use `launchctl` instead of `systemctl`.
  - [ ] **`display.py` (Conditional):**
    - Adapt `get_display_info` using macOS commands (e.g., `system_profiler SPDisplaysDataType`). _Crucially_, make this function gracefully handle headless systems (return default/empty data or a specific 'headless' status).
    - Adapt `take_screenshot` using `screencapture` command. Make this conditional based on display presence.
    - Adapt `get_screenshot_history`.
  - [ ] **`player.py` (Adapt for `oaTracker`):**
    - Rename/refactor to `tracker.py` or similar.
    - Adapt `check_player_status` to check the status of the _`oaTracker`_ process/service (using `launchctl list | grep ...` and `ps aux | grep ...`). This assumes `oaTracker` will eventually run as a service managed by `launchd`.
    - Adapt `get_deployment_info` to report `oaTracker` version and status. Make display info conditional.
  - [ ] **`health.py`:** Keep as is initially; `calculate_health_score` uses data from other services. Weights might need tuning for Macs.
  - [ ] **`utils.py`:** Keep as is (cross-platform).
- [ ] **Adapt Routers (`macos-api/routers/`):**
  - [ ] Update routers (`health.py`, `screenshots.py`) to call the adapted service functions.
  - [ ] Ensure screenshot routes handle headless scenarios (e.g., return 404 or specific error).
- [ ] **Adapt Core (`macos-api/core/`):**
  - [ ] Update `config.py` with relevant paths/commands for macOS. Remove OrangePi-specific paths.
- [ ] **Update Models (`macos-api/models/`):**
  - [ ] Adjust `schemas.py` if the structure of information returned by macOS commands differs significantly (e.g., display info). Add flags/fields indicating headless status if needed.
- [ ] **Update `requirements.txt`:** Include `fastapi`, `uvicorn`, `psutil`, `pydantic`, etc. `uv` should be used for installation.
- [ ] **Add `.gitignore` for `macos-api`:** Ignore `.venv`, `__pycache__`, etc.

## Phase 3: Ansible Enhancements for macOS Configuration & API Deployment

- [ ] **Dynamic Inventory:**
  - [ ] Create an inventory script (e.g., `inventory/dynamic_inventory.py`) that:
    - Reads Tailscale API Key (from Vault or env var).
    - Queries Tailscale API (`/api/v2/tailnet/-/devices`) for devices tagged appropriately (e.g., `tag:macos-managed`) or identified as macOS.
    - Outputs JSON inventory format including `ansible_host` (Tailscale IP) and other relevant vars (`hostname`, `os`).
  - [ ] Update `ansible.cfg` to point `inventory` to this script.
  - [ ] Update `inventory/` directory structure (remove static `hosts.yml` or keep for local testing).
- [ ] **New Ansible Role: `macos_api`:**
  - [ ] **Task:** Copy the `macos-api` project files to a target directory on the Mac (e.g., `/usr/local/orangead/macos-api`).
  - [ ] **Task:** Create Python virtual environment using `uv` (e.g., `/usr/local/orangead/macos-api/.venv`).
  - [ ] **Task:** Install API dependencies using `uv pip install -r requirements.txt`.
  - [ ] **Task:** Create a `launchd` plist file (e.g., in `/Library/LaunchDaemons/com.orangead.macosapi.plist`) to run the API using `uvicorn`.
    - Ensure it runs as a specific user (e.g., `_orangead` - create this user if needed).
    - Set `WorkingDirectory`.
    - Set necessary `EnvironmentVariables` (like `PYTHONPATH`).
    - Configure `StandardOutPath` and `StandardErrorPath` for logging.
    - Set `RunAtLoad` and `KeepAlive`.
  - [ ] **Handler:** Load/reload the `launchd` service when the plist file or API code changes.
  - [ ] **Task:** Ensure the API port (e.g., 9090) is allowed through the macOS firewall (`pf` or `socketfilterfw`).
- [ ] **New Ansible Role: `macos_security`:**
  - [ ] **Task:** Configure macOS Firewall (`pfctl` via `command` or `community.general.pf` if suitable, or using `socketfilterfw`). Allow necessary ports (SSH, API port, Tailscale ports).
  - [ ] **Task:** Enforce screen lock after inactivity (`defaults write com.apple.screensaver askForPassword -int 1`, `defaults write com.apple.screensaver askForPasswordDelay -int 5`).
  - [ ] **Task:** Configure FileVault settings (check status, potentially enforce - complex, might require user interaction or MDM).
  - [ ] **Task:** Configure Gatekeeper settings.
  - [ ] **Task:** Configure basic password policies if needed.
- [ ] **New Ansible Role: `macos_settings`:**
  - [ ] **Task:** Configure system preferences using `defaults write` (e.g., disable guest user, time zone, remote login settings).
  - [ ] **Task:** Set hostname if not already matching inventory/desired state.
- [ ] **New Ansible Role: `oa_tracker` (Placeholder):**
  - [ ] Define tasks to deploy and manage the future `oaTracker` application (install, configure, manage service via `launchd`).
- [ ] **Update `main.yml`:** Include the new roles (`macos_api`, `macos_security`, `macos_settings`, `oa_tracker`). Use tags appropriately.
- [ ] **Update `dev-cleanup.yml`:** Add tasks to uninstall the `macos-api`, remove its `launchd` plist, and revert security/system settings applied by the new roles.

## Phase 4: Integration with `oaDashboard`

- [ ] **`oaDashboard` Backend:**
  - [ ] Modify `DeviceMonitorService` (or create a new service) to detect macOS devices (e.g., based on Tailscale OS field or tags).
  - [ ] For macOS devices, query the new `macos-api` endpoint (`http://<tailscale_ip>:9090/health`) instead of the `opi-setup` one.
  - [ ] Adapt the data processing logic to handle potential differences in the macOS API response (especially regarding headless status, display info, tracker status vs. player status).
  - [ ] Update `DeviceEntity` model and `DeviceDTO` schema if necessary to store/represent Mac-specific states or lack thereof (e.g., no display info).
  - [ ] (Optional) Implement endpoint to trigger Ansible runs via `ansible-runner`.
  - [ ] (Optional) Modify inventory generation endpoint if `oaAnsible` uses it.
- [ ] **`oaDashboard` Frontend:**
  - [ ] Update `DeviceTable` and `DeviceDetails` components to correctly display information for macOS devices.
  - [ ] Conditionally render components based on device type or available data (e.g., don't show Screenshot panel for headless Macs, show Tracker status instead of Player status).
  - [ ] Adapt health/metric visualizations if necessary.
  - [ ] (Optional) Add UI elements to trigger/monitor Ansible runs if implemented in the backend.

## Phase 5: Documentation and Refinement

- [ ] **Update `oaAnsible/README.md`:** Detail the new structure, macOS API, `launchd` service setup, dynamic inventory usage, Vault setup, and new roles.
- [ ] **Update `oaDashboard/README.md`:** Mention support for macOS devices and integration with `oaAnsible`.
- [ ] **Update `oaPangaea/.windsurfrules`:** Ensure it reflects the final structure and guidelines for all three components.
- [ ] **Testing:** Thoroughly test Ansible playbooks on target Macs (different models/OS versions if possible). Test the `macos-api` independently. Test the full `oaDashboard` integration.
- [ ] **Refine:** Based on testing, refine Ansible tasks, API responses, and dashboard display logic. Tune health score weights if needed.
