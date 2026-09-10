"""Keep current public entry facts tied to the product's declared contracts."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
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
