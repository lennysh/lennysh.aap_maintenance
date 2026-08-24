# -*- coding: utf-8 -*-
"""Unit tests for host_metrics soft-delete helpers (no live AAP)."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COLLECTIONS_ROOT = os.path.join(tempfile.gettempdir(), "lennysh_aap_maintenance_test_cols")


def _ensure_collection_path():
    dest = os.path.join(COLLECTIONS_ROOT, "ansible_collections", "lennysh", "aap_maintenance")
    if not os.path.islink(dest) and not os.path.exists(dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.symlink(ROOT, dest)
    if COLLECTIONS_ROOT not in sys.path:
        sys.path.insert(0, COLLECTIONS_ROOT)


_ensure_collection_path()

from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.soft_delete import (  # noqa: E402
    normalize_hostname,
    soft_delete_stale_host_metrics,
)


class FakeClient(object):
    def __init__(self, pages):
        self.pages = pages
        self.deleted = []

    def api_path(self, component, endpoint):
        return "/api/controller/v2/{0}/".format(endpoint.strip("/"))

    def iter_pages(self, component, endpoint, query=None):
        key = (component, endpoint)
        for batch in self.pages.get(key, []):
            yield batch

    def delete(self, path):
        self.deleted.append(path)
        return {}


class TestNormalizeHostname(unittest.TestCase):
    def test_lowercase_trim(self):
        self.assertEqual(normalize_hostname("  Host.EXAMPLE  "), "host.example")

    def test_empty(self):
        self.assertIsNone(normalize_hostname(None))
        self.assertIsNone(normalize_hostname(""))

    def test_empty_token_string(self):
        from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.auth import token_value

        self.assertIsNone(token_value(""))
        self.assertIsNone(token_value("   "))
        self.assertEqual(token_value("abc"), "abc")


class TestSoftDeleteStaleHostMetrics(unittest.TestCase):
    def test_deletes_only_absent_hosts(self):
        client = FakeClient(
            {
                ("controller", "host_metrics"): [
                    [
                        {"id": 1, "hostname": "keep-me"},
                        {"id": 2, "hostname": "DELETE-ME"},
                    ],
                    [{"id": 3, "hostname": "also-gone"}],
                ],
            }
        )
        inventory = {"keep-me"}
        result = soft_delete_stale_host_metrics(
            client,
            inventory,
            page_size=200,
            soft_delete=True,
            check_mode=False,
            return_hostnames=True,
        )
        self.assertEqual(result["metrics_host_count"], 3)
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(result["soft_deleted_count"], 2)
        self.assertEqual(sorted(result["candidate_hostnames"]), ["DELETE-ME", "also-gone"])
        self.assertEqual(len(client.deleted), 2)

    def test_check_mode_reports_without_delete(self):
        client = FakeClient(
            {
                ("controller", "host_metrics"): [
                    [{"id": 10, "hostname": "stale"}],
                ],
            }
        )
        result = soft_delete_stale_host_metrics(
            client,
            set(),
            page_size=200,
            soft_delete=True,
            check_mode=True,
            return_hostnames=False,
        )
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["soft_deleted_count"], 0)
        self.assertEqual(client.deleted, [])

    def test_soft_delete_false(self):
        client = FakeClient(
            {
                ("controller", "host_metrics"): [
                    [{"id": 5, "hostname": "stale"}],
                ],
            }
        )
        result = soft_delete_stale_host_metrics(
            client,
            set(),
            page_size=200,
            soft_delete=False,
            check_mode=False,
            return_hostnames=False,
        )
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["soft_deleted_count"], 0)
        self.assertEqual(client.deleted, [])


if __name__ == "__main__":
    unittest.main()
