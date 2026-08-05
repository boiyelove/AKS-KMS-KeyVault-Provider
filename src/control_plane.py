#!/usr/bin/env python3
"""Fail-closed desired-state planner shared only within this repository."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RejectedRequest(ValueError):
    """A request failed one or more security invariants."""

    def __init__(self, violations: list[str]):
        super().__init__("; ".join(violations))
        self.violations = violations


@dataclass(frozen=True)
class Policy:
    project: str
    rank: int
    action: str
    allowed_credential_modes: tuple[str, ...]
    protected_targets: tuple[str, ...]
    allowed_tenant_ids: tuple[str, ...]

    @classmethod
    def load(cls, path: Path) -> "Policy":
        raw = json.loads(path.read_text())
        required = {
            "project", "rank", "action", "allowedCredentialModes",
            "protectedTargets", "allowedTenantIds",
        }
        missing = sorted(required - raw.keys())
        if missing:
            raise ValueError(f"policy missing keys: {', '.join(missing)}")
        return cls(
            project=str(raw["project"]),
            rank=int(raw["rank"]),
            action=str(raw["action"]),
            allowed_credential_modes=tuple(raw["allowedCredentialModes"]),
            protected_targets=tuple(raw["protectedTargets"]),
            allowed_tenant_ids=tuple(raw["allowedTenantIds"]),
        )


def canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def contains_sensitive_value(value: Any) -> bool:
    """Detect common credential-shaped fields without inspecting free-form text."""
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = key.lower().replace("_", "").replace("-", "")
            if normalized in {"password", "token", "accesstoken", "refreshtoken", "clientsecret", "apikey"} and nested:
                return True
            if contains_sensitive_value(nested):
                return True
    if isinstance(value, list):
        return any(contains_sensitive_value(item) for item in value)
    return False


def plan(request: dict[str, Any], policy: Policy) -> dict[str, Any]:
    """Validate an adapter-neutral request and return an idempotent plan."""
    violations: list[str] = []
    required = ("tenantId", "correlationId", "target", "requestedAction", "credentialMode")
    for key in required:
        if not isinstance(request.get(key), str) or not request[key].strip():
            violations.append(f"{key} is required")
    if request.get("requestedAction") != policy.action:
        violations.append("requestedAction is not allow-listed")
    if request.get("tenantId") not in policy.allowed_tenant_ids:
        violations.append("tenantId is not allow-listed")
    if request.get("credentialMode") not in policy.allowed_credential_modes:
        violations.append("credentialMode must be secretless")
    if request.get("publicNetworkAccess") is not False:
        violations.append("publicNetworkAccess must be false")
    if request.get("evidenceFresh") is not True:
        violations.append("fresh evidence is required")
    if request.get("target") in policy.protected_targets and request.get("approved") is not True:
        violations.append("protected target requires explicit approval")
    if request.get("containsSecret") is True:
        violations.append("embedded credentials are forbidden")
    if contains_sensitive_value(request):
        violations.append("credential-shaped fields are forbidden")
    if violations:
        raise RejectedRequest(sorted(set(violations)))

    material = {
        "project": policy.project,
        "tenantId": request["tenantId"],
        "correlationId": request["correlationId"],
        "target": request["target"],
        "action": policy.action,
    }
    return {
        "schemaVersion": "1.0",
        "decision": "approved",
        "project": policy.project,
        "rank": policy.rank,
        "action": policy.action,
        "target": request["target"],
        "tenantId": request["tenantId"],
        "correlationId": request["correlationId"],
        "idempotencyKey": hashlib.sha256(canonical(material).encode()).hexdigest(),
        "adapterExecutionRequired": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and plan a guarded project action")
    parser.add_argument("--policy", type=Path, default=Path("config/policy.json"))
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    policy = Policy.load(args.policy)
    request = json.loads(args.request.read_text())
    try:
        result = plan(request, policy)
    except RejectedRequest as exc:
        print(canonical({"decision": "denied", "violations": exc.violations}))
        return 2
    print(canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
