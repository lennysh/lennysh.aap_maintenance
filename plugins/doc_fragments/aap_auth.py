# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  aap_hostname:
    description: URL / hostname of the AAP Gateway.
    type: str
    aliases: [controller_host, tower_host, gateway_hostname]
  aap_username:
    description:
      - Username used to mint a short-lived gateway token when I(aap_token) is unset.
    type: str
    aliases: [controller_username, tower_username, gateway_username]
  aap_password:
    description:
      - Password used with I(aap_username) to mint a gateway token when I(aap_token) is unset.
    type: str
    aliases: [controller_password, tower_password, gateway_password]
  aap_token:
    description:
      - OAuth2 / gateway token string, or a dict with a C(token) (or C(access_token)) key.
      - Prefer a token for API calls. When unset, modules mint a short-lived
        gateway token from I(aap_username)/I(aap_password) and revoke it when done.
    type: raw
    aliases: [controller_oauthtoken, gateway_token, aap_oauthtoken]
  aap_validate_certs:
    description: Validate TLS certificates.
    type: bool
    default: true
    aliases: [validate_certs, tower_verify_ssl]
  aap_request_timeout:
    description:
      - HTTP timeout in seconds for connect and response read.
      - Increase for large inventories when list API pages are slow to return.
    type: float
    default: 30.0
    aliases: [request_timeout]
"""
