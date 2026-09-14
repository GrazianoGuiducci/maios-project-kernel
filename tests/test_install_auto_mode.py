from __future__ import annotations

import json
import subprocess
import sys
from unittest.mock import patch

import test_builder_installer_runtime as base
from maios_project_kernel import installer


class AutomaticInstallationTests(base.DistributionFixture):
    def test_install_into_the_coders_empty_working_directory(self):
        target = self.base / 'active-workspace'
        target.mkdir()
        identity = target.stat().st_ino
        plan = self.preview(target, 'active-workspace-plan')
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', '-B', str(self.distribution / 'install.py'), 'apply',
             '--plan', str(self.base / 'active-workspace-plan.json')],
            cwd=target, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(target.stat().st_ino, identity)
        receipt = installer.current_receipt(target)
        self.assertEqual(receipt['mode'], 'new_repository')
        self.assertTrue(installer.verify_installation(target, receipt)['valid'])
        repeated = self.preview(target, 'active-workspace-repeated')
        self.assertEqual(repeated['status'], 'idempotent')
        self.assertEqual(repeated['mode'], plan['mode'])

    def test_empty_directory_recovers_partial_install_without_losing_new_work(self):
        target = (self.base / 'interrupted-empty').resolve()
        target.mkdir()
        identity = target.stat().st_ino
        plan = installer.make_plan(self.distribution, target, 'auto', 'opencode')
        real_copy = installer.copy_entry
        copied = []

        def interrupted_copy(root, receiving, entry):
            if copied:
                (target / 'operator-note.txt').write_bytes(b'Keep this new work')
                raise OSError('interrupted installation')
            record = real_copy(root, receiving, entry)
            copied.append(entry['destination'])
            return record

        with patch.object(installer, 'copy_entry', side_effect=interrupted_copy):
            with self.assertRaisesRegex(OSError, 'interrupted installation'):
                installer.apply_plan(self.distribution, plan)
        self.assertEqual(target.stat().st_ino, identity)
        self.assertEqual((target / 'operator-note.txt').read_bytes(), b'Keep this new work')
        self.assertFalse((target / copied[0]).exists())
        self.assertFalse((target / '.maios/receipts/install/PENDING.json').exists())
        self.assertIsNone(installer.current_receipt(target))

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
