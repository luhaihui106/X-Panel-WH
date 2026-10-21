"""Builder contract tests; synthetic ELF fixtures are never executed."""
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from test_native import elf


class BuildPackageTests(unittest.TestCase):
    def test_amd64_builder_and_mismatched_core(self):
        spec = importlib.util.spec_from_file_location('builder', Path(__file__).with_name('build-package.py'))
        assert spec is not None and spec.loader is not None
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as temp:
            root = Path(temp)
            panel = root / 'panel'
            panel.write_bytes(elf('amd64'))
            archive = root / 'xray.zip'
            source = io.BytesIO()
            with tarfile.open(fileobj=source, mode='w:gz') as tf:
                pass
            for core in ['amd64', 'arm64']:
                with self.subTest(core=core):
                    with zipfile.ZipFile(archive, 'w') as z:
                        for name, data in {'xray': elf(core), 'geoip.dat': b'ip', 'geosite.dat': b'site',
                                           'LICENSE': b'MPL fixture', 'README.md': b'fixture'}.items():
                            z.writestr(name, data)
                    output = root / (core + '.tar.gz')
                    args = ['build-package.py', '--arch', 'amd64', '--panel', str(panel),
                            '--panel-sha256', builder.digest(panel.read_bytes()),
                            '--xray-zip', str(archive), '--geodata-dir', str(root),
                            '--version', 'test-amd64', '--output', str(output)]
                    def git(command, **kwargs):
                        return 'a' * 40 + '\n' if command[1] == 'rev-parse' else source.getvalue()
                    with patch.object(sys, 'argv', args), patch.object(builder.subprocess, 'check_output', git), patch.object(builder, 'XRAY_SHA256', {'amd64': builder.digest(archive.read_bytes())}), patch.object(builder, 'verified_geodata', return_value={'bin/geoip.dat': b'licensed ip', 'bin/geosite.dat': b'licensed site', 'NOTICE': b'licensed fixture'}):
                        if core == 'amd64':
                            try:
                                builder.main()
                            except SystemExit as exc:
                                self.fail('builder refused --arch amd64: ' + str(exc))
                            _, manifest = builder.read_package(output, builder.digest(output.read_bytes()))
                            self.assertEqual(manifest['arch'], 'amd64')
                            files, _ = builder.read_package(output, builder.digest(output.read_bytes()))
                            self.assertEqual(files['bin/geoip.dat'], b'licensed ip')
                            self.assertEqual(files['bin/geosite.dat'], b'licensed site')
                            self.assertIn(b'licensed fixture', files['NOTICE'])
                        else:
                            with self.assertRaises(ValueError):
                                builder.main()
                            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
