"""Consumer checks for the finite teaching evidence boundary."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / 'reviewed-inputs'


class TeachingBuildTests(unittest.TestCase):
    def run_build(self, directory, inventory=None, audit=None):
        directory = Path(directory)
        audit_path = INPUTS / 'audit.json'
        inventory_path = INPUTS / 'inventory.json'
        if audit is not None:
            audit_path = directory / 'audit.json'
            audit_path.write_text(json.dumps(audit), encoding='utf-8')
        if inventory is not None:
            inventory_path = directory / 'inventory.json'
            inventory_path.write_text(json.dumps(inventory), encoding='utf-8')
        output = directory / 'output.json'
        result = subprocess.run([sys.executable, str(ROOT / 'build_data.py'),
            '--audit', str(audit_path), '--inventory', str(inventory_path),
            '--output', str(output)], capture_output=True, text=True)
        return result, output

    def test_reviewed_pair_builds_the_same_lessons(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output = self.run_build(directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = json.loads((ROOT.parents[1] / 'frontend/src/data/catalogueTeaching.json').read_text(encoding='utf-8'))
            actual = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(actual['lessons'], expected['lessons'])
            self.assertEqual(actual['styles'], expected['styles'])
            self.assertEqual(actual['planning'], expected['planning'])

    def test_old_audit_cannot_be_bound_to_a_changed_contract(self):
        original = json.loads((INPUTS / 'inventory.json').read_text(encoding='utf-8'))
        for change in ('revision', 'method', 'domain', 'archetype', 'variant'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                inventory = json.loads(json.dumps(original))
                choice = inventory['choices'][0]
                if change in ('revision', 'method'):
                    choice['placements'][0]['model'][change] = 'unreviewed-change'
                elif change == 'variant':
                    choice['placements'][0]['model']['variantId'] = 'unreviewed-variant'
                elif change == 'archetype':
                    choice['option']['id'] = 'unreviewed-archetype'
                else:
                    choice['domain'] = 'park_plaza'
                result, output = self.run_build(directory, inventory=inventory)
                self.assertNotEqual(result.returncode, 0, 'Changed evidence was accepted')
                self.assertIn('reviewed evidence', result.stderr)
                self.assertFalse(output.exists())

    def test_changed_audit_needs_a_new_review(self):
        audit = json.loads((INPUTS / 'audit.json').read_text(encoding='utf-8'))
        audit['choices'][0]['proposed_style_ids'] = ['neoclassical']
        with tempfile.TemporaryDirectory() as directory:
            result, output = self.run_build(directory, audit=audit)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('reviewed evidence', result.stderr)
            self.assertFalse(output.exists())

    def test_git_preserves_the_hash_bound_snapshot_bytes(self):
        repository = ROOT.parents[1]
        for name in ('audit.json', 'inventory.json'):
            with self.subTest(name=name):
                path = INPUTS / name
                data = path.read_bytes()
                raw = subprocess.run(['git', 'hash-object', '--no-filters', '--stdin'],
                    cwd=repository, input=data, capture_output=True, check=True).stdout
                filtered = subprocess.run(['git', '-c', 'core.autocrlf=true', 'hash-object',
                    '--path', path.relative_to(repository).as_posix(), '--stdin'],
                    cwd=repository, input=data, capture_output=True, check=True).stdout
                self.assertEqual(filtered, raw, 'Git would change the reviewed bytes on checkout')


if __name__ == '__main__':
    unittest.main()
