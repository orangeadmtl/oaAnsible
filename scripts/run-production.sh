#!/bin/bash
echo "⚠️  Running in PRODUCTION environment"
echo "Press CTRL+C now to abort, or wait 5 seconds to continue..."
sleep 5
ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml -i inventory/production/hosts.yml "$@"
