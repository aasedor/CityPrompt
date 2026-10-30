"""The user-selected handoff branch must receive the existing release gates."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    return yaml.load((ROOT / '.github/workflows' / name).read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


class DeploymentWorkflowTargets(unittest.TestCase):
    def test_full_ci_checks_deployment_pull_requests_and_pushes(self):
        triggers = workflow('ci.yml')['on']
        for event in ('push', 'pull_request'):
            self.assertIn('deployment-version', triggers[event]['branches'])

    def test_backend_gate_also_checks_deployment_pushes(self):
        self.assertIn('deployment-version', workflow('backend-tests.yml')['on']['push']['branches'])

    def test_backend_checks_deployment_boundaries_before_other_release_gates(self):
        for filename, job in [('ci.yml', 'backend'), ('backend-tests.yml', 'pytest')]:
            steps = workflow(filename)['jobs'][job]['steps']
            selected = [index for index, step in enumerate(steps)
                        if all(name in step.get('run', '') for name in (
                            'test_deployment_secret_boundaries.py', 'test_compose_data_ports.py'))]
            self.assertEqual(len(selected), 1, filename)
            installation = next(index for index, step in enumerate(steps)
                                if 'pip install -r requirements.txt' in step.get('run', ''))
            migration = next(index for index, step in enumerate(steps)
                             if 'alembic upgrade head' in step.get('run', ''))
            self.assertLess(installation, selected[0], filename)
            self.assertLess(selected[0], migration, filename)
            publication = [index for index, step in enumerate(steps)
                           if 'catalogue_promotion check' in step.get('run', '')]
            for index in publication:
                self.assertLess(selected[0], index, filename)

    def test_manual_asset_verification_defaults_to_the_handoff_branch(self):
        dispatch = workflow('release-assets.yml')['on']['workflow_dispatch']
        self.assertEqual(dispatch['inputs']['ref']['default'], 'deployment-version')

    def test_each_frontend_checkout_restores_its_archive_backed_assets(self):
        jobs = workflow('ci.yml')['jobs']
        for job in ('frontend', 'browser'):
            steps = jobs[job]['steps']
            restoration = [index for index, step in enumerate(steps)
                           if 'python scripts/materialize_frontend_assets.py --fetch-lfs' in step.get('run', '')]
            self.assertEqual(len(restoration), 1, job)
            self.assertEqual(steps[restoration[0]].get('working-directory'), '.')
            execution = next(index for index, step in enumerate(steps)
                             if ('npx vitest run' if job == 'frontend' else 'npm run test:e2e') in step.get('run', ''))
            self.assertLess(restoration[0], execution, job)
