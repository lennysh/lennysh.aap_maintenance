# Export installer secrets

Export auto-generated AAP installer crypto keys from a running **RPM** or
**containerized** deployment into plain-text files you can vault and reuse on
future installer runs.

## Requirements

- Ansible core `>=2.16`
- The same **installer inventory** used for the original install (`-i inventory`)
- SSH access to component hosts with privilege escalation as required
- **Containerized only:** `containers.podman` collection (`>=1.14.0`)

## Quick start

```bash
ansible-playbook -i inventory playbooks/export_installer_secrets.yml \
  -e install_type=containerized

# Recommended before storing or committing
ansible-vault encrypt installer-secrets.yml
```

On the next install or reinstall:

```bash
ansible-playbook -i inventory .../install -e @installer-secrets.yml
```

## Output files

Written to `installer_secrets_output_dir` (default: playbook directory):

| File | Purpose |
| ---- | ------- |
| `installer-secrets.yml` | YAML extra-vars (`-e @installer-secrets.yml`) |
| `installer-secrets-inventory.snippet` | Commented INI lines for copy/paste into inventory |

Both files are created with mode `0600`.

## Role variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `install_type` | *(required)* | `rpm` or `containerized` |
| `installer_secrets_output_dir` | `{{ playbook_dir }}` | Output directory |
| `installer_secrets_output_basename` | `installer-secrets` | Output file basename |
| `installer_secrets_include_lightspeed` | `true` | Export when `ansiblelightspeed` group exists |
| `installer_secrets_include_metrics` | `true` | Export when `automationmetrics` group exists |
| `installer_secrets_strict_groups` | `false` | Fail if a required component group is missing |

## Supported components (AAP 2.6+)

Secrets are read from the **first host** in each inventory group:

| Inventory group | Exported vars (containerized) | RPM notes |
| --------------- | ----------------------------- | ------- |
| `automationcontroller` | `controller_secret_key` | `secret_key_override` |
| `automationgateway` | `gateway_secret_key` | `gateway_secret_key` |
| `automationhub` | `hub_secret_key`, `hub_database_fields` | `hub_secret_key`, `hub_database_fields` |
| `automationeda` / `automationedacontroller` | `eda_secret_key` | `eda_secret_key` |
| `ansiblelightspeed` | `lightspeed_secret_key` | containerized only |
| `automationmetrics` | `automationmetrics_secret_key` | containerized only |

`hub_database_fields` matches the containerized podman secret name. There is no
standard scalar in `inventory-example`; the export includes a comment explaining
how to preserve it.

## Example

```yaml
- hosts: localhost
  connection: local
  gather_facts: true
  tasks:
    - ansible.builtin.include_role:
        name: lennysh.aap_maintenance.aap_installer_secrets_export
      vars:
        install_type: rpm
        installer_secrets_output_dir: /root/aap-backups
        installer_secrets_output_basename: prod-installer-secrets
```

## Security

- Tasks that read secrets use `no_log: true`.
- Encrypt `installer-secrets.yml` with `ansible-vault` before storing in git or
  ticket systems.
- This role exports **crypto identity keys** only — not full platform backups.

## License

GPL-3.0-or-later
