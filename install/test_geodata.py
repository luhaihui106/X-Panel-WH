"""Pinned GeoData contract; never executes panel/core or contacts production."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('builder_geo', HERE / 'build-package.py')
assert spec is not None and spec.loader is not None
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class GeoDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Minimal protobuf: GeoIPList/GeoSiteList containing countryCode AA.
        self.blob = b'\x0a\x04\x0a\x02AA'
        for name in ('geoip.dat', 'geosite.dat'):
            (self.root / name).write_bytes(self.blob)
        (self.root / 'NOTICE').write_text('Full licensed fixture attribution')
        self.lock = {'assets': {n: builder.digest((self.root / n).read_bytes())
                               for n in ('geoip.dat', 'geosite.dat', 'NOTICE')},
                     'required_labels': {'geoip.dat': ['aa'], 'geosite.dat': ['aa']}}

    def validate(self):
        return builder.verified_geodata(self.root, self.lock)

    def test_valid_assets_notice_and_labels_bound(self):
        files = self.validate()
        self.assertEqual(files['bin/geoip.dat'], self.blob)
        self.assertEqual(files['bin/geosite.dat'], self.blob)
        self.assertIn(b'Full licensed fixture attribution', files['NOTICE'])

    def test_old_or_wrong_hash_refused(self):
        for data in (b'historical dat', b'wrong hash'):
            with self.subTest(data=data):
                (self.root / 'geoip.dat').write_bytes(data)
                with self.assertRaises(ValueError):
                    self.validate()

    def test_missing_license_refused(self):
        (self.root / 'NOTICE').unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.validate()

    def test_changed_license_refused(self):
        (self.root / 'NOTICE').write_text('missing attribution')
        with self.assertRaises(ValueError):
            self.validate()

    def test_missing_label_even_with_matching_hash_refused(self):
        self.lock['required_labels']['geoip.dat'] = ['private']
        with self.assertRaises(ValueError):
            self.validate()

    def test_malformed_dat_refused(self):
        (self.root / 'geoip.dat').write_bytes(b'\x0a\xff')
        self.lock['assets']['geoip.dat'] = builder.digest(b'\x0a\xff')
        with self.assertRaises(ValueError):
            self.validate()

    def test_no_implicit_old_zip_data_path(self):
        text = (HERE / 'build-package.py').read_text()
        self.assertNotIn("archive.read('geoip.dat')", text)
        self.assertNotIn("archive.read('geosite.dat')", text)
        self.assertIn("'--geodata-dir'", text)


if __name__ == '__main__':
    unittest.main()
