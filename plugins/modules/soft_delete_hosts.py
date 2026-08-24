#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: soft_delete_hosts
short_description: Soft-delete host_metrics entries not present in any inventory
description:
  - Compares controller C(host_metrics) (non-deleted) against all controller C(hosts) across inventories.
  - Soft-deletes metrics rows whose hostname is not present in any inventory (case-insensitive).
  - Streams API pages in Python instead of accumulating large Ansible facts, which avoids high memory
    use when the controller returns hundreds of paginated results.
version_added: "0.1.0"
author: Lenny Shirley (@lennysh)
options:
  page_size:
    description:
      - Page size for controller list API requests.
      - Smaller values can help when the controller is slow to return large host lists.
    type: int
    default: 200
  soft_delete:
    description:
      - When C(true), issue DELETE against matching C(host_metrics) rows.
      - When C(false), scan and report candidates only; no deletes are performed.
    type: bool
    default: true
  return_hostnames:
    description:
      - Include C(candidate_hostnames) in the module result.
      - Leave C(false) when deleting thousands of hosts to keep the task result small.
    type: bool
    default: false
extends_documentation_fragment:
  - lennysh.aap_maintenance.aap_auth
"""

EXAMPLES = r"""
- name: Soft-delete host_metrics rows not in any inventory
  lennysh.aap_maintenance.soft_delete_hosts:
    aap_hostname: "{{ aap_hostname }}"
    aap_username: "{{ aap_username }}"
    aap_password: "{{ aap_password }}"
    aap_validate_certs: false

- name: Report candidates only (no DELETE)
  lennysh.aap_maintenance.soft_delete_hosts:
    aap_hostname: "{{ aap_hostname }}"
    aap_token: "{{ aap_token }}"
    soft_delete: false
    return_hostnames: true

- name: Check mode preview
  lennysh.aap_maintenance.soft_delete_hosts:
    aap_hostname: "{{ aap_hostname }}"
    aap_token: "{{ aap_token }}"
  check_mode: true
"""

RETURN = r"""
inventory_host_count:
  description: Unique inventory hostnames scanned (case-insensitive).
  type: int
  returned: always
metrics_host_count:
  description: Non-deleted host_metrics rows scanned.
  type: int
  returned: always
candidate_count:
  description: Metrics hostnames absent from all inventories.
  type: int
  returned: always
soft_deleted_count:
  description: Metrics rows soft-deleted (0 in check mode or when I(soft_delete=false)).
  type: int
  returned: always
candidate_hostnames:
  description: Hostnames that matched the delete criteria when I(return_hostnames=true).
  type: list
  elements: str
  returned: when I(return_hostnames=true)
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.aap_client import (
    AAPClientError,
    client_from_params,
)
from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.auth import AUTH_ARGSPEC
from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.soft_delete import (
    collect_inventory_hostnames,
    soft_delete_stale_host_metrics,
)


def main():
    argument_spec = dict(
        page_size=dict(type="int", default=200),
        soft_delete=dict(type="bool", default=True),
        return_hostnames=dict(type="bool", default=False),
    )
    argument_spec.update(AUTH_ARGSPEC)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not module.params.get("aap_hostname"):
        module.fail_json(msg="aap_hostname (or CONTROLLER_HOST) is required")

    page_size = module.params["page_size"]
    soft_delete = module.params["soft_delete"]
    return_hostnames = module.params["return_hostnames"]
    check_mode = module.check_mode

    client = None
    try:
        client = client_from_params(module.params)
        inventory_hosts = collect_inventory_hostnames(client, page_size)
        result = soft_delete_stale_host_metrics(
            client,
            inventory_hosts,
            page_size,
            soft_delete=soft_delete,
            check_mode=check_mode,
            return_hostnames=return_hostnames,
        )
    except AAPClientError as exc:
        module.fail_json(msg=str(exc))
    finally:
        if client is not None:
            client.cleanup()

    candidate_count = result["candidate_count"]
    soft_deleted_count = result["soft_deleted_count"]
    changed = soft_deleted_count > 0
    if check_mode and soft_delete:
        changed = candidate_count > 0

    exit_result = {
        "changed": changed,
        "inventory_host_count": len(inventory_hosts),
        "metrics_host_count": result["metrics_host_count"],
        "candidate_count": candidate_count,
        "soft_deleted_count": soft_deleted_count,
        "msg": (
            "Soft-deleted {0} host_metrics row(s); {1} candidate(s) from {2} metrics host(s) "
            "vs {3} inventory host(s)".format(
                soft_deleted_count,
                candidate_count,
                result["metrics_host_count"],
                len(inventory_hosts),
            )
        ),
    }
    if return_hostnames:
        exit_result["candidate_hostnames"] = result["candidate_hostnames"]

    module.exit_json(**exit_result)


if __name__ == "__main__":
    main()
