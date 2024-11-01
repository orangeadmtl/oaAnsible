#!/bin/bash
ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml -i inventory/staging/hosts.yml "$@"
