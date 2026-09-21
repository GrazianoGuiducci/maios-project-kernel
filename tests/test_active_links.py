"""Consumer-parsed links, with failure cases independent of the product docs."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_active_links import Document, active_text, check


class ActiveLinkTests(unittest.TestCase):
    def test_active_product_routes(self):
        result = check()
        self.assertTrue(result["valid"], result["errors"])

    def test_markdown_parser_handles_references_code_html_and_duplicate_unicode_headings(self):
        doc = Document('''# Lavoro *utile* e `caffè`
# Lavoro *utile* e `caffè`
[A [nested] label][ref]
![image](image.png)

[ref]: target%20file.md#heading
<a id="explicit" href="other.md">HTML</a>
```
[not a link](missing.md)
```
''')
        self.assertEqual(doc.links, ["target%20file.md#heading", "image.png", "other.md"])
        self.assertEqual(doc.anchors, {"lavoro-utile-e-caffè", "lavoro-utile-e-caffè-1", "explicit"})

    def test_missing_path_and_fragment_fail_but_encoded_path_and_directory_anchor_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target file.md").write_text("# Heading\n", encoding="utf-8")
            (root / "folder").mkdir()
            (root / "folder/README.md").write_text("# Entry\n", encoding="utf-8")
            (root / "source.md").write_text(
                "[ok](target%20file.md#heading) [directory](folder/#entry) "
                "[missing](absent.md) [anchor](target%20file.md#wrong) "
                "[escape](../outside.md)", encoding="utf-8")
            result = check(root, ("source.md",))
            self.assertFalse(result["valid"])
            self.assertEqual(result["local_links"], 5)
            self.assertEqual(len(result["errors"]), 3)
            self.assertTrue(any("missing destination" in e for e in result["errors"]))
            self.assertTrue(any("missing anchor" in e for e in result["errors"]))
            self.assertTrue(any("escapes" in e for e in result["errors"]))

    def test_current_scope_excludes_history_without_confusing_fenced_headings(self):
        text = "# Changelog\n## 5.0.0\n[current](ok.md)\n```\n## fake\n```\n## 4.5.0\n[old](gone.md)\n"
        self.assertEqual(Document(active_text("CHANGELOG.md", text)).links, ["ok.md"])
        text = "# State\n## Current\n[now](ok.md)\n## Earlier states\n[old](gone.md)\n"
        self.assertEqual(Document(active_text("CURRENT_STATE.md", text)).links, ["ok.md"])
