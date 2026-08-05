# Operations runbook

## Preflight

1. Run `./scripts/validate.sh` from a clean clone.
2. Review the request tenant, target, action `plan_aks_kms_keyvault_provider`, and approval evidence.
3. Confirm workload federation, least-privilege Azure roles, private DNS, quotas,
   retention, budgets, and regional support in a disposable environment.
4. Compile and review `infra/main.bicep`; keep `deployPlatform=false` until change approval.

## Deployment and observation

Use a synthetic tenant and a dedicated resource group. Preserve the canonical
plan and deployment correlation ID. Monitor adapter retries, denial rate,
provider throttling, evidence delivery, latency, and cost. Never log tokens,
request bodies containing personal data, or provider credentials.

## Failure and rollback

The planner fails closed. On adapter failure, stop retries after a bounded
attempt count, retain sanitized evidence, and alert the owner. Roll back the
service-specific desired state using the approved pre-change snapshot; do not
delete evidence under retention. Break-glass use requires two-person review and
a retrospective.

## Teardown

Disable triggers, drain in-flight work, revoke federated role assignments,
export required evidence, remove project resources only after retention and
dependency checks, then verify no private endpoints, DNS records, identities,
or cost-bearing resources remain.
