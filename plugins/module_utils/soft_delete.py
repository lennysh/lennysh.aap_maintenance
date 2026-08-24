# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Stream host_metrics soft-delete logic (hosts not present in any inventory)."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def normalize_hostname(hostname):
    if not hostname:
        return None
    return str(hostname).lower().strip()


def collect_inventory_hostnames(client, page_size):
    """Paginate controller hosts and return a lowercase hostname set."""
    inventory_hosts = set()
    for batch in client.iter_pages("controller", "hosts", query={"page_size": page_size}):
        for host in batch:
            key = normalize_hostname(host.get("name"))
            if key:
                inventory_hosts.add(key)
    return inventory_hosts


def soft_delete_stale_host_metrics(
    client,
    inventory_hosts,
    page_size,
    soft_delete=True,
    check_mode=False,
    return_hostnames=False,
):
    """
    Find host_metrics rows (deleted=false) whose hostname is absent from inventory_hosts.

    Pages through host_metrics without storing every metrics hostname in memory.
    Only candidate hostnames (and optional return list) are retained.
    """
    metrics_host_count = 0
    candidate_count = 0
    soft_deleted_count = 0
    candidate_hostnames = []

    metrics_path = client.api_path("controller", "host_metrics")
    query = {"page_size": page_size, "deleted": False}

    for batch in client.iter_pages("controller", "host_metrics", query=query):
        for metric in batch:
            metrics_host_count += 1
            hostname = metric.get("hostname")
            key = normalize_hostname(hostname)
            if not key or key in inventory_hosts:
                continue
            metric_id = metric.get("id")
            if metric_id is None:
                continue
            candidate_count += 1
            if return_hostnames:
                candidate_hostnames.append(hostname)
            if soft_delete and not check_mode:
                delete_path = "{0}{1}/".format(metrics_path.rstrip("/"), metric_id)
                client.delete(delete_path)
                soft_deleted_count += 1

    return {
        "metrics_host_count": metrics_host_count,
        "candidate_count": candidate_count,
        "soft_deleted_count": soft_deleted_count,
        "candidate_hostnames": candidate_hostnames,
    }
