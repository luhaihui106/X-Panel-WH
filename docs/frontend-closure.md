# Frontend material closure — t_2802d57d / run82

2026-10-21. Baseline 852359bb5f9265003243c2d0300d9e4fe12b9229.
This assessment covers the named frontend materials only, not a legal warranty,
new release authorization, a new platform matrix or production deployment.

## File-level disposition

- CLOSED — `web/assets/ant-design-vue/antd.min.js` known dependency notices:
  original sidecar and 39 notice texts retained; nine supplemental texts in
  `LICENSES/frontend/` and hashes/sources in
  `docs/frontend-license-supplement.json`. Covers icons/icons-vue,
  array-tree-filter, component-indexof/classes, JSX helper,
  dom-scroll-into-view, is-mobile, omit.js and TinyColor. Unmodified upstream
  packages declaring MIT without their own copyright line are preserved in
  `third_party/frontend-declarations/`; supplemental standard terms are clearly
  labelled, not fabricated upstream notices. Source-map leads and known
  modified-module identities are used proportionately; no exact reconstruction
  of the whole AntD bundle or exhaustive authorship guarantee is asserted.
- CLOSED — `web/assets/moment/moment-jalali.min.js` notice obligations:
  retained moment-jalaali and jalaali-js full MIT copyright/permission texts
  cover the identified included projects. Ten retained moment-jalaali releases
  (0.8.3; 0.9.0–0.9.6; 0.10.0–0.10.1) all declare MIT and have the identical
  LICENSE digest 6fde4ed2f189ce494a5e0b1ab4f9af7ac700d1c6d65d929d7540ae542a05b108.
  Runtime exact release remains unknown; no version is fabricated. That is not
  itself an outstanding copyright/permission obligation.
- CLOSED — `web/assets/qrcode/qrious2.min.js` corresponding-source materials:
  `third_party/qrious2/src/qrious2.js` is the actual preferred editable source
  maintained by this project, byte-identical to the exact published readable
  fork, with original copyrights/GPL/Nevis MIT intact. `build.cjs` now consumes
  it without a fixed-hash refusal that would prevent maintenance. Pinned
  package/lock, source, script, instructions and tests are supplied together.
  The original author's private modular workflow is not claimed recovered.
  No unrelated QR library or historical minification is substituted.
- CLOSED in run81, unchanged here — licensed GeoData source/input delivery and
  browser DB-IP attribution, under `docs/geodata.md`/`docs/geodata-lock.json`.
  Historical unresolved packages are retained, not relabelled as corrected.

## Actual focused checks

Six Python material tests pass: 48 notice hashes, retained upstream MIT
metadata, named missing dependency coverage, source identity/build input,
all original frontend assets unchanged, exact sidecar/font/qs checks.
A scratch clean `npm ci --ignore-scripts` succeeds. Two builds from the
maintained input produce identical SHA-256
888b55623f104fc1ca5c5f80ee9d63eab7c5bfc1baa9b6d61ff3c39b5104c2d4.
Forty drawing-operation cases match original runtime, maintained source and
rebuilt output. A scratch-only source edit demonstrably changes the output;
no canonical runtime/source probe is left behind. These are bounded drawing
checks, not exhaustive QR correctness or a byte-identical historical build.

## Exact local-ready delivery contract

The fixed ARM64/AMD64 run81 archives remain at commit 852359bb, including their
original source archive and binary identity. No panel or native payload is
rebuilt for these material-only edits. Their restored AntD sidecar was already
verified over HTTP by run81, not re-tested as a platform exercise here.

Run82 supplies a separately hashed full current Git source archive, plus a
binding manifest naming both fixed payload hashes, their binary/source commit
and this later material/source commit. It includes the original minified QR,
maintained editable fork, locked build inputs, all notices and declarations.
This companion is an essential part of the local release set, not an optional
link and not something claimed to exist inside the old payload archives.
The separately hashed run81 GeoData input/source archive remains essential too.
The complete set is locally ready when those exact payloads, this source/
material companion, the GeoData input archive and binding manifest are kept
and delivered together. Recipient-facing downloads must expose the complete
source/notices alongside payloads; retain them for recipients and do not ship
just the old native tarballs. No technical frontend material decision remains.

Public push/main/tag/Release and production cutover remain NOT AUTHORIZED.
That is an authority boundary, not an unclosed version-number, modular-source
or notice defect. No new approval framework, signature or broad audit is
required by this task. If a future concrete omitted component is identified,
correct that component specifically; do not restart historical archaeology.

Run evidence and exact deliverable/commit hashes:
`/root/.hermes/cache/scratch/xpanel-launch-20261021/frontend-closure-result.json`.
Prior run80/run81 reports and summary.json remain untouched.
