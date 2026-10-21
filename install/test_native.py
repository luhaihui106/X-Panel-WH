"""Synthetic-root tests: never execute a panel/core or host service command."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'native.py'


def elf(arch='arm64'):
    data = bytearray(64)
    data[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<HH', data, 16, 2, {'arm64': 183, 'amd64': 62}[arch])
    return bytes(data)


def package(path, version='test1', extra=None, arch='arm64', panel_arch='arm64', core_arch='arm64'):
    files = {'x-panel': elf(panel_arch), 'bin/xray-linux-' + arch: elf(core_arch),
             'bin/geoip.dat': b'fixture ip', 'bin/geosite.dat': b'fixture site',
             'LICENSE': b'GPL fixture', 'NOTICE': b'upstream attribution fixture',
             'xray-LICENSE': b'MPL fixture', 'xray-README.md': b'Xray fixture',
             'source.tar.gz': b'synthetic source fixture'}
    manifest = {'format': 1, 'product': 'X-Panel-WH', 'version': version,
                'arch': arch, 'source_commit': 'a' * 40,
                'files': {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}
    files['manifest.json'] = json.dumps(manifest).encode()
    with tarfile.open(path, 'w:gz') as tf:
        for name, data in files.items():
            t = tarfile.TarInfo('x-panel-wh/' + name)
            t.size = len(data)
            tf.addfile(t, io.BytesIO(data))
        if extra:
            name, kind = extra
            t = tarfile.TarInfo(name)
            if kind == 'link':
                t.type = tarfile.SYMTYPE
                t.linkname = '/etc/shadow'
            tf.addfile(t, io.BytesIO(b''))
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'])
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'root'
        self.root.mkdir()
        self.pkg = self.base / 'package.tar.gz'
        self.sha = package(self.pkg)

    def run_cli(self, command, *args, ok=True, payload=True):
        cmd = ['python3', '-B', str(SCRIPT), command, '--root', str(self.root)]
        if payload:
            cmd += ['--package', str(self.pkg), '--sha256', self.sha]
        result = subprocess.run(cmd + list(args), text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    @property
    def data(self):
        return self.root / 'var/lib/x-panel-wh'

    def seed(self):
        db = sqlite3.connect(self.data / 'db/x-ui.db')
        db.execute('create table clients (value text)')
        db.execute("insert into clients values ('before')")
        db.commit()
        db.close()
        (self.data / 'bin/config.json').write_text('original config')

    def test_install_existing_refusal_and_uninstall_preserves_data(self):
        self.run_cli('install')
        self.seed()
        self.run_cli('install', ok=False)
        self.run_cli('uninstall', payload=False)
        self.assertTrue((self.data / 'db/x-ui.db').exists())
        self.assertTrue((self.data / 'bin/config.json').exists())
        self.assertFalse((self.root / 'usr/local/lib/x-panel-wh').exists())
        self.run_cli('install', ok=False)

    def test_update_backup_restore_matched_data_and_program(self):
        self.run_cli('install')
        self.seed()
        old = (self.root / 'usr/local/lib/x-panel-wh/manifest.json').read_bytes()
        self.sha = package(self.pkg, 'test2')
        out = self.run_cli('update')
        snapshot = json.loads(out.stdout)['backup']
        db = sqlite3.connect(self.data / 'db/x-ui.db')
        db.execute("update clients set value='after'")
        db.commit()
        db.close()
        (self.data / 'bin/config.json').write_text('changed config')
        self.run_cli('restore', '--backup', snapshot, payload=False)
        self.assertEqual((self.root / 'usr/local/lib/x-panel-wh/manifest.json').read_bytes(), old)
        self.assertEqual((self.data / 'bin/config.json').read_text(), 'original config')
        with sqlite3.connect(self.data / 'db/x-ui.db') as db:
            self.assertEqual(db.execute('select value from clients').fetchone()[0], 'before')
        self.assertTrue(Path(snapshot).exists())

    def test_hash_failure_no_install(self):
        self.sha = '0' * 64
        self.run_cli('install', ok=False)
        self.assertFalse(self.data.exists())

    def test_bad_arch(self):
        self.sha = package(self.pkg, arch='amd64')
        self.run_cli('install', ok=False)
        self.assertFalse(self.data.exists())

    def test_amd64_package_and_cli_install(self):
        from unittest.mock import patch
        module = self.module()
        self.sha = package(self.pkg, arch='amd64', panel_arch='amd64', core_arch='amd64')
        try:
            files, manifest = module.read_package(self.pkg, self.sha)
        except ValueError as exc:
            self.fail('valid AMD64 package refused: ' + str(exc))
        self.assertEqual(manifest['arch'], 'amd64')
        self.assertIn('bin/xray-linux-amd64', files)
        args = ['native.py', 'install', '--root', str(self.root),
                '--package', str(self.pkg), '--sha256', self.sha]
        with patch.object(module.platform, 'machine', return_value='x86_64'), patch.object(module.sys, 'argv', args):
            self.assertEqual(module.main(), 0)
        self.assertEqual((self.data / 'bin/xray-linux-amd64').read_bytes(), elf('amd64'))

    def test_mixed_payload_architectures_refused(self):
        module = self.module()
        for arch, panel, core in [('amd64', 'arm64', 'amd64'),
                                  ('amd64', 'amd64', 'arm64'),
                                  ('arm64', 'amd64', 'arm64'),
                                  ('arm64', 'arm64', 'amd64')]:
            with self.subTest(arch=arch, panel=panel, core=core):
                self.sha = package(self.pkg, arch=arch, panel_arch=panel, core_arch=core)
                with self.assertRaises(ValueError):
                    module.read_package(self.pkg, self.sha)

    def test_valid_package_wrong_host_refused_without_mutation(self):
        from unittest.mock import patch
        module = self.module()
        args = ['native.py', 'install', '--root', str(self.root),
                '--package', str(self.pkg), '--sha256', self.sha]
        with patch.object(module.platform, 'machine', return_value='x86_64'), patch.object(module.sys, 'argv', args):
            self.assertEqual(module.main(), 1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_archive_negative_shapes(self):
        for name, kind in [('x-panel-wh/x-panel', 'file'), ('../escape', 'file'),
                           ('wrong-root/file', 'file'), ('x-panel-wh/link', 'link'),
                           ('x-panel-wh/secret.db', 'file')]:
            with self.subTest(name=name):
                self.sha = package(self.pkg, extra=(name, kind))
                self.run_cli('install', ok=False)
                self.assertFalse(self.data.exists())

    def test_legacy_conflicts(self):
        for item in ['etc/x-ui', 'usr/local/x-ui', 'etc/systemd/system/x-ui.service',
                     'usr/bin/x-ui', 'etc/3x-ui']:
            with self.subTest(item=item):
                p = self.root / item
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
                self.run_cli('install', ok=False)
                self.assertEqual(p.read_bytes(), b'')
                p.unlink()

    def test_custom_paths_render_every_environment(self):
        args = ['--install-dir', '/opt/wh/app', '--data-dir', '/srv/wh/data', '--log-dir', '/srv/wh/log']
        self.run_cli('install', *args)
        unit = (self.root / 'etc/systemd/system/x-panel-wh.service').read_text()
        for text in ['ExecStart=/opt/wh/app/x-panel', 'WorkingDirectory=/opt/wh/app',
                     'XUI_DB_FOLDER=/srv/wh/data/db', 'XUI_BIN_FOLDER=/srv/wh/data/bin',
                     'XUI_LOG_FOLDER=/srv/wh/log', 'ReadWritePaths=/srv/wh/data /srv/wh/log']:
            self.assertIn(text, unit)
        self.assertEqual((self.root / 'srv/wh/data').stat().st_mode & 0o777, 0o700)
        self.assertTrue((self.root / 'srv/wh/data/bin/xray-linux-arm64').is_file())

    def test_symlink_ancestor_rejected(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (self.root / 'var').symlink_to(outside, target_is_directory=True)
        self.run_cli('install', ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_payload_and_unsupported_operations(self):
        self.run_cli('install', payload=False, ok=False)
        self.run_cli('recover', payload=False, ok=False)
        self.run_cli('install', '--url', 'http://example.invalid/latest', ok=False)

    def test_snapshot_tamper_refused_without_mutation(self):
        self.run_cli('install')
        self.seed()
        self.sha = package(self.pkg, 'test2')
        snapshot = Path(json.loads(self.run_cli('update').stdout)['backup'])
        (snapshot / 'app/x-panel').write_bytes(b'tamper')
        current = (self.root / 'usr/local/lib/x-panel-wh/manifest.json').read_bytes()
        self.run_cli('restore', '--backup', str(snapshot), payload=False, ok=False)
        self.assertEqual((self.root / 'usr/local/lib/x-panel-wh/manifest.json').read_bytes(), current)

    def module(self):
        spec = importlib.util.spec_from_file_location('native', SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def installer(self):
        import argparse
        return self.module().Installer(argparse.Namespace(root=str(self.root),
            install_dir='/usr/local/lib/x-panel-wh', data_dir='/var/lib/x-panel-wh',
            log_dir='/var/log/x-panel-wh', command='update', backup=None))

    def test_start_failure_restores_matched_snapshot(self):
        self.run_cli('install')
        self.seed()
        installer = self.installer()
        old = (installer.app / 'x-panel').read_bytes()
        files, _ = self.module().read_package(self.pkg, self.sha)
        calls = []
        def start():
            calls.append('start')
            if len(calls) == 1:
                (installer.data / 'bin/config.json').write_text('failed candidate config')
                raise RuntimeError('injected service failure')
        installer.start = start
        with self.assertRaisesRegex(RuntimeError, 'injected'):
            installer.execute(files)
        self.assertEqual(calls, ['start', 'start'])
        self.assertEqual((installer.app / 'x-panel').read_bytes(), old)
        self.assertEqual((installer.data / 'bin/config.json').read_text(), 'original config')
        self.assertFalse(installer.marker.exists())

    def test_marker_write_failure_restarts_unchanged_service(self):
        from unittest.mock import patch
        self.run_cli('install')
        self.seed()
        installer = self.installer()
        module = self.module()
        files, _ = module.read_package(self.pkg, self.sha)
        restore = installer.snapshot()
        before = [module.tree_manifest(p) for p in
                  [installer.app, installer.data / 'db', installer.data / 'bin']]
        real_write = installer.execute.__globals__['write']
        def fail_marker(path, data, mode=0o600):
            if path == installer.marker:
                raise OSError(28, 'injected marker ENOSPC')
            return real_write(path, data, mode)
        for command in ['update', 'restore', 'uninstall']:
            with self.subTest(command=command):
                installer.args.command = command
                installer.args.backup = str(restore)
                with patch.object(installer, 'stop') as stop, patch.object(installer, 'start') as start, patch.dict(installer.execute.__globals__, write=fail_marker):
                    with self.assertRaisesRegex(OSError, 'marker ENOSPC'):
                        installer.execute(files)
                stop.assert_called_once_with()
                start.assert_called_once_with()
                self.assertFalse(installer.marker.exists())
                self.assertEqual(before, [module.tree_manifest(p) for p in
                    [installer.app, installer.data / 'db', installer.data / 'bin']])
        self.assertEqual(len(list((installer.data / 'backups').iterdir())), 4)

    def test_pre_mutation_failures_preserve_evidence_and_restart(self):
        from unittest.mock import patch
        self.run_cli('install')
        self.seed()
        installer = self.installer()
        module = self.module()
        files, _ = module.read_package(self.pkg, self.sha)
        restore = installer.snapshot()
        real_unlink = Path.unlink
        real_write = installer.execute.__globals__['write']
        real_snapshot = installer.snapshot
        def fail_unlink(path, *args, **kwargs):
            if path == installer.marker:
                raise OSError('injected marker unlink failure')
            return real_unlink(path, *args, **kwargs)
        def partial_marker(path, data, mode=0o600):
            if path == installer.marker:
                real_write(path, b'partial marker')
                raise OSError('injected partial marker failure')
            return real_write(path, data, mode)
        def partial_snapshot():
            directory = real_snapshot()
            raise OSError('injected snapshot failure after ' + str(directory))
        for command in ['update', 'restore', 'uninstall']:
            for failure in ['snapshot', 'unlink', 'partial-marker']:
                with self.subTest(command=command, failure=failure):
                    installer.args.command = command
                    installer.args.backup = str(restore)
                    installer.marker.unlink(missing_ok=True)
                    if failure == 'unlink':
                        # Only restore accepts a retained pending marker.
                        if command == 'restore':
                            installer.marker.write_bytes(b'previous pending')
                    before = [module.tree_manifest(p) for p in
                              [installer.app, installer.data / 'db', installer.data / 'bin']]
                    with patch.object(installer, 'stop') as stop, patch.object(installer, 'start') as start, patch.object(installer, 'replace_from_snapshot') as replace, patch.object(installer, 'snapshot', partial_snapshot if failure == 'snapshot' else real_snapshot), patch.object(Path, 'unlink', fail_unlink if failure == 'unlink' else real_unlink), patch.dict(installer.execute.__globals__, write=partial_marker if failure == 'partial-marker' else real_write):
                        with self.assertRaisesRegex(OSError, 'injected'):
                            installer.execute(files)
                    stop.assert_called_once_with()
                    start.assert_called_once_with()
                    replace.assert_not_called()
                    self.assertEqual(before, [module.tree_manifest(p) for p in
                        [installer.app, installer.data / 'db', installer.data / 'bin']])
                    if failure == 'partial-marker':
                        self.assertEqual(installer.marker.read_bytes(), b'partial marker')
                    if command == 'restore' and failure == 'unlink':
                        self.assertEqual(installer.marker.read_bytes(), b'previous pending')

    def test_recovery_failure_reports_original_and_recovery_errors(self):
        from unittest.mock import patch
        self.run_cli('install')
        self.seed()
        installer = self.installer()
        files, _ = self.module().read_package(self.pkg, self.sha)
        for mutated in [False, True]:
            with self.subTest(mutated=mutated):
                installer.marker.unlink(missing_ok=True)
                failing = patch.object(installer, 'deploy', side_effect=OSError('candidate deploy failed')) if mutated else patch.object(installer, 'snapshot', side_effect=OSError('snapshot ENOSPC'))
                with failing, patch.object(installer, 'stop'), patch.object(installer, 'start', side_effect=OSError('old service restart failed')):
                    with self.assertRaisesRegex(ValueError, 'recovery failed:.*old service restart failed') as caught:
                        installer.execute(files)
                self.assertIn('candidate deploy failed' if mutated else 'snapshot ENOSPC', str(caught.exception))
                self.assertIsInstance(caught.exception.__cause__, OSError)
                if mutated:
                    self.assertTrue(installer.marker.exists())
                    self.assertTrue(list((installer.data / 'backups').iterdir()))

    def test_wal_snapshot_includes_committed_rows(self):
        self.run_cli('install')
        db = sqlite3.connect(self.data / 'db/x-ui.db')
        self.addCleanup(db.close)
        db.execute('pragma journal_mode=WAL')
        db.execute('create table clients (value text)')
        db.execute("insert into clients values ('wal committed')")
        db.commit()
        installer = self.installer()
        snapshot = installer.snapshot()
        with sqlite3.connect(snapshot / 'db/x-ui.db') as backup:
            self.assertEqual(backup.execute('select value from clients').fetchone()[0], 'wal committed')
        self.assertFalse((snapshot / 'db/x-ui.db-wal').exists())

    def test_https_download_flags_and_checksum(self):
        from unittest.mock import patch
        module = self.module()
        # Exercise the real CLI parser/download branch without network or host mutation.
        args = ['native.py', 'install', '--root', str(self.root), '--url',
                'https://example.invalid/v1/x-panel-wh.tar.gz', '--sha256', self.sha]
        def curl(command, **kwargs):
            self.assertIn('--proto-redir', command)
            self.assertIn('=https', command)
            self.assertNotIn('-k', command)
            Path(command[command.index('-o') + 1]).write_bytes(self.pkg.read_bytes())
        with patch.object(module.sys, 'argv', args), patch.object(module.subprocess, 'run', curl):
            self.assertEqual(module.main(), 0)

    def test_interrupted_marker_refuses_automatic_retry(self):
        self.run_cli('install')
        (self.data / '.operation-pending').write_text('interrupted')
        self.run_cli('update', ok=False)

    def test_service_stop_failure_does_not_replace_state(self):
        self.run_cli('install')
        self.seed()
        installer = self.installer()
        old = (installer.app / 'manifest.json').read_bytes()
        files, _ = self.module().read_package(self.pkg, self.sha)
        def stop():
            raise RuntimeError('cannot stop service')
        installer.stop = stop
        with self.assertRaisesRegex(RuntimeError, 'cannot stop'):
            installer.execute(files)
        self.assertEqual((installer.app / 'manifest.json').read_bytes(), old)
        self.assertFalse((installer.data / 'backups').exists())

    def test_package_required_members_and_elf_validation(self):
        module = self.module()
        module.check_elf(elf())
        for bad in [b'', b'#!/bin/sh', b'\x7fELF' + bytes(60)]:
            with self.assertRaises(ValueError):
                module.check_elf(bad)
        with tarfile.open(self.pkg, 'w:gz') as tf:
            t = tarfile.TarInfo('x-panel-wh/manifest.json')
            t.size = 2
            tf.addfile(t, io.BytesIO(b'{}'))
        self.sha = hashlib.sha256(self.pkg.read_bytes()).hexdigest()
        self.run_cli('install', ok=False)

    def test_lock_contention_refuses_no_install(self):
        import fcntl
        with (self.root / '.x-panel-wh.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.run_cli('install', ok=False)
        self.assertFalse(self.data.exists())


if __name__ == '__main__':
    unittest.main()
