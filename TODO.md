# TODO: Enhance oaAnsible for macOS Management and Dashboard Integration

This plan outlines the steps to evolve `oaAnsible` into a comprehensive macOS configuration management tool and integrate Macs into the `oaDashboard`.

## Phase 1: Foundation and Restructuring

- [x] **Branching:** Create a new feature branch from `dev` (e.g., `feat/macos-management-api`).
- [x] **Project Restructuring (Ansible Roles):** Move tasks into dedicated roles (`macos_network`, `macos_python`, `macos_node`, `macos_base`).
- [x] **Ansible Configuration (`ansible.cfg`):** Update inventory path, disable retry files.
- [x] **Secrets Management:** Introduce Ansible Vault (`group_vars/all/vault.yml`).

## Phase 2: macOS Status API Development (Mirroring `opi-setup/api`)

- [x] **Create Project Structure (`macos-api`):** Basic FastAPI structure.
- [x] **Adapt Services (`macos-api/services/`):** Port logic from `opi-setup` for macOS (`system.py`, `display.py`, `tracker.py`, `health.py`). Handle headless systems.
- [x] **Adapt Routers (`macos-api/routers/`):** Update routers to use adapted services.
- [x] **Adapt Core (`macos-api/core/`):** Update config for macOS paths/commands.
- [x] **Update Models (`macos-api/models/`):** Adjust schemas for macOS data.
- [x] **Update `requirements.txt`:** Add FastAPI, psutil, etc. Use `uv`.
- [x] **Add `.gitignore` for `macos-api`:** Ignore virtual env, caches.

## Phase 3: Ansible Enhancements for macOS Configuration & API Deployment

- [x] **Dynamic Inventory:** Create `inventory/dynamic_inventory.py` using Tailscale API.
- [x] **New Ansible Role: `macos_api`:** Deploy `macos-api` files, create venv, install deps, set up `launchd` service, configure firewall.
- [x] **New Ansible Role: `macos_security`:** Configure macOS Firewall, screen lock, FileVault (check), Gatekeeper.
- [x] **New Ansible Role: `macos_settings`:** Configure system preferences, hostname.
- [ ] **New Ansible Role: `oa_tracker` (Placeholder):** Define tasks for future `oaTracker` (skipped for now).
- [x] **Update `main.yml`:** Include new roles with tags.
- [x] **Update `dev-cleanup.yml`:** Add tasks to uninstall `macos-api` and revert settings.

## Phase 4: Integration with `oaDashboard`

- [ ] **`oaDashboard` Backend:**
  - [ ] Modify `DeviceMonitorService` to detect macOS devices.
  - [ ] Query `macos-api` endpoint for macOS devices.
  - [ ] Adapt data processing for macOS API responses.
  - [ ] Update `DeviceEntity` model and `DeviceDTO` schema if needed.
- [ ] **`oaDashboard` Frontend:**
  - [ ] Update components (`DeviceTable`, `DeviceDetails`) to display macOS info correctly.
  - [ ] Conditionally render UI elements (e.g., Screenshot panel).
  - [ ] Adapt health/metric visualizations.

## Phase 5: Documentation and Refinement

- [ ] **Update `oaAnsible/README.md`:** Detail new structure, macOS API, dynamic inventory, Vault, roles.
- [ ] **Update `oaDashboard/README.md`:** Mention macOS support.
- [ ] **Testing:** Thoroughly test playbooks on target Macs and dashboard integration.
- [ ] **Refine:** Improve tasks, API responses, and UI based on testing.

---

## Testing on a Local Development Machine

This section details how to use the `staging` environment configuration to test the `oaAnsible` playbooks on a local development machine with the IP address `192.168.2.9`.

**Prerequisites:**

1. **Target Machine:** Ensure your local development machine has the IP address `192.168.2.9`.
2. **SSH Access:**
    - Enable Remote Login on the target Mac (System Settings > General > Sharing > Remote Login).
    - Ensure you can SSH from your control machine (where you run Ansible) to the target machine as the `admin` user.
    - **Recommended:** Configure SSH key-based authentication. Add your control machine's public SSH key (`~/.ssh/id_rsa.pub` or similar) to the `~/.ssh/authorized_keys` file on the target machine (`admin` user's home directory).
3. **Ansible Control Machine:** Have Ansible and the necessary collections (`ansible-galaxy install -r requirements.yml`) installed.

**Steps:**

1. **Verify Inventory:**

    - Check the `inventory/staging/hosts.yml` file. It should already list a host (e.g., `b3`) pointing to `ansible_host: 192.168.2.9` with `ansible_user: admin`. Adjust the hostname (`b3`) if necessary, but keep the IP and user.

    ```yaml
    # inventory/staging/hosts.yml
    all:
      # ...
      children:
        macos:
          hosts:
            your_dev_hostname: # Or keep b3
              ansible_host: 192.168.2.9
              ansible_user: admin
    ```

2. **Review Variables:**

    - Examine `inventory/staging/group_vars/all.yml`. This file defines the Python/Node versions, Homebrew packages, and feature toggles (`configure:`) that will be applied. Modify these settings if needed for your local test.

3. **(Optional) Clean Target Machine:**

    - If you want to ensure a clean slate before applying the configuration (removing Homebrew, pyenv, nvm, Tailscale, API service), run the cleanup playbook. You will be prompted for the `admin` user's sudo password.

    ```bash
    ansible-playbook dev-cleanup.yml -i inventory/staging/hosts.yml --ask-become-pass
    # You might also need --ask-vault-pass if vault.yml is used and encrypted
    ```

    - **Warning:** This playbook removes development tools and settings. Only run this on your designated local test machine.

4. **Run the Main Playbook:**

    - Execute the main playbook using the staging script. You will likely be prompted for the `admin` user's sudo password.

    ```bash
    ./scripts/run-staging.sh --ask-become-pass
    # Add --ask-vault-pass if vault.yml is used and encrypted
    ```

5. **Verify:**
    - After the playbook finishes, SSH into the target machine (`ssh admin@192.168.2.9`) and verify that the expected tools (Homebrew, Python, Node, etc.) are installed and configured correctly.
    - Check if the `macos-api` service is running: `curl http://localhost:9090/health`.

This setup allows you to iteratively test and develop the Ansible roles and playbooks on a local machine before applying them to actual staging or production environments managed via dynamic inventory.
