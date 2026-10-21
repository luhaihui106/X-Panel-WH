#!/usr/bin/env python3
"""X-Panel-WH native installer. Standard library only; no inherited script execution.
Synthetic --root mode is offline: it NEVER calls systemctl or runs payloads.
Trust boundary: exclusive root operator, trusted package digest and root-owned paths.
Not a power-loss journal or protection against a concurrent malicious root process.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import sqlite3
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import uuid

FILES = {'x-panel', 'bin/geoip.dat', 'bin/geosite.dat',
         'LICENSE', 'NOTICE', 'xray-LICENSE', 'xray-README.md', 'source.tar.gz'}
ARCHES = {'arm64': 183, 'amd64': 62}
MAX_BYTES = 512 * 1024 * 1024
UNIT = 'x-panel-wh.service'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def check_elf(data, arch='arm64'):
    if (len(data) < 64 or data[:6] != b'\x7fELF\x02\x01' or
            arch not in ARCHES or struct.unpack_from('<H', data, 18)[0] != ARCHES[arch] or
            struct.unpack_from('<H', data, 16)[0] not in (2, 3)):
        raise ValueError('expected Linux ' + arch + ' ELF executable')


def host_arch():
    arch = {'aarch64': 'arm64', 'arm64': 'arm64',
            'x86_64': 'amd64', 'amd64': 'amd64'}.get(platform.machine())
    if platform.system() != 'Linux' or arch is None:
        raise ValueError('only Linux ARM64/AMD64 is currently supported')
    return arch


def read_package(path, sha):
    if not re.fullmatch('[0-9a-f]{64}', sha or ''):
        raise ValueError('--sha256 must be the independently recorded package SHA256')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('package too large')
    raw = path.read_bytes()
    if digest(raw) != sha:
        raise ValueError('package SHA256 mismatch')
    import io
    contents = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tf:
        for member in tf:
            if not member.isfile() or member.name in contents:
                raise ValueError('only unique regular package files allowed')
            allowed = {'x-panel-wh/' + f for f in FILES | {'manifest.json'} |
                       {'bin/xray-linux-' + arch for arch in ARCHES}}
            if member.name not in allowed:
                raise ValueError('unexpected package member: ' + member.name)
            total += member.size
            if total > MAX_BYTES:
                raise ValueError('expanded package too large')
            stream = tf.extractfile(member)
            if stream is None:
                raise ValueError('unreadable package file')
            contents[member.name] = stream.read()
    if 'x-panel-wh/manifest.json' not in contents:
        raise ValueError('incomplete package')
    files = {k.removeprefix('x-panel-wh/'): v for k, v in contents.items()}
    manifest = unique_json(files['manifest.json'])
    if (set(manifest) != {'format', 'product', 'version', 'arch', 'source_commit', 'files'} or
            manifest['format'] != 1 or manifest['product'] != 'X-Panel-WH' or
            manifest['arch'] not in ARCHES or
            not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', manifest['version']) or
            not re.fullmatch('[0-9a-f]{40}', manifest['source_commit']) or
            set(manifest['files']) != FILES | {'bin/xray-linux-' + manifest['arch']}):
        raise ValueError('unsupported package manifest')
    expected = FILES | {'bin/xray-linux-' + manifest['arch']}
    if set(files) != expected | {'manifest.json'}:
        raise ValueError('incomplete or mixed-architecture package')
    for name in expected:
        if digest(files[name]) != manifest['files'][name]:
            raise ValueError('payload SHA256 mismatch: ' + name)
    for name in ['x-panel', 'bin/xray-linux-' + manifest['arch']]:
        check_elf(files[name], manifest['arch'])
    return files, manifest


def safe_path(root, value):
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+', value):
        raise ValueError('path must be absolute, without spaces or shell/systemd escapes')
    parts = PurePosixPath(value).parts[1:]
    if not parts or any(p in ('.', '..') for p in parts) or '//' in value:
        raise ValueError('noncanonical path')
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise ValueError('symlink path refused: ' + str(p))
        if p.exists() and (p.stat().st_uid != os.geteuid() or p.stat().st_mode & 0o022):
            raise ValueError('path must be operator-owned and not group/world writable: ' + str(p))
    return p


def mkdir(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)


def write(path, data, mode=0o600):
    mkdir(path.parent)
    with path.open('xb') as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    path.chmod(mode)


def tree_manifest(root):
    result = {}
    for p in sorted(root.rglob('*')):
        st = p.lstat()
        if not stat.S_ISREG(st.st_mode) and not stat.S_ISDIR(st.st_mode):
            raise ValueError('non-regular state entry refused: ' + str(p))
        if stat.S_ISREG(st.st_mode):
            if st.st_nlink != 1:
                raise ValueError('hardlinked state refused')
            result[str(p.relative_to(root))] = [digest(p.read_bytes()), stat.S_IMODE(st.st_mode)]
    return result


def copy_tree(src, dst):
    tree_manifest(src)  # reject symlinks/special files before copying
    shutil.copytree(src, dst)


def render_unit(install, data, log):
    return f'''[Unit]
Description=X-Panel-WH (community derivative of xeefei/X-Panel)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
UMask=0077
WorkingDirectory={log}
ExecStart={install}/x-panel
Environment="XUI_DB_FOLDER={data}/db"
Environment="XUI_LOG_FOLDER={log}"
Environment="XUI_BIN_FOLDER={data}/bin"
Environment="XRAY_VMESS_AEAD_FORCED=false"
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
KillMode=control-group
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths={data} {log}

[Install]
WantedBy=multi-user.target
'''.encode()


class Installer:
    def __init__(self, args):
        self.args = args
        self.offline = args.root is not None
        self.root = Path(args.root or '/')
        if not self.root.is_absolute() or self.root.is_symlink() or not self.root.is_dir():
            raise ValueError('--root must be an existing absolute real directory')
        if self.offline and self.root.resolve() == Path('/'):
            raise ValueError('--root / is not synthetic; omit it for explicit host installation')
        host_arch()
        if not self.offline:
            if os.geteuid() != 0 or not Path('/run/systemd/system').is_dir():
                raise ValueError('real installation requires root and running systemd')
            if not shutil.which('systemctl'):
                raise ValueError('systemctl unavailable')
        paths = [args.install_dir, args.data_dir, args.log_dir]
        self.app, self.data, self.log = [safe_path(self.root, p) for p in paths]
        self.unit = safe_path(self.root, '/etc/systemd/system/' + UNIT)
        for i, p in enumerate([self.app, self.data, self.log]):
            for q in [self.app, self.data, self.log][i + 1:]:
                if p == q or p in q.parents or q in p.parents:
                    raise ValueError('install/data/log roots must not overlap')
        for legacy in ['/etc/x-ui', '/etc/3x-ui', '/usr/local/x-ui', '/usr/local/3x-ui',
                       '/usr/bin/x-ui', '/usr/local/bin/x-ui',
                       '/etc/systemd/system/x-ui.service', '/etc/systemd/system/3x-ui.service',
                       '/lib/systemd/system/x-ui.service', '/usr/lib/systemd/system/x-ui.service']:
            p = self.root / legacy.lstrip('/')
            if p.exists() or p.is_symlink():
                raise ValueError('existing X-UI installation refused: ' + legacy)
        self.marker = self.data / '.operation-pending'

    def service(self, *args):
        if not self.offline:
            subprocess.run(['systemctl', *args], check=True, timeout=65,
                           stdout=subprocess.DEVNULL)

    def stop(self):
        self.service('stop', UNIT)
        if not self.offline:
            # KillMode=control-group; check inactive before touching SQLite/core config.
            status = subprocess.run(['systemctl', 'is-active', '--quiet', UNIT])
            if status.returncode == 0:
                raise ValueError('service still active after stop')

    def start(self):
        self.service('daemon-reload')
        self.service('start', UNIT)
        self.service('is-active', '--quiet', UNIT)
        # This is service-active only, NOT authenticated HTTP/core acceptance.

    def installed(self):
        if not self.app.is_dir() or not self.data.is_dir() or not self.unit.is_file():
            raise ValueError('managed installation incomplete or absent')
        receipt = unique_json((self.app / '.installation.json').read_bytes())
        expected = [self.args.install_dir, self.args.data_dir, self.args.log_dir]
        if receipt != {'product': 'X-Panel-WH', 'paths': expected}:
            raise ValueError('managed installation receipt/path mismatch')
        if self.unit.read_bytes() != render_unit(*expected):
            raise ValueError('unit changed; reconcile manually before lifecycle operation')
        tree_manifest(self.app)
        tree_manifest(self.data / 'db')
        tree_manifest(self.data / 'bin')

    def snapshot(self):
        directory = self.data / 'backups' / uuid.uuid4().hex
        mkdir(directory)
        copy_tree(self.app, directory / 'app')
        copy_tree(self.data / 'bin', directory / 'bin')
        copy_tree(self.data / 'db', directory / 'db')
        # stopped service + SQLite backup API: includes committed WAL pages, no blind main-file copy.
        for dbpath in (self.data / 'db').glob('*.db'):
            dest = directory / 'db' / dbpath.name
            dest.unlink()
            with contextlib.closing(sqlite3.connect(dbpath.as_uri() + '?mode=ro', uri=True)) as src:
                with contextlib.closing(sqlite3.connect(dest)) as dst:
                    src.backup(dst)
                    if dst.execute('pragma integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('backup SQLite integrity failure')
                    dst.execute('pragma journal_mode=DELETE')
            for suffix in ['-wal', '-shm', '-journal']:
                (directory / 'db' / (dbpath.name + suffix)).unlink(missing_ok=True)
            dest.chmod(0o600)
        write(directory / 'unit', self.unit.read_bytes())
        sums = tree_manifest(directory)
        write(directory / 'snapshot.json', json.dumps({'format': 1, 'files': sums}).encode())
        return directory

    def checked_snapshot(self, path):
        directory = Path(path)
        if (directory.parent != self.data / 'backups' or
                not re.fullmatch('[0-9a-f]{32}', directory.name) or directory.is_symlink()):
            raise ValueError('backup must be a managed snapshot in this data directory')
        expected = unique_json((directory / 'snapshot.json').read_bytes())
        actual = tree_manifest(directory)
        actual.pop('snapshot.json')
        if expected != {'format': 1, 'files': actual}:
            raise ValueError('backup content/permission mismatch')
        receipt = unique_json((directory / 'app/.installation.json').read_bytes())
        if receipt != {'product': 'X-Panel-WH', 'paths': [self.args.install_dir, self.args.data_dir, self.args.log_dir]}:
            raise ValueError('backup belongs to different paths')
        return directory

    def replace_from_snapshot(self, directory):
        # Called only with stopped service under installer lock. Backups themselves are retained.
        for src, dst in [(directory / 'app', self.app), (directory / 'bin', self.data / 'bin'),
                         (directory / 'db', self.data / 'db')]:
            if dst.exists():
                shutil.rmtree(dst)
            copy_tree(src, dst)
        self.unit.unlink(missing_ok=True)
        write(self.unit, (directory / 'unit').read_bytes(), 0o644)

    def deploy(self, files):
        stage = Path(tempfile.mkdtemp(prefix='.x-panel-wh-stage-', dir=self.app.parent))
        try:
            for name, data in files.items():
                if name.startswith('bin/'):
                    continue
                write(stage / name, data, 0o755 if name == 'x-panel' else 0o600)
            write(stage / '.installation.json', json.dumps({'product': 'X-Panel-WH', 'paths':
                  [self.args.install_dir, self.args.data_dir, self.args.log_dir]}).encode())
            old = None
            if self.app.exists():
                old = self.app.parent / ('.x-panel-wh-old-' + uuid.uuid4().hex)
                self.app.rename(old)
            stage.rename(self.app)
            if old:
                shutil.rmtree(old)
            for name, data in files.items():
                if name.startswith('bin/'):
                    dest = self.data / name
                    temp = dest.with_name('.' + dest.name + '.new')
                    write(temp, data, 0o700 if 'xray-' in name else 0o600)
                    temp.replace(dest)
        finally:
            if stage.exists():
                shutil.rmtree(stage)

    def execute(self, files=None):
        command = self.args.command
        if command != 'restore' and self.app.parent.exists():
            for pattern in ['.x-panel-wh-stage-*', '.x-panel-wh-old-*']:
                if any(self.app.parent.glob(pattern)):
                    raise ValueError('interrupted program tree retained; manual reconciliation required')
        if self.marker.exists() and command != 'restore':
            raise ValueError('interrupted operation: retain evidence and explicitly restore a checked backup')
        if command == 'install':
            for p in [self.app, self.data, self.log, self.unit]:
                if p.exists():
                    raise ValueError('occupied destination refused: ' + str(p))
            for p in [self.app.parent, self.data / 'db', self.data / 'bin', self.log, self.unit.parent]:
                mkdir(p)
            write(self.marker, b'install pending; no previous snapshot')
            self.deploy(files)
            write(self.unit, render_unit(self.args.install_dir, self.args.data_dir, self.args.log_dir), 0o644)
            # No auto-enable: operator first changes default credentials and checks local HTTP.
            self.marker.unlink()
            return {'installed': str(self.app), 'started': False, 'enabled': False}
        directory = self.checked_snapshot(self.args.backup) if command == 'restore' else None
        self.installed()
        self.stop()
        backup = None
        changed = False
        try:
            backup = self.snapshot()
            self.marker.unlink(missing_ok=True)
            write(self.marker, json.dumps({'operation': command, 'backup': str(backup)}).encode())
            changed = True  # mutation may partially succeed before raising
            if command == 'update':
                self.deploy(files)
                self.start()
            elif command == 'restore':
                self.replace_from_snapshot(directory)
                self.start()
            elif command == 'uninstall':
                self.service('disable', UNIT)
                self.unit.unlink()
                shutil.rmtree(self.app)
                self.service('daemon-reload')
            self.marker.unlink()
        except Exception as failure:
            try:
                if changed:
                    # Match program, DB, generated config, core assets and service definition.
                    self.stop()
                    self.replace_from_snapshot(backup)
                self.start()
                if changed:
                    self.marker.unlink(missing_ok=True)
                # Before mutation, retain any partial marker/snapshot as failure evidence.
            except Exception as recovery:
                raise ValueError(f'{command} failed: {failure!r}; recovery failed: {recovery!r}; '
                                 f'retain pending/snapshots at {self.data}; backup={backup}') from failure
            raise
        return {'operation': command, 'backup': str(backup), 'offline': self.offline,
                'data_retained': str(self.data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['install', 'update', 'restore', 'uninstall'])
    parser.add_argument('--root', help='offline synthetic root; NEVER starts/enables services')
    parser.add_argument('--install-dir', default='/usr/local/lib/x-panel-wh')
    parser.add_argument('--data-dir', default='/var/lib/x-panel-wh')
    parser.add_argument('--log-dir', default='/var/log/x-panel-wh')
    parser.add_argument('--package', type=Path)
    parser.add_argument('--url', help='explicit fixed HTTPS asset URL; no latest/upstream fallback')
    parser.add_argument('--sha256')
    parser.add_argument('--backup')
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.command == 'restore' and not args.backup:
            raise ValueError('restore requires --backup')
        with tempfile.TemporaryDirectory(prefix='x-panel-wh-') as temp:
            files = None
            if args.command in ('install', 'update'):
                if bool(args.package) == bool(args.url):
                    raise ValueError('specify exactly one of --package or --url')
                if args.url:
                    from urllib.parse import urlsplit
                    parsed = urlsplit(args.url)
                    if (parsed.scheme != 'https' or not parsed.netloc or parsed.username or
                            parsed.query or parsed.fragment or 'latest' in parsed.path.lower()):
                        raise ValueError('only fixed HTTPS URLs without credentials/query/fragment allowed')
                    args.package = Path(temp) / 'package.tar.gz'
                    subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                                    '--proto', '=https', '--proto-redir', '=https', '--tlsv1.2',
                                    '--connect-timeout', '20', '--max-time', '300',
                                    '--max-filesize', str(MAX_BYTES), '-o', str(args.package), args.url], check=True)
                files, manifest = read_package(args.package, args.sha256)
                if manifest['arch'] != host_arch():
                    raise ValueError('package architecture does not match host')
            elif args.package or args.url or args.sha256:
                raise ValueError('payload options are only valid for install/update')
            installer = Installer(args)
            lockdir = installer.root if installer.offline else Path('/run/lock')
            lockpath = lockdir / '.x-panel-wh.lock'
            fd = os.open(lockpath, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'w') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print(json.dumps(installer.execute(files)))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, tarfile.TarError, sqlite3.Error, KeyError, TypeError) as exc:
        print('x-panel-wh: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
