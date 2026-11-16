"""Run: python3 -m unittest discover -s skills/refresh-site/tests -v."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def test_search_hints_are_interpolated(self):
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp) / "site"
            shutil.copytree(ROOT / "examples/emaildatagroup", site)
            for file in (ROOT / "templates/verify-skin").iterdir():
                shutil.copy(file, site / file.name)
            out = Path(temp) / "dist"
            subprocess.run([sys.executable, str(ROOT / "scripts/build_site.py"), str(site), "--out", str(out)], check=True)
            for page in out.rglob("*.html"):
                with self.subTest(page=page.relative_to(out)):
                    self.assertNotIn("{E(", page.read_text())


if __name__ == "__main__":
    unittest.main()
