# Ansible Collection - lennysh.aap_maintenance

[![CI](https://github.com/lennysh/aap_maintenance/actions/workflows/tests.yml/badge.svg)](https://github.com/lennysh/aap_maintenance/actions/workflows/tests.yml)
[![GitHub license](https://img.shields.io/github/license/lennysh/aap_maintenance.svg)](https://github.com/lennysh/aap_maintenance/blob/devel/LICENSE)

> **Under construction / pre-1.0.0** — This collection is under active development
> toward a first stable release. APIs, layouts, and coverage may change
> without a deprecation cycle until **1.0.0**.

**Maintenance utilities for Ansible Automation Platform (AAP) 2.5+.**

Operational tasks on a running platform: cleanup stale data, health checks, and
related maintenance workflows. No other Ansible collections are required.

## Modules

| Module | Purpose |
| ------ | ------- |
| `soft_delete_hosts` | Soft-delete stale `host_metrics` rows not present in any inventory |

Example playbook: `playbooks/soft_delete_hosts.yml`.

### Soft-delete stale host metrics

AAP tracks hosts that have run jobs in **host metrics** (`/api/controller/v2/host_metrics`).
That list can grow when VMs are removed from inventories but their metrics rows remain.

This module:

1. Lists every host in all controller inventories
2. Lists non-deleted `host_metrics` rows
3. Soft-deletes metrics whose hostname is not in any inventory (case-insensitive compare)

Pagination runs inside the module (one API page at a time) so large environments do not
load hundreds of pages into Ansible facts.

```yaml
- name: Soft-delete host_metrics not in any inventory
  lennysh.aap_maintenance.soft_delete_hosts:
    aap_hostname: "{{ aap_hostname }}"
    aap_username: "{{ aap_username }}"
    aap_password: "{{ aap_password }}"
    aap_validate_certs: false
```

Preview only (no deletes):

```yaml
- lennysh.aap_maintenance.soft_delete_hosts:
    aap_hostname: "{{ aap_hostname }}"
    aap_token: "{{ aap_token }}"
    soft_delete: false
    return_hostnames: true
```

Or use check mode on the task when `soft_delete: true` to see what would change.

Playbook:

```bash
cp vars/example.yml vars/local.yml
ansible-playbook playbooks/soft_delete_hosts.yml -e @vars/local.yml
```

### Authentication

Pass `aap_token`, or `aap_username` / `aap_password`. With username/password the module
mints a short-lived gateway write token, uses it for all API calls, and revokes it on exit.
Tokens you supply yourself are left intact.

Environment variables are supported (`AAP_HOSTNAME`, `CONTROLLER_HOST`, `AAP_USERNAME`,
`CONTROLLER_USERNAME`, etc.) — see `vars/example.yml`.

## Installing

Install directly from GitHub with Ansible Galaxy:

```bash
ansible-galaxy collection install git+https://github.com/lennysh/aap_maintenance.git
```

Pin a branch or tag:

```bash
ansible-galaxy collection install git+https://github.com/lennysh/aap_maintenance.git,devel
# ansible-galaxy collection install git+https://github.com/lennysh/aap_maintenance.git,v1.0.0
```

Or via `requirements.yml`:

```yaml
---
collections:
  - name: https://github.com/lennysh/aap_maintenance.git
    type: git
    version: devel
...
```

```bash
ansible-galaxy collection install -r requirements.yml
```

## Requirements

- ansible-core `>=2.16`
- No other Ansible collections required

## Development

```bash
# Unit tests (no AAP required)
python3 -m unittest discover -s tests/unit -v
```

Python's pre-commit tool can be installed, and hooks installed, to clean up
whitespace, newlines, and run yamllint and ansible-lint before committing:

```bash
pip install pre-commit
pre-commit install --install-hooks -c .pre-commit-config.yaml
```

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
