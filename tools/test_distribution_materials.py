#!/usr/bin/env python3
"""Check only distribution-material completeness/integrity, not legal clearance."""
import hashlib
import json
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MaterialTests(unittest.TestCase):
    def test_notice_hashes(self):
        records = json.loads((ROOT / 'docs/frontend-license-sources.json').read_text())
        self.assertEqual(len(records), 39)
        self.assertEqual(len({item['path'] for item in records}), len(records))
        for item in records:
            with self.subTest(component=item['component']):
                data = (ROOT / item['path']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])
                self.assertIn('SOFTWARE', data.decode())

    def test_sidecar(self):
        path = ROOT / 'web/assets/ant-design-vue/antd.min.js.LICENSE.txt'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         'b7b4580b625aee07be8e9c69d7f878a4b73b8212823e0397b51802e58ff3e6e7')
        self.assertIn(path.name, (path.parent / 'antd.min.js').read_text())

    def test_original_assets_unchanged(self):
        baseline = '6bd7f6a3b4f3379081b2bf324b87e1c04fec1c84'
        paths = subprocess.check_output(
            ['git', 'ls-tree', '-r', '--name-only', baseline, 'web/assets'], cwd=ROOT,
            text=True).splitlines()
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                original = subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)
                self.assertEqual(original, (ROOT / path).read_bytes())

    def test_actual_qrious_sources(self):
        source = ROOT / 'third_party/qrious2/upstream/dist/qrious2.js'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         '528afc4d52510d19ac39fc957c94e8dc8c3e8aff3d8925e7c04133c9ae4ff219')
        for symbol in ['positionCorner', 'dataCornerTL', 'dataCornerTR',
                       'dataCornerBR', 'dataCornerBL', 'positionSep', 'dataSep']:
            self.assertIn(symbol, source.read_text())
        self.assertIn('OPEN', (source.parents[2] / 'README.md').read_text())

    def test_font_and_qs_identity(self):
        for path, digest in {
            'Vazirmatn-UI-NL-Regular.woff2': '1270a82ccd9a773092f3f89cfc803fdb2b3c598f6406a420bb552006c2739c62',
            'qs/qs.min.js': '3c087b72da857ec5ab1a07dfad36805210a4ff0f9166c76a4f8156451fe1e3c6'
        }.items():
            self.assertEqual(hashlib.sha256((ROOT / 'web/assets' / path).read_bytes()).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()
