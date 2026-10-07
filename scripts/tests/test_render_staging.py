"""Deployment contracts that prevent missing queues, secrets and asset fallbacks."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class RenderStagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load((ROOT / "render.staging.yaml").read_text())
        cls.services = {s["name"]: s for s in cls.config["services"]}

    def test_staging_does_not_replace_existing_resources_or_auto_deploy(self):
        for service in self.services.values():
            self.assertTrue(service["name"].startswith("cityprompt-staging-"))
            self.assertNotIn("domains", service)
            if service.get("runtime"):
                self.assertEqual(service["autoDeployTrigger"], "off")
        for database in self.config["databases"]:
            self.assertEqual(database["ipAllowList"], [])
        self.assertEqual(self.services["cityprompt-staging-queue"]["maxmemoryPolicy"], "noeviction")

    def test_all_image_document_and_recovery_consumers_exist(self):
        commands = [s.get("dockerCommand", "") for s in self.services.values()]
        for queue in ("direct3d", "direct3d-maintenance", "celery"):
            self.assertTrue(any(f"--queues={queue} " in command for command in commands), queue)
        self.assertEqual(sum("celery_app beat " in command for command in commands), 1)
        api = self.services["cityprompt-staging-api"]
        self.assertEqual(api["preDeployCommand"], "python -m scripts.prepare_database")
        for service in self.services.values():
            if service.get("runtime") == "docker":
                self.assertEqual(service["dockerContext"], ".")

    def test_full_catalogue_profile_and_secrets_are_consistent(self):
        api_vars = {v["key"]: v for v in self.services["cityprompt-staging-api"]["envVars"] if "key" in v}
        self.assertEqual(api_vars["CLASSROOM_RELEASE"]["value"], "false")
        self.assertEqual(api_vars["COMFY_TRIALS_ENABLED"]["value"], "false")
        self.assertEqual(api_vars["RUN_DATABASE_MIGRATIONS"]["value"], "false")
        for key in ("S3_ACCESS_KEY", "S3_SECRET_KEY", "OPENAI_API_KEY", "FAL_KEY", "RENDER_GLOBAL_DAILY_TOKEN_CAP"):
            self.assertIs(api_vars[key]["sync"], False)
        for service in self.services.values():
            if service["type"] == "worker":
                variables = {v["key"]: v for v in service["envVars"]}
                for key in ("DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY", "S3_BUCKET_NAME", "S3_SECRET_KEY", "CLASSROOM_RELEASE"):
                    ref = variables[key]["fromService"]
                    self.assertEqual(ref["name"], "cityprompt-staging-api")
                    self.assertEqual(ref["envVarKey"], key)

    def test_static_build_has_no_private_keys_or_asset_spa_fallback(self):
        frontend = self.services["cityprompt-staging-web"]
        variables = {v["key"]: v for v in frontend["envVars"]}
        self.assertEqual(set(variables), {"NODE_VERSION", "PYTHON_VERSION", "GIT_LFS_SKIP_SMUDGE", "VITE_API_URL", "VITE_GOOGLE_MAPS_API_KEY"})
        self.assertIn("scripts/build_hosted_frontend.py --fetch-lfs", frontend["buildCommand"])
        self.assertNotIn("/*", {r["source"] for r in frontend["routes"]})
        self.assertIn("/projects/*", {r["source"] for r in frontend["routes"]})
        self.assertTrue(any(h["path"] == "/version.json" and h["value"] == "no-store" for h in frontend["headers"]))


if __name__ == "__main__":
    unittest.main()
