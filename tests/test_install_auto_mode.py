from __future__ import annotations

import json
import subprocess
import sys

import test_builder_installer_runtime as base
from maios_project_kernel import installer


class AutomaticInstallationTests(base.DistributionFixture):
    def preview(self, target, name):
        path = self.base / (name + '.json')
        result = subprocess.run(
            [sys.executable, '-B', str(self.distribution / 'install.py'), 'preview',
             '--target', str(target), '--host', 'opencode', '--plan-out', str(path)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(path.read_text(encoding='utf-8'))

    def test_cli_selects_mode_and_repeats_installation_without_changing_it(self):
        for kind in ('absent', 'empty', 'contains-source-clone'):
            with self.subTest(kind=kind):
                target = self.base / kind
                if kind != 'absent':
                    target.mkdir()
                if kind == 'contains-source-clone':
                    source = target / 'maios-project-kernel'
                    source.mkdir()
                    (source / 'README.md').write_text('Existing source', encoding='utf-8')
                plan = self.preview(target, kind)
                mode = 'existing_repository' if kind == 'contains-source-clone' else 'new_repository'
                self.assertEqual(plan['mode'], mode)
                installer.apply_plan(self.distribution, plan)
                self.assertTrue((target / 'START_HERE.md').is_file())
                self.assertTrue((target / '.opencode').is_dir())
                repeated = self.preview(target, kind + '-again')
                self.assertEqual(repeated['mode'], mode)
                self.assertEqual(repeated['status'], 'idempotent')
                installer.apply_plan(self.distribution, repeated)
                if kind == 'contains-source-clone':
                    self.assertEqual((source / 'README.md').read_text(encoding='utf-8'), 'Existing source')

    def test_auto_preserves_conflicts_and_rejects_changes_after_preview(self):
        target = self.base / 'existing'
        target.mkdir()
        (target / 'AGENTS.md').write_text('Existing instructions', encoding='utf-8')
        plan = installer.make_plan(self.distribution, target, 'auto', 'opencode')
        self.assertEqual(plan['status'], 'blocked')
        with self.assertRaises(installer.InstallerError):
            installer.apply_plan(self.distribution, plan)
        self.assertEqual((target / 'AGENTS.md').read_text(encoding='utf-8'), 'Existing instructions')
        empty = self.base / 'initially-absent'
        plan = self.preview(empty, 'before-change')
        empty.mkdir()
        (empty / 'new-work.txt').write_text('Keep me', encoding='utf-8')
        with self.assertRaises(installer.InstallerError):
            installer.apply_plan(self.distribution, plan)
        self.assertEqual((empty / 'new-work.txt').read_text(encoding='utf-8'), 'Keep me')
        self.assertFalse((empty / '.maios').exists())
