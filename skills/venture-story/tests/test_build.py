import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('venture_build',ROOT/'build.py')
assert spec is not None and spec.loader is not None
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
SOURCE=ROOT/'examples/champions'

class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__();self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))

class BuildTests(unittest.TestCase):
    def setUp(self): self.site=json.loads((SOURCE/'site.json').read_text())
    def test_full_build_and_raw_content(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'output';text=module.build(SOURCE,out)
            self.assertEqual(text,(out/'handoff/index.html').read_text())
            self.assertIn('noindex,nofollow',text)
            self.assertEqual((out/'handoff/robots.txt').read_text(),'User-agent: *\nDisallow: /\n')
            self.assertEqual(len([x for x in Tags(text).tags if x[0]=='details']),12)
            for g in self.site['groups']:
                for v in g['ventures']:
                    self.assertIn(module.E(v['name']),text)
                    self.assertIn(v['name'],(out/'handoff/index.md').read_text())
            self.assertNotIn('\u2014',text)
            self.assertNotIn('\u2013',text)
            for tag,attrs in Tags(text).tags:
                if tag in ('script','img') and 'src' in attrs:
                    self.assertTrue(attrs['src'].startswith('data:'))
    def test_alternate_data_counts_and_brand(self):
        self.site['name']='Fixture Group'
        self.site['hero']['description']='A four-venture test fixture, not a real company.'
        self.site['accent']='#24614A'
        for g in self.site['groups']: g['ventures']=g['ventures'][:1]
        result=module.render(self.site,SOURCE)
        self.assertIn('Fixture Group',result)
        self.assertIn('--accent:#24614A',result)
        self.assertIn('<b>4</b> ventures',result)
        self.assertEqual(len([x for x in Tags(result).tags if x[0]=='details']),4)
    def test_escapes_content(self):
        self.site['hero']['title']='<img src=x onerror=alert(1)>'
        result=module.render(self.site,SOURCE)
        self.assertIn('&lt;img',result)
        self.assertNotIn('<img src=x',result)
    def test_arrowhead_shares_scrubbed_curve(self):
        svg=module.scene(self.site['groups'][1],1)
        paths=[attrs for tag,attrs in Tags(svg).tags if tag=='path']
        curve=[attrs for attrs in paths if attrs.get('class')=='draw-path']
        self.assertEqual(len(curve),1)
        self.assertEqual(curve[0]['d'].count('M'),1)
        self.assertNotIn('m',curve[0]['d'])
        self.assertTrue(curve[0]['d'].endswith('470 43l-14-2 14 2-5 13'))
        self.assertFalse(any(attrs['d'].startswith('M456 42') for attrs in paths))
    def test_reject_urls(self):
        for value in ['javascript:alert(1)','data:text/html,hi','https://user:pass@example.com/','https://a.example/\nmalicious','//example.com']:
            with self.subTest(value=value),self.assertRaises(ValueError): module.safe_url(value)
    def test_reject_contract_errors(self):
        variants=[]
        s=copy.deepcopy(self.site);s['groups'].pop();variants.append(s)
        s=copy.deepcopy(self.site);s['groups'][1]['id']=s['groups'][0]['id'];variants.append(s)
        s=copy.deepcopy(self.site);s['accent']='red;display:none';variants.append(s)
        s=copy.deepcopy(self.site);s['logo']='../../../../../../etc/passwd';variants.append(s)
        s=copy.deepcopy(self.site);s['email']='mail@example.com?cc=someone';variants.append(s)
        s=copy.deepcopy(self.site);s['groups'][0]['visual']='unknown';variants.append(s)
        s=copy.deepcopy(self.site);s['groups'][0]['ventures'][0]['url']='javascript:alert(1)';variants.append(s)
        for i,s in enumerate(variants):
            with self.subTest(case=i),self.assertRaises(ValueError): module.validate(s,SOURCE)

if __name__=='__main__': unittest.main()
