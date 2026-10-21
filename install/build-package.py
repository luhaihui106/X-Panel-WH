#!/usr/bin/env python3
"""Build a local ARM64/AMD64 candidate from a verified panel and pinned Xray ZIP.
Does not execute payloads, compile code, install services or publish anything.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile

from native import check_elf, digest, read_package

XRAY_SHA256 = {
    'arm64': '4d30283ae614e3057f730f67cd088a42be6fdf91f8639d82cb69e48cde80413c',
    'amd64': '23cd9af937744d97776ee35ecad4972cf4b2109d1e0fe6be9930467608f7c8ae',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arch', choices=sorted(XRAY_SHA256), default='arm64')
    parser.add_argument('--panel', type=Path, required=True)
    parser.add_argument('--panel-sha256', required=True)
    parser.add_argument('--xray-zip', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', args.version):
        raise ValueError('invalid version')
    if args.output.exists():
        raise ValueError('output already exists')
    panel = args.panel.read_bytes()
    if digest(panel) != args.panel_sha256:
        raise ValueError('panel SHA256 mismatch')
    check_elf(panel, args.arch)
    raw = args.xray_zip.read_bytes()
    if digest(raw) != XRAY_SHA256[args.arch]:
        raise ValueError('Xray release ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files = {'bin/xray-linux-' + args.arch: archive.read('xray'),
                 'bin/geoip.dat': archive.read('geoip.dat'),
                 'bin/geosite.dat': archive.read('geosite.dat'),
                 'xray-LICENSE': archive.read('LICENSE'),
                 'xray-README.md': archive.read('README.md')}
    check_elf(files['bin/xray-linux-' + args.arch], args.arch)
    files['x-panel'] = panel
    files['LICENSE'] = (repo / 'LICENSE').read_bytes()
    # Explicit tracked source only; .hermes/summary.json/runtime data cannot enter.
    files['source.tar.gz'] = subprocess.check_output(
        ['git', 'archive', '--format=tar.gz', '--prefix=X-Panel-WH/', head], cwd=repo)
    files['NOTICE'] = (f'''X-Panel-WH local candidate {args.version}
Community derivative of xeefei/X-Panel. Preserve inherited copyright and GPL license.
Source commit: {head}
Corresponding panel source is included in source.tar.gz.
Panel SHA256: {args.panel_sha256}
Xray-core v26.3.27, MPL-2.0: https://github.com/XTLS/Xray-core/tree/v26.3.27
Xray ZIP SHA256: {XRAY_SHA256[args.arch]}
Original Xray LICENSE and README included. Data files are exact upstream ZIP bytes.
This is a private test candidate, NOT a public Release or a redistribution-rights verdict.
Third-party frontend/data redistribution and final notices need scoped release review.
Panel target: linux/{args.arch}. Reused verified executable, not compiled by this packager.
Panel build revision/toolchain may differ from package source commit; consult delivery evidence.
No claim of static linking, cross-distro compatibility, browser or core traffic acceptance.
''').encode()
    manifest = {'format': 1, 'product': 'X-Panel-WH', 'version': args.version,
                'arch': args.arch, 'source_commit': head,
                'files': {name: digest(data) for name, data in files.items()}}
    files['manifest.json'] = json.dumps(manifest, indent=2, sort_keys=True).encode() + b'\n'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as out:
        with tarfile.open(fileobj=out, mode='w:gz') as archive:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo('x-panel-wh/' + name)
                member.size = len(data)
                member.mode = 0o755 if name == 'x-panel' or name.startswith('bin/xray-') else 0o644
                archive.addfile(member, io.BytesIO(data))
    sha = digest(args.output.read_bytes())
    read_package(args.output, sha)
    sidecar = args.output.with_name(args.output.name + '.sha256')
    with sidecar.open('x') as out:
        out.write(sha + '  ' + args.output.name + '\n')
    print(json.dumps({'package': str(args.output.resolve()), 'sha256': sha,
                      'source_commit': head, 'members': len(files)}, indent=2))


if __name__ == '__main__':
    main()
