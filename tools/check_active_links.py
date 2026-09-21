#!/usr/bin/env python3
"""Check local links and GitHub-style anchors in active release documents.

Source-test dependencies live in requirements-test.txt, outside the runtime.
External URLs and cold historical outbound routes are intentionally not checked.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DOCUMENTS = (
    "README.md", "README.it.md", "VERSION.md", "CURRENT_STATE.md", "CHANGELOG.md",
    "AGENTS.md", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md", "TRADEMARKS.md",
    "docs/README.md", "docs/INSTALLATION.md", "docs/USAGE.md", "docs/USAGE.it.md",
    "docs/COMPATIBILITY.md", "docs/GENERATED_KERNEL_BUILD.md", "docs/RELEASE_5.0.0.md",
    "docs/PROVENANCE.md", "docs/ARCHITECTURE.md", "docs/RECEIPTS.md",
    "docs/INSTANCE_COORDINATION.md", "kernel/UPDATE_CONTINUITY.md",
    "package/README.md", "package/INSTALL.md", "package/AGENTS.md",
    "package/payload/START_HERE.md", "package/payload/HOSTS.md", "package/payload/AGENTS.md",
)


class Document(HTMLParser):
    def __init__(self, markdown: str):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.anchors: set[str] = set()
        self.heading_ids: set[str] = set()
        self.heading: list[str] | None = None
        self.feed(MarkdownIt("commonmark").enable("table").render(markdown))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.links.append(attrs[attribute] or "")
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.heading = []
        if self.heading is not None and tag == "img":
            self.heading.append(attrs.get("alt", ""))

    def handle_data(self, data):
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.heading is not None:
            # GitHub heading IDs preserve Unicode word characters, hyphens and
            # spaces; punctuation is removed and spaces become hyphens. Work
            # from parsed visible text, not Markdown source or a link regex.
            text = "".join(self.heading).lower()
            base = "".join(c for c in text if c in " -" or
                           unicodedata.category(c)[0] in "LMN" or
                           unicodedata.category(c) == "Pc").replace(" ", "-")
            slug, count = base, 0
            while slug in self.heading_ids:
                count += 1
                slug = f"{base}-{count}"
            self.heading_ids.add(slug)
            self.anchors.add(slug)
            self.heading = None


def active_text(relative: str, text: str) -> str:
    """Use parsed heading boundaries, ignoring apparent headings in code fences."""
    tokens = MarkdownIt("commonmark").parse(text)
    headings = [t for t in tokens if t.type == "heading_open" and t.tag == "h2"]
    cutoff = None
    if relative == "CHANGELOG.md" and len(headings) > 1:
        cutoff = headings[1].map[0]
    if relative == "CURRENT_STATE.md":
        for i, token in enumerate(tokens):
            if token.type == "heading_open" and tokens[i + 1].content == "Earlier states":
                cutoff = token.map[0]
                break
    return text if cutoff is None else "\n".join(text.splitlines()[:cutoff])


def check(root: Path = ROOT, documents=ACTIVE_DOCUMENTS) -> dict:
    root = root.resolve()
    errors = []
    checked = 0
    target_cache = {}
    for relative in documents:
        source = root / relative
        if not source.is_file():
            errors.append(f"{relative}: active document missing")
            continue
        document = Document(active_text(relative, source.read_text(encoding="utf-8")))
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            checked += 1
            path = unquote(url.path)
            target = (root / path.lstrip("/") if path.startswith("/") else source.parent / path) if path else source
            target = target.resolve()
            label = f"{relative}: {link}"
            if not target.is_relative_to(root):
                errors.append(label + " escapes document root")
                continue
            if not target.exists():
                errors.append(label + " missing destination")
                continue
            fragment = unquote(url.fragment)
            if not fragment:
                continue
            if target.is_dir():
                target = target / "README.md"
            if not target.is_file():
                errors.append(label + " missing document for anchor")
                continue
            if target.suffix.lower() not in (".md", ".markdown", ".html"):
                errors.append(label + " unsupported anchor target")
                continue
            if target not in target_cache:
                target_cache[target] = Document(target.read_text(encoding="utf-8")).anchors
            if fragment not in target_cache[target]:
                errors.append(label + " missing anchor")
    return {"valid": not errors, "documents": len(documents), "local_links": checked,
            "scope": "active release documents; external URLs and historical outbound links excluded",
            "errors": errors}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)
