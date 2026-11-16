"""Run: python3 -m unittest discover -s skills/refresh-site/tests -v."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
assert spec is not None and spec.loader is not None
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PreferredSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / "site"
        shutil.copytree(ROOT / "examples/emaildatagroup", self.site)
        for file in (ROOT / "templates/verify-skin").iterdir():
            shutil.copy(file, self.site / file.name)
        self.data = json.loads((self.site / "site.json").read_text())

    def build(self, name):
        (self.site / "site.json").write_text(json.dumps(self.data))
        out = self.root / name
        builder.build(self.site, out)
        return {str(p.relative_to(out)): p.read_bytes() for p in out.rglob("*") if p.is_file()}

    def test_disabled_matches_legacy_template_byte_for_byte(self):
        default = self.build("default")
        self.data["preferred_source"] = False
        self.assertEqual(default, self.build("disabled"))
        template = self.site / "template.html"
        template.write_text(template.read_text().replace("{{PREFERRED_SOURCE}}", "").replace("{{PREFERRED_SOURCE_CSS}}", ""))
        self.assertEqual(default, self.build("legacy"))
        self.assertNotIn(b"preferred-source", default["handoff/index.html"])

    def test_enabled_link_is_in_nav_and_markdown(self):
        self.data["preferred_source"] = True
        result = self.build("enabled")
        page = result["handoff/index.html"].decode()
        link, css = builder.preferred_source(self.data)
        self.assertIn(link, page[page.index('<nav class="nav"'):page.index('</nav>')])
        self.assertIn(css, page)
        self.assertIn('target="_blank" rel="noopener noreferrer"', link)
        self.assertIn("Add www.emaildatagroup.net as a preferred source on Google", link)
        self.assertIn("https://www.google.com/preferences/source?q=www.emaildatagroup.net", result["handoff/index.md"].decode())
        self.assertNotIn("{{PREFERRED_SOURCE", page)

    def test_invalid_flag_is_not_treated_as_consent(self):
        for value in ("true", "false", 1, None, {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.preferred_source({"preferred_source": value})

    def test_invalid_domain_rejected(self):
        for domain in ('javascript:alert(1)', 'http://example.com', 'https://example.com/path',
                       'https://user@example.com', 'https://example.com?q=x', 'https://example.com#x',
                       'https://example.com:443', 'https://bad..com', 'https://-bad.com', 'https://bad.com/\"<>'):
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                builder.preferred_source({"preferred_source": True, "domain": domain})

    def test_hostname_and_trailing_slash(self):
        for domain in ('https://example.com', 'https://news.example.com/', 'https://xn--bcher-kva.de'):
            with self.subTest(domain=domain):
                link, _ = builder.preferred_source({"preferred_source": True, "domain": domain})
                host = domain.removeprefix('https://').rstrip('/')
                self.assertIn(f'?q={host}"', link)
                self.assertIn(f'Add {host} as a preferred source on Google', link)

    def test_enabled_legacy_template_fails_actionably(self):
        self.data["preferred_source"] = True
        template = self.site / "template.html"
        for slot in ('{{PREFERRED_SOURCE}}', '{{PREFERRED_SOURCE_CSS}}'):
            original = template.read_text()
            template.write_text(original.replace(slot, ""))
            with self.subTest(slot=slot), self.assertRaisesRegex(ValueError, "Add.*PREFERRED_SOURCE"):
                self.build("invalid")
            template.write_text(original)


if __name__ == "__main__":
    unittest.main()
