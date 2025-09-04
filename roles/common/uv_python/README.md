# UV Python Role

A streamlined Ansible role for Python environment management using UV package manager, replacing the complex pyenv-based approach.

## Features

- **Unified Python Management**: Single approach for macOS, Ubuntu, and all components
- **Simplified Installation**: UV handles Python installation, virtual environments, and dependencies
- **Performance Optimized**: Faster dependency resolution and installation than pip/pyenv
- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Cross-Platform**: Consistent behavior across macOS and Linux

## Usage

### Basic Usage
```yaml
- name: Setup Python environment
  import_role:
    name: common/uv_python
```

### With Custom Python Version
```yaml
- name: Setup Python 3.12
  import_role:
    name: common/uv_python
  vars:
    uv_python_version: "3.12.0"
```

### Skip Python Installation (UV only)
```yaml
- name: Install UV only
  import_role:
    name: common/uv_python
  vars:
    uv_manage_python: false
```

## Variables

### Core Configuration
- `uv_python_version`: Python version to install (default: from runtime_versions.yml)
- `uv_manage_python`: Whether UV should install/manage Python (default: true)
- `uv_install_method`: How to install UV - curl, homebrew (default: curl)

### Advanced Configuration
- `uv_concurrent_installs`: Parallel installation jobs (default: 4)
- `uv_link_mode`: How UV links packages - copy, hardlink, symlink (default: copy)
- `uv_resolution_strategy`: Dependency resolution - highest, lowest-direct (default: highest)

## Facts Set

After running, this role sets these facts for dependent roles:
- `python_environment_ready`: true
- `python_version_installed`: The installed Python version
- `python_manager`: "uv"
- `uv_path`: Path to UV executable
- `python_executable`: Command to run Python via UV

## Migration from PyEnv

This role replaces the complex pyenv-based Python management:

### Before (PyEnv)
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.11.11
pyenv global 3.11.11
python -m venv myproject
source myproject/bin/activate
pip install -r requirements.txt
```

### After (UV)
```bash
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.11.11
uv venv myproject
uv pip install -r requirements.txt
```

## Component Integration

For component roles (device_api, tracker, parking_monitor):

### Before
```yaml
python_path: "{{ ansible_user_dir }}/.pyenv/versions/3.11.11/bin/python"
venv_path: "{{ ansible_user_dir }}/.pyenv/versions/3.11.11/envs/myapp"
```

### After
```yaml
python_path: "{{ ansible_user_dir }}/.local/bin/uv run python"
project_path: "{{ ansible_user_dir }}/orangead/myapp"
```

Components now use project-based Python management with `uv sync` instead of separate virtual environments.