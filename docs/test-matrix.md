# Test matrix

| Scenario | Local evidence | Azure/integration evidence |
|---|---|---|
| Valid synthetic request | Approved deterministic plan | Adapter performs intended action |
| Missing tenant or correlation | Denied | Token tenant also verified |
| Public access requested | Denied | Private endpoint reachability proven |
| Embedded or long-lived secret | Denied | Federated identity and least privilege proven |
| Stale evidence | Denied | Source timestamp/signature verified |
| Unknown action | Denied | Provider refuses unsupported mutation |
| Production without approval | Denied | Approval authority and PIM evidence captured |
| Identical replay | Same idempotency key | Exactly-once reconciliation demonstrated |
| Dependency/provider outage | N/A | Bounded retry and observable failure drill |
| Teardown | Documentation check | Resource and cost inventory reaches zero |

Project-specific scenarios to add to an isolated Azure test environment:
Test per-workload authorization, forbidden namespace access, initial mount, automated rotation, pod restart, Key Vault outage/throttling, revoked identity, synced-secret cleanup, and audit visibility.
