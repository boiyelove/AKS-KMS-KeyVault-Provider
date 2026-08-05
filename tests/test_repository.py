import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_goal_is_ignored(self):
        self.assertIn("goal.md", (ROOT / ".gitignore").read_text().splitlines())

    def test_policy_matches_readme(self):
        policy = json.loads((ROOT / "config/policy.json").read_text())
        readme = (ROOT / "README.md").read_text()
        self.assertIn(policy["project"], readme)
        self.assertIn(f"Portfolio rank: **{policy['rank']}**", readme)

    def test_iac_defaults_to_no_deployment(self):
        bicep = (ROOT / "infra/main.bicep").read_text()
        self.assertIn("param deployPlatform bool = false", bicep)
        self.assertIn("publicNetworkAccess: 'Disabled'", bicep)

    def test_ci_uses_minimum_permissions(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("contents: read", workflow)
        self.assertNotIn("pull-requests: write", workflow)


if __name__ == "__main__":
    unittest.main()
