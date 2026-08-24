# Ansible Collection - lennysh.aap_maintenance

[![CI](https://github.com/lennysh/aap_maintenance/actions/workflows/tests.yml/badge.svg)](https://github.com/lennysh/aap_maintenance/actions/workflows/tests.yml)
[![GitHub license](https://img.shields.io/github/license/lennysh/aap_maintenance.svg)](https://github.com/lennysh/aap_maintenance/blob/devel/LICENSE)

> **Under construction / pre-1.0.0** — This collection is under active development
> toward a first stable release. APIs, layouts, and coverage may change
> without a deprecation cycle until **1.0.0**.

**Maintenance utilities for Ansible Automation Platform 2.5+.**

Companion to [`lennysh.aap_configuration`](https://github.com/lennysh/lennysh.aap_configuration)
(Configuration-as-Code). This collection is for operational maintenance of a
running platform — cleanup, health checks, and related tasks.

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
