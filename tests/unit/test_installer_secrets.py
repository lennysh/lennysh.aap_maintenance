#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULE_UTILS = _REPO_ROOT / "plugins" / "module_utils" / "installer_secrets.py"
_spec = importlib.util.spec_from_file_location("installer_secrets", _MODULE_UTILS)
installer_secrets = importlib.util.module_from_spec(_spec)
sys.modules["installer_secrets"] = installer_secrets
_spec.loader.exec_module(installer_secrets)


class TestInstallerSecretsGather(unittest.TestCase):
    def test_read_file_secret(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write("super-secret\n")
            path = handle.name

        value, err = installer_secrets.read_file_secret(path)
        self.assertIsNone(err)
        self.assertEqual(value, "super-secret")

    def test_read_hub_secret_key(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write('SECRET_KEY = "hub-django-key"\n')
            path = handle.name

        value, err = installer_secrets.read_hub_secret_key(path)
        self.assertIsNone(err)
        self.assertEqual(value, "hub-django-key")

    def test_gather_controller_maps_secret_key_override(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write("controller-key")
            path = handle.name

        original = installer_secrets.COMPONENT_DEFAULTS["controller"]["entries"][0]["file"]
        installer_secrets.COMPONENT_DEFAULTS["controller"]["entries"][0]["file"] = path
        try:
            installer_vars, notes, warnings = installer_secrets.gather_rpm_component_secrets(
                "controller"
            )
        finally:
            installer_secrets.COMPONENT_DEFAULTS["controller"]["entries"][0]["file"] = original

        self.assertEqual(installer_vars["secret_key_override"], "controller-key")
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
