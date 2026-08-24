# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Lenny Shirley (@lennysh)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Minimal HTTP client for AAP Gateway / Controller APIs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
import json

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode, urlparse
from ansible.module_utils.urls import open_url

from ansible_collections.lennysh.aap_maintenance.plugins.module_utils.auth import token_value

API_PREFIX = {
    "gateway": "/api/gateway/v1",
    "controller": "/api/controller/v2",
}


class AAPClientError(Exception):
    def __init__(self, message, status=None, body=None):
        super(AAPClientError, self).__init__(message)
        self.status = status
        self.body = body


class AAPClient(object):
    """REST client for an AAP 2.5+ gateway host."""

    def __init__(
        self,
        hostname,
        username=None,
        password=None,
        token=None,
        validate_certs=True,
        request_timeout=30.0,
    ):
        if not hostname:
            raise AAPClientError("aap_hostname is required")
        self.base = hostname.rstrip("/")
        if not self.base.startswith("http"):
            self.base = "https://{0}".format(self.base)
        self.username = username
        self.password = password
        self.token = token_value(token)
        self.validate_certs = validate_certs
        self.request_timeout = request_timeout
        self._managed_token_id = None
        self._token_managed = False

    def __enter__(self):
        self.ensure_token()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def ensure_token(self, description="lennysh.aap_maintenance", scope="write"):
        if self.token:
            return False
        if not (self.username and self.password):
            raise AAPClientError("Provide aap_token or aap_username/aap_password")
        payload = {"description": description, "scope": scope}
        created = self.post(self.api_path("gateway", "tokens"), payload)
        token_str = None
        token_id = None
        if isinstance(created, dict):
            token_str = created.get("token") or created.get("access_token")
            token_id = created.get("id")
        if not token_str:
            raise AAPClientError(
                "Gateway token create succeeded but response had no token value: {0!r}".format(created)
            )
        self.token = token_str
        self._managed_token_id = token_id
        self._token_managed = True
        return True

    def cleanup(self):
        if not self._token_managed or self._managed_token_id is None:
            self._token_managed = False
            self._managed_token_id = None
            return
        path = "{0}{1}/".format(self.api_path("gateway", "tokens"), self._managed_token_id)
        try:
            self.delete(path)
        except AAPClientError:
            pass
        finally:
            self._token_managed = False
            self._managed_token_id = None

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = "Bearer {0}".format(self.token)
        elif self.username and self.password:
            basic = base64.b64encode(
                "{0}:{1}".format(self.username, self.password).encode("utf-8")
            ).decode("ascii")
            headers["Authorization"] = "Basic {0}".format(basic)
        else:
            raise AAPClientError("Provide aap_token or aap_username/aap_password")
        return headers

    def request(self, method, path, query=None, data=None):
        url = path if path.startswith("http") else "{0}{1}".format(self.base, path)
        if query:
            url = "{0}?{1}".format(url, urlencode(query, doseq=True))
        body = None
        if data is not None:
            body = json.dumps(data)
        try:
            resp = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                validate_certs=self.validate_certs,
                timeout=self.request_timeout,
            )
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))
        except HTTPError as exc:
            err_body = exc.read()
            try:
                parsed = json.loads(err_body.decode("utf-8"))
            except Exception:
                parsed = err_body.decode("utf-8", errors="replace")
            raise AAPClientError(
                "HTTP {0} for {1} {2}: {3}".format(exc.code, method, url, parsed),
                status=exc.code,
                body=parsed,
            )
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise AAPClientError(
                "Failed to reach {0} ({1}): {2}. "
                "Check aap_hostname, network/VPN access, firewall rules, and "
                "aap_request_timeout (currently {3}s).".format(
                    url, method, reason, self.request_timeout
                )
            )

    def get(self, path, query=None):
        return self.request("GET", path, query=query)

    def post(self, path, data):
        return self.request("POST", path, data=data)

    def delete(self, path):
        return self.request("DELETE", path)

    def api_path(self, component, endpoint):
        prefix = API_PREFIX[component]
        endpoint = endpoint.strip("/")
        return "{0}/{1}/".format(prefix, endpoint)

    def iter_pages(self, component, endpoint, query=None):
        """Yield one API page (list of objects) at a time without accumulating."""
        query = dict(query or {})
        page_size = query.setdefault("page_size", 200)
        query.setdefault("limit", page_size)
        path = self.api_path(component, endpoint)
        next_url = None
        first = True
        while True:
            if first:
                payload = self.get(path, query=query)
                first = False
            else:
                payload = self.get(next_url)
            if isinstance(payload, list):
                if payload:
                    yield payload
                break
            batch = payload.get("results")
            if batch is None:
                batch = payload.get("data") or []
            if batch:
                yield batch
            next_url = payload.get("next")
            if not next_url:
                links = payload.get("links") or {}
                next_url = links.get("next")
            if not next_url:
                break
            if next_url.startswith("http"):
                pass
            elif next_url.startswith("/"):
                next_url = "{0}{1}".format(self.base, next_url)
            else:
                next_url = "{0}/{1}".format(self.base, next_url)


def client_from_params(params, ensure_token=True):
    client = AAPClient(
        hostname=params.get("aap_hostname"),
        username=params.get("aap_username"),
        password=params.get("aap_password"),
        token=params.get("aap_token"),
        validate_certs=params.get("aap_validate_certs"),
        request_timeout=params.get("aap_request_timeout"),
    )
    if ensure_token:
        client.ensure_token()
    return client
