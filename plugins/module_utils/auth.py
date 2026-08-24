# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared AAP authentication argument spec for maintenance modules."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback


AUTH_ARGSPEC = dict(
    aap_hostname=dict(
        type="str",
        required=False,
        aliases=["controller_host", "tower_host", "gateway_hostname"],
        fallback=(env_fallback, ["AAP_HOSTNAME", "CONTROLLER_HOST", "TOWER_HOST"]),
    ),
    aap_username=dict(
        type="str",
        required=False,
        aliases=["controller_username", "tower_username", "gateway_username"],
        fallback=(env_fallback, ["AAP_USERNAME", "CONTROLLER_USERNAME", "TOWER_USERNAME"]),
    ),
    aap_password=dict(
        type="str",
        required=False,
        no_log=True,
        aliases=["controller_password", "tower_password", "gateway_password"],
        fallback=(env_fallback, ["AAP_PASSWORD", "CONTROLLER_PASSWORD", "TOWER_PASSWORD"]),
    ),
    aap_token=dict(
        type="raw",
        required=False,
        no_log=True,
        aliases=["controller_oauthtoken", "gateway_token", "aap_oauthtoken"],
        fallback=(env_fallback, ["AAP_TOKEN", "CONTROLLER_OAUTH_TOKEN", "TOWER_OAUTH_TOKEN"]),
    ),
    aap_validate_certs=dict(
        type="bool",
        required=False,
        default=True,
        aliases=["validate_certs", "tower_verify_ssl"],
        fallback=(env_fallback, ["AAP_VALIDATE_CERTS", "CONTROLLER_VERIFY_SSL", "TOWER_VERIFY_SSL"]),
    ),
    aap_request_timeout=dict(
        type="float",
        required=False,
        default=30.0,
        aliases=["request_timeout"],
        fallback=(env_fallback, ["AAP_REQUEST_TIMEOUT", "CONTROLLER_REQUEST_TIMEOUT"]),
    ),
)


def token_value(raw):
    """Normalize token dict or string to a bearer token string."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw.get("token") or raw.get("access_token")
    return raw
