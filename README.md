# OrangeAd Mac Setup Playbook

This Ansible playbook automates the setup and configuration of MacOS devices for the OrangeAd project. It installs and configures essential software and tools to quickly get new devices ready for development.

## Project Structure

```tree
oaAnsible/
├── default.config.yml
├── inventory
├── main.yml
├── README.md
├── requirements.yml
├── tasks/
│   ├── node.yml
│   ├── pyenv.yml
│   ├── tailscale.yml
│   └── xcode.yml
```

## Prerequisites

1. Ensure Apple's command line tools are installed (`xcode-select --install`).
2. [Install Ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html):

   ```sh
   pip3 install ansible
   ```

## Installation

1. Clone this repository to your local drive.
2. Run `ansible-galaxy install -r requirements.yml` inside this directory to install required Ansible roles.
3. Update the `inventory` file with the correct IP address or hostname of your remote Mac.
4. Run `ansible-playbook main.yml -i inventory --ask-become-pass` inside this directory. Enter your macOS account password when prompted for the 'BECOME' password.

## Customization

You can override any of the defaults configured in `default.config.yml` by creating a `config.yml` file and setting the overrides in that file.

## Included Software and Configurations

- Homebrew packages: git, node, nvm, pyenv, xcode-select
- Homebrew Cask apps: Google Chrome
- Python 3.10 (via pyenv)
- Node.js v20.18.0 (via nvm)
- Tailscale (version 1.76.0)
- Xcode Command Line Tools

## Task Descriptions

- `pyenv.yml`: Installs pyenv and sets the default Python version.
- `node.yml`: Installs Node.js, nvm, and sets up a specific Node.js version.
- `tailscale.yml`: Downloads and installs Tailscale.
- `xcode.yml`: Installs Xcode Command Line Tools and accepts the license.

## Remote Usage

This playbook is configured to work on remote Mac machines. The default inventory file is set up for a Mac Mini with the hostname 'b3'.

## Acknowledgments

This project is inspired by [geerlingguy/mac-dev-playbook](https://github.com/geerlingguy/mac-dev-playbook).
