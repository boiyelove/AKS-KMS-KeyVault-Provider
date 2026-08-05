import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from control_plane import Policy, RejectedRequest, plan


class ControlPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = Policy.load(ROOT / "config/policy.json")
        cls.base = json.loads((ROOT / "examples/approved-request.json").read_text())

    def test_approved_request_is_deterministic(self):
        self.assertEqual(plan(self.base, self.policy), plan(self.base, self.policy))

    def test_project_action_is_tailored(self):
        result = plan(self.base, self.policy)
        self.assertEqual(self.policy.action, result["action"])
        self.assertTrue(result["adapterExecutionRequired"])

    def test_public_access_is_denied(self):
        request = self.base | {"publicNetworkAccess": True}
        with self.assertRaises(RejectedRequest):
            plan(request, self.policy)

    def test_secrets_are_denied(self):
        request = self.base | {"containsSecret": True}
        with self.assertRaises(RejectedRequest):
            plan(request, self.policy)

    def test_stale_evidence_is_denied(self):
        request = self.base | {"evidenceFresh": False}
        with self.assertRaises(RejectedRequest):
            plan(request, self.policy)

    def test_unknown_action_is_denied(self):
        request = self.base | {"requestedAction": "delete_everything"}
        with self.assertRaises(RejectedRequest):
            plan(request, self.policy)

    def test_production_requires_approval(self):
        request = self.base | {"target": "production", "approved": False}
        with self.assertRaises(RejectedRequest):
            plan(request, self.policy)

    def test_cross_tenant_request_is_denied(self):
        with self.assertRaises(RejectedRequest):
            plan(self.base | {"tenantId": "tenant-b"}, self.policy)

    def test_credential_shaped_field_is_denied(self):
        with self.assertRaises(RejectedRequest):
            plan(self.base | {"clientSecret": "not-a-real-secret"}, self.policy)


if __name__ == "__main__":
    unittest.main()
