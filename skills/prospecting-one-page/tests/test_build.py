import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prospecting', ROOT / 'build.py')
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.source = ROOT / 'examples/champions'
        self.site = json.loads((self.source / 'site.json').read_text())

    def test_worked_example_contains_exactly_five_sections_and_no_runtime(self):
        with tempfile.TemporaryDirectory() as d:
            page = module.build(self.source, Path(d) / 'out')
            self.assertEqual(page.count('<section '), 5)
            for section in module.SECTIONS:
                self.assertIn(f'id="{section}"', page)
            self.assertIn('mailto:info@championsgroup.com', page)
            self.assertNotIn('<script', page)
            self.assertIn('noindex,nofollow', page)
            self.assertEqual((Path(d) / 'out/robots.txt').read_text(), 'User-agent: *\nDisallow: /\n')

    def test_missing_each_required_area_refuses(self):
        for section in module.SECTIONS:
            with self.subTest(section=section):
                site = copy.deepcopy(self.site)
                del site[section]
                with self.assertRaises(ValueError):
                    module.validate(site, self.source)

    def test_invalid_trust_boundary_values_refuse(self):
        for key, value in [('domain', 'javascript:alert(1)'), ('domain', 'https://a.example/?x=1'),
                           ('domain', 'https://u:p@a.example'), ('email', 'a@example.com?subject=bad'),
                           ('logo', '../logo.png'), ('logo', '/etc/passwd'),
                           ('name', 'bad\u2014dash'), ('name', '')]:
            with self.subTest(key=key, value=value):
                site = copy.deepcopy(self.site)
                site[key] = value
                with self.assertRaises(ValueError):
                    module.validate(site, self.source)
        for items in ([], None, [{}], [self.site['services']['items'][0]] * 13):
            site = copy.deepcopy(self.site)
            site['services']['items'] = items
            with self.assertRaises(ValueError):
                module.validate(site, self.source)

    def test_copy_escapes_markup_and_template_tokens_are_not_evaluated(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'input'
            source.mkdir()
            (source / 'logo.png').write_bytes((self.source / 'logo.png').read_bytes())
            self.site['overview']['body'] = '<script>alert("x")</script> $name'
            (source / 'site.json').write_text(json.dumps(self.site))
            page = module.build(source, Path(d) / 'out')
            self.assertIn('&lt;script&gt;', page)
            self.assertNotIn('<script>', page)
            self.assertIn('$name', page)

    def test_refusal_does_not_touch_prior_output(self):
        with tempfile.TemporaryDirectory() as d:
            source, out = Path(d) / 'input', Path(d) / 'out'
            source.mkdir()
            out.mkdir()
            target = out / 'index.html'
            target.write_text('previous build')
            (source / 'site.json').write_text('{}')
            with self.assertRaises(ValueError):
                module.build(source, out)
            self.assertEqual(target.read_text(), 'previous build')


if __name__ == '__main__':
    unittest.main()
