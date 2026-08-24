# Collections Plugins Directory

## Modules

- `soft_delete_hosts` — paginate controller inventories and `host_metrics`, then
  soft-delete metrics rows whose hostname is not in any inventory.

## module_utils

- `aap_client` — minimal gateway/controller REST client with page streaming
- `soft_delete` — inventory vs host_metrics comparison logic
- `auth` — shared `aap_*` authentication argument spec
