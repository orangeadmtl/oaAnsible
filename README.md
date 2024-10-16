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
├── roles/
│   └── main/
│       ├── tasks/
│       │   ├── node.yml
│       │   ├── pyenv.yml
│       │   ├── tailscale.yml
│       │   └── xcode.yml
│       └── templates/
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
- Set up Python environment using pyenv
- Configure Node.js and npm using NVM
- Install and configure Tailscale for secure networking
- Configure sudoers

## Usage

1. Clone this repository:

   ```sh
   git clone https://github.com/oa-device/oaAnsible.git
   cd oaAnsible
   ```

2. Review and modify the `inventory` file if needed. The current inventory includes a macOS machine named 'b3'.

3. Review and modify the `default.config.yml` file to suit your needs. This file contains all the configurable options for the playbook.

4. Install required roles:

   ```sh
   ansible-galaxy install -r requirements.yml
   ```

5. Run the playbook:

   ```sh
   ansible-playbook main.yml -K
   ```

   The `-K` flag prompts for the SUDO password.

   You can also use tags to run specific parts of the playbook:

   ```sh
   ansible-playbook main.yml -K --tags "python,node"
   ```

## Roles

This playbook uses the following role:

- `elliotweiser.osx-command-line-tools`: Installs Xcode Command Line Tools.

This role is automatically installed when you run `ansible-galaxy install -r requirements.yml`.

### Custom Tasks

The project includes custom tasks for setting up pyenv, Node.js (via NVM), Tailscale, and configuring sudoers. These tasks are defined in the `roles/main/tasks/` directory.

## Customization

You can customize the playbook by modifying the `default.config.yml` file. This file contains variables that control various aspects of the setup, such as Python and Node.js versions.

## Testing

To test the playbook:

1. Ensure you have the necessary permissions to manage the test machine (b3) remotely.

2. Run a dry run with the `--check` flag:

   ```sh
   ansible-playbook main.yml -K --check
   ```

   This will simulate the playbook execution without making any changes.

## Troubleshooting

If you encounter any errors during the playbook run, the output will provide information about where the failure occurred. You can increase verbosity with the `-v` flag (up to `-vvvv`) for more detailed output:

```sh
ansible-playbook main.yml -K -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is inspired by [geerlingguy/mac-dev-playbook](https://github.com/geerlingguy/mac-dev-playbook) and uses roles from [Jeff Geerling](https://github.com/geerlingguy) and [Elliot Weiser](https://github.com/elliotweiser).
