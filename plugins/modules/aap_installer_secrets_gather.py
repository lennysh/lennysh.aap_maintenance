#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: aap_installer_secrets_gather
short_description: Read installer crypto secrets from an RPM AAP component host
description:
  - Reads Django SECRET_KEY files and Hub encryption keys from a running RPM install.
  - Returns plain-text values keyed by installer inventory variable names suitable
    for export to a vars file (for example C(secret_key_override) on controller).
version_added: "0.1.0"
author: Lenny Shirley (@lennysh)
options:
  component:
    description: AAP component to read secrets from on this host.
    required: true
    type: str
    choices: [controller, gateway, hub, eda]
notes:
  - Must run on the RPM host where the component is installed with appropriate become user.
  - Callers MUST use C(no_log=true) on the task.
"""

EXAMPLES = r"""
- name: Read controller SECRET_KEY for export
  lennysh.aap_maintenance.aap_installer_secrets_gather:
    component: controller
  become: true
  become_user: awx
  register: controller_secrets
  no_log: true
"""

RETURN = r"""
installer_vars:
  description: Plain-text secret values keyed by installer variable name.
  returned: success
  type: dict
notes:
  description: Optional per-variable guidance when no standard inventory var exists.
  returned: when notes are available
  type: dict
warnings:
  description: Non-fatal read issues (missing files, parse errors).
  returned: when warnings are present
  type: list
  elements: str
component:
  description: Component that was queried.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.installer_secrets import (
    COMPONENT_DEFAULTS,
    gather_rpm_component_secrets,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            component=dict(
                type="str",
                required=True,
                choices=sorted(COMPONENT_DEFAULTS.keys()),
            ),
        ),
        supports_check_mode=True,
    )

    component = module.params["component"]
    installer_vars, notes, warnings = gather_rpm_component_secrets(component)

    if not installer_vars and warnings:
        module.fail_json(
            msg="No secrets gathered for {0}: {1}".format(
                component, "; ".join(warnings)
            ),
            component=component,
            warnings=warnings,
        )

    result = {
        "changed": False,
        "component": component,
        "installer_vars": installer_vars,
    }
    if notes:
        result["notes"] = notes
    if warnings:
        result["warnings"] = warnings

    module.exit_json(**result)


if __name__ == "__main__":
    main()
