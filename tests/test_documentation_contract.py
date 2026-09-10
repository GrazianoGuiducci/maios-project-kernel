"""Keep current public entry facts tied to the product's declared contracts."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_reader_routes_reach_their_source_documents(self):
        routes = {
            'README.md': [
                'package/',
                'docs/USAGE.md',
                'docs/GENERATED_KERNEL_BUILD.md',
                'CONTRIBUTING.md',
                '.github/ISSUE_TEMPLATE/evolution-feedback.md',
            ],
            'README.it.md': [
                'package/',
                'docs/USAGE.it.md',
                'docs/GENERATED_KERNEL_BUILD.md',
                'CONTRIBUTING.md',
                '.github/ISSUE_TEMPLATE/evolution-feedback.md',
            ],
            'docs/USAGE.md': ['../README.md'],
            'docs/USAGE.it.md': ['../README.it.md'],
            'CONTRIBUTING.md': [
                'docs/GENERATED_KERNEL_BUILD.md',
                'docs/RENEW_KERNEL_SELECTION.md',
            ],
        }
        for path, destinations in routes.items():
            document = ROOT / path
            links = {url.split('#', 1)[0] for url in re.findall(
                r'\[[^\]]*\]\(([^)]+)\)', document.read_text(encoding='utf-8'))}
            for destination in destinations:
                with self.subTest(path=path, destination=destination):
                    self.assertIn(destination, links)
                    self.assertTrue((document.parent / destination).exists())

    def test_evolution_feedback_keeps_public_submission_owner_gated(self):
        template = (ROOT / '.github/ISSUE_TEMPLATE/evolution-feedback.md').read_text(
            encoding='utf-8'
        )
        contributing = (ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8')
        self.assertIn('operator_approved_public_submission', template)
        self.assertIn('private_data_included: no', template)
        self.assertIn('credentials_or_tokens_included: no', template)
        self.assertIn('permission before publishing', contributing)
        self.assertIn('GitHub Issue', contributing)
        self.assertIn('Pull Request', contributing)
        self.assertIn('seven days', contributing)
        self.assertIn('read-only', contributing)

    def test_native_update_continuity_can_return_feedback_without_claiming_submission(self):
        update = (ROOT / 'kernel/UPDATE_CONTINUITY.md').read_text(encoding='utf-8')
        system = (ROOT / 'skills/maios-project-system/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Return useful experience upstream', update)
        self.assertIn('first meaningful use', update)
        self.assertIn('Evolution Feedback', update)
        self.assertIn('explicit consent', update)
        self.assertIn('GitHub Issue', update)
        self.assertIn('focused Pull Request', update)
        self.assertIn('prepared feedback to the operator instead of claiming submission', update)
        self.assertIn('useful real-world experience can return to the upstream Kernel', system)
        self.assertIn('ask for consent before any external submission', system)
        self.assertIn('Source contact, feedback preparation and public submission remain distinct effects', system)

    def test_current_entry_facts_match_distribution(self):
        manifest = json.loads((ROOT / 'package/MANIFEST.json').read_text(encoding='utf-8'))
        projection = json.loads((ROOT / 'release/PROJECTION.json').read_text(encoding='utf-8'))
        family = json.loads((ROOT / 'kernel/PROJECT_KERNEL_FAMILY_CONTRACT.json').read_text(encoding='utf-8'))
        version_text = (ROOT / 'VERSION.md').read_text(encoding='utf-8')
        version = re.search(r'Product version: `([^`]+)`', version_text).group(1)
        self.assertEqual(version, projection['version'])
        self.assertEqual(version, manifest['version'])
        self.assertEqual(family['family_version'], manifest['project_kernel_family_version'])
        python_min = manifest['runtime_requirements']['python'].removeprefix('>=')
        for path, product_label, family_label, python_suffix in [
            ('README.md', 'Product version', 'Project Kernel family', 'or later'),
            ('README.it.md', 'Versione del prodotto', 'Famiglia Project Kernel', 'o successivo'),
        ]:
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding='utf-8')
                self.assertEqual(re.findall(re.escape(product_label) + r': \*\*\[([^\]]+)\]', text), [version])
                self.assertEqual(re.findall(re.escape(family_label) + r': \*\*([^*]+)\*\*', text), [family['family_version']])
                self.assertIn(f'Python **{python_min} {python_suffix}**', text)
        for path in ['templates/distribution/README.md', 'package/README.md']:
            text = (ROOT / path).read_text(encoding='utf-8')
            self.assertEqual(re.search(r'^# MAIOS Project Kernel ([0-9.]+)', text).group(1), version)
        self.assertEqual((ROOT / 'templates/distribution/README.md').read_bytes(),
                         (ROOT / 'package/README.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
