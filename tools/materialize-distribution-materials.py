#!/usr/bin/env python3
"""Materialize verified notice/source inputs; never fetch or change runtime assets.

Usage: python3 tools/materialize-distribution-materials.py EVIDENCE_ROOT
The evidence root is the run80 directory documented in docs/distribution-materials.md.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
evidence = pathlib.Path(sys.argv[1]).resolve()
frontend = evidence / 'frontend'
records = []


def emit(path, content):
    target = ROOT / path
    if target.exists():
        raise SystemExit('Refusing to overwrite: ' + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


# Versions below identify notice inputs, not unproved runtime bundle versions.
names = ['ant-design-vue', 'axios', 'vue', 'otpauth', '@noble_hashes',
         'urijs', 'codemirror', 'jshint', 'moment', 'moment-jalaali',
         'jalaali-js', 'qs', 'vazirmatn', 'classnames', 'object-assign',
         'punycode-1.4.0', '@majidh1_jalalidatepicker-0.9.4', 'lodash',
         'babel-runtime', 'raf', 'warning', 'vue-ref', 'shallowequal',
         'dom-align', 'resize-observer-polyfill', 'process', 'async-validator',
         'json2mq', 'enquire.js', 'add-dom-event-listener', '@ant-design_colors',
         'shallow-equal', 'dom-closest', 'performance-now', 'mutationobserver-shim',
         'string-convert', 'dom-matches', 'core-js']
for name in names:
    directory = frontend / name
    package = directory / 'unpacked/package'
    if not package.exists():
        package = directory / 'package'
    licenses = [p for p in package.glob('*') if p.is_file() and
                any(word in p.name.lower() for word in ('license', 'copying', 'ofl'))]
    if not licenses:
        licenses = list(directory.glob('fallback-LICENSE'))
    if len(licenses) != 1:
        raise SystemExit('Expected exactly one license: ' + name)
    source = licenses[0]
    metadata = json.loads((package / 'package.json').read_text())
    content = source.read_bytes()
    destination = 'LICENSES/frontend/' + name.replace('@', '') + '.txt'
    emit(destination, content)
    records.append(dict(component=metadata['name'], notice_version=metadata['version'],
                        path=destination, sha256=hashlib.sha256(content).hexdigest(),
                        source=str(source.relative_to(evidence)),
                        scope='Notice input; see asset mapping for runtime identity.'))

source = frontend / 'jsonlint-1.6.3/package/README.md'
content = (source.read_text().split('## MIT License', 1)[1].strip() + '\n').encode()
emit('LICENSES/frontend/jsonlint.txt', content)
records.append(dict(component='jsonlint', notice_version='1.6.3',
                    path='LICENSES/frontend/jsonlint.txt',
                    sha256=hashlib.sha256(content).hexdigest(),
                    source=str(source.relative_to(evidence)), scope='README MIT section'))
sidecar = frontend / 'ant-design-vue/unpacked/package/dist/antd.min.js.LICENSE.txt'
content = sidecar.read_bytes()
assert hashlib.sha256(content).hexdigest() == 'b7b4580b625aee07be8e9c69d7f878a4b73b8212823e0397b51802e58ff3e6e7'
emit('web/assets/ant-design-vue/antd.min.js.LICENSE.txt', content)

upstream = evidence / 'qrious/upstream'
asset = ROOT / 'web/assets/qrcode/qrious2.min.js'
assert asset.read_bytes() == (upstream / 'dist/qrious2.min.js').read_bytes()
assert hashlib.sha256(asset.read_bytes()).hexdigest() == '2303386046f790f19339ec1b161ac2edfd45d31ba7f8060dc3779745fdc4e7ce'
for path in ['dist/qrious2.js', 'Gruntfile.js', 'package.json', 'package-lock.json',
             'src/QRious.js', 'src/service/element/BrowserElementService.js', 'LICENSE.md']:
    emit('third_party/qrious2/upstream/' + path, (upstream / path).read_bytes())
emit('docs/frontend-license-sources.json', (json.dumps(records, indent=2) + '\n').encode())
print(json.dumps(dict(notices=len(records), qrious_asset_exact=True)))
