# OrangeAd Mac Setup Playbook

This Ansible playbook automates the setup and configuration of macOS devices for the OrangeAd project. It installs and configures essential software and tools to quickly get new macOS devices ready for development and remote management.

## Project Structure

```tree
oaAnsible/
├── default.config.yml
├── inventory
├── main.yml
├── README.md
├── requirements.yml
├── playbooks/
│   └── macos.yml
├── roles/
│   └── main/
│       ├── tasks/
│       │   ├── node.yml
│       │   ├── pyenv.yml
│       │   ├── tailscale.yml
│       │   ├── xcode.yml
│       │   ├── firewall.yml
│       │   └── monitoring.yml
│       └── templates/
│           ├── com.github.prometheus.node_exporter.plist.j2
│           └── sudoers.j2
└── tests/
    └── test.yml
```

## Prerequisites

1. Ensure Ansible is installed on your control machine (which should be a Mac):

   ```sh
   pip3 install ansible
   ```

2. Make sure you have the necessary permissions to manage the target macOS machines remotely.

## Features

This playbook configures the following on your macOS devices:

- Install Xcode Command Line Tools using `elliotweiser.osx-command-line-tools` role
- Manage Homebrew, packages, and cask applications using `geerlingguy.mac.homebrew` role
- Manage Mac App Store applications using `geerlingguy.mac.mas` role
- Configure the Dock using `geerlingguy.mac.dock` role
- Set up Python environment using pyenv
- Configure Node.js and npm
- Install and configure Tailscale for secure networking
- Set up macOS firewall rules
- Install and configure monitoring tools
- Configure macOS-specific settings
- Configure sudoers

## Usage

1. Clone this repository:

   ```sh
   git clone https://github.com/oa-device/oaAnsible.git
   cd oaAnsible
   ```

2. Review and modify the `inventory` file if needed. The current inventory includes a macOS machine named 'b3'.

3. Review and modify the `default.config.yml` file to suit your needs. This file contains all the configurable options for the playbook.

4. Install required roles and collections:

   ```sh
   ansible-galaxy install -r requirements.yml
   ```

5. Run the playbook:

   ```sh
   ansible-playbook -i inventory playbooks/macos.yml
   ```

   If you need to enter a sudo password, use the `-K` flag:

   ```sh
   ansible-playbook -i inventory playbooks/macos.yml -K
   ```

   You can also use tags to run specific parts of the playbook:

   ```sh
   ansible-playbook -i inventory playbooks/macos.yml -K --tags "homebrew,python,node"
   ```

## Roles

This playbook uses the following roles:

- `elliotweiser.osx-command-line-tools`: Installs Xcode Command Line Tools.
- `geerlingguy.mac.homebrew`: Manages Homebrew installation and package management.
- `geerlingguy.mac.mas`: Manages Mac App Store application installation.
- `geerlingguy.mac.dock`: Manages the macOS Dock configuration.

These roles are automatically installed when you run `ansible-galaxy install -r requirements.yml`.

## Customization

### Configuration Overrides

You can override any of the defaults configured in `default.config.yml` by creating a `config.yml` file and setting the overrides in that file.

## Testing

To test the playbook:

1. Ensure you have the necessary permissions to manage the test machine (b3) remotely.

2. Run a dry run with the `--check` flag:

   ```sh
   ansible-playbook -i inventory playbooks/macos.yml -K --check
   ```

   This will simulate the playbook execution without making any changes.

## Troubleshooting

If you encounter any errors during the playbook run, the output will provide information about where the failure occurred. You can increase verbosity with the `-v` flag (up to `-vvvv`) for more detailed output:

```sh
ansible-playbook -i inventory playbooks/macos.yml -K -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is inspired by [geerlingguy/mac-dev-playbook](https://github.com/geerlingguy/mac-dev-playbook) and uses roles from [Jeff Geerling](https://github.com/geerlingguy) and [Elliot Weiser](https://github.com/elliotweiser).
