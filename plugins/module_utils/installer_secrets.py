# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Read AAP installer crypto secrets from RPM installation paths."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ast

COMPONENT_DEFAULTS = {
    "controller": {
        "become_user": "awx",
        "entries": [
            {
                "var": "secret_key_override",
                "file": "/etc/tower/SECRET_KEY",
            },
        ],
    },
    "gateway": {
        "become_user": "gateway",
        "entries": [
            {
                "var": "gateway_secret_key",
                "file": "/etc/ansible-automation-platform/gateway/SECRET_KEY",
            },
        ],
    },
    "hub": {
        "become_user": "pulp",
        "entries": [
            {
                "var": "hub_secret_key",
                "hub_settings": True,
            },
            {
                "var": "hub_database_fields",
                "file": "/etc/pulp/certs/database_fields.symmetric.key",
                "note": (
                    "RPM: preserve file at /etc/pulp/certs/database_fields.symmetric.key. "
                    "Containerized installer uses podman secret hub_database_fields."
                ),
            },
        ],
    },
    "eda": {
        "become_user": "eda",
        "entries": [
            {
                "var": "eda_secret_key",
                "file": "/etc/ansible-automation-platform/eda/SECRET_KEY",
            },
        ],
    },
}


def read_file_secret(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as handle:
            return handle.read().strip(), None
    except FileNotFoundError:
        return None, "Secret file not found: {0}".format(filepath)
    except PermissionError:
        return None, "Permission denied reading: {0}".format(filepath)


def read_hub_secret_key(settings_file="/etc/pulp/settings.py"):
    try:
        with open(settings_file, "r", encoding="utf-8") as handle:
            content = handle.read()

        for node in ast.walk(ast.parse(content)):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "SECRET_KEY":
                        if isinstance(node.value, ast.Constant):
                            return str(node.value.value), None

        return None, "SECRET_KEY not found as a constant in {0}".format(settings_file)
    except FileNotFoundError:
        return None, "Hub settings file not found: {0}".format(settings_file)
    except (SyntaxError, ValueError) as exc:
        return None, "Failed to parse {0}: {1}".format(settings_file, exc)


def gather_rpm_component_secrets(component):
    defaults = COMPONENT_DEFAULTS.get(component)
    if defaults is None:
        return None, None, ["Unknown component: {0}".format(component)]

    installer_vars = {}
    notes = {}
    warnings = []

    for entry in defaults["entries"]:
        var_name = entry["var"]

        if entry.get("hub_settings"):
            value, err = read_hub_secret_key()
        else:
            value, err = read_file_secret(entry["file"])

        if err:
            warnings.append(err)
            continue

        installer_vars[var_name] = value
        if entry.get("note"):
            notes[var_name] = entry["note"]

    return installer_vars, notes, warnings
