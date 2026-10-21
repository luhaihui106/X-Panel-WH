# Frontend third-party notices and exact-file mapping

This community derivative retains the root GPLv3 license and existing upstream
copyrights. Third-party components retain their own licenses; font aggregation
does not relicense the font as GPL. Full retrieved texts are in
LICENSES/frontend/. docs/frontend-license-sources.json maps notice inputs to
paths and hashes. docs/frontend-license-supplement.json records run82 additions.
A notice-input version is not an asserted runtime version.

Verified runtime identification:

- ant-design-vue JS/CSS: embedded 1.7.8 identification. The actual JS differs
  from npm 1.7.8: classnames changes, integer DOM measurements, embedded core-js
  version string 2.7.16, TinyColor module and other edits. The upstream 1.7.8
  source map identifies its dependency modules, but is NOT a source map for
  these modified bytes. Restored antd.min.js.LICENSE.txt retains the three
  original sidecar notices. Full ant-design-vue/Alipay, classnames and
  object-assign MIT texts are supplied separately. Additional observed
  dependency notices are supplied, including the run82 supplement described
  below. Known dependency notice coverage is closed without claiming the
  upstream source map reconstructs the modified bundle byte-for-byte.
- axios: exact npm 1.11.0 dist/axios.min.js bytes; MIT, Matt Zabriskie and
  collaborators.
- Vue: 2.7.16 header and parsed/minified code identity with npm 2.7.16
  (comments/whitespace differ); MIT, Evan You.
- OTPAuth: npm 9.4.0 dist/otpauth.umd.min.js equal ignoring outer whitespace;
  contains noble-hashes 1.7.1 identified in its retained header. Both MIT
  notices are provided, not merely the wrapper notice.
- URI.js: retained 1.19.11 header and included IPv6.js, punycode.js,
  SecondLevelDomains.js, URI.js and URITemplate.js identities. URI.js and
  its Rodney Rehm components use MIT; punycode 1.4.0 carries Mathias Bynens's
  separate MIT. The actual asset has inherited transformations versus npm;
  no exact-byte equality is claimed for that whole bundle.
- CodeMirror: runtime version 5.65.15; foldcode, brace-fold, foldgutter JS/CSS,
  javascript-lint and lint.js exactly match npm 5.65.15 members. Core and other
  style/addon files are inherited transformed files, not claimed byte-equal.
  MIT, Marijn Haverbeke and others.
- JSHint: exact npm 2.13.2 dist/jshint.js. MIT, Anton Kovalyov; all existing
  Node/Narwhal and Lodash/Underscore notices in the distributed file remain.
  Full Lodash notice is also supplied. No obsolete JSON "no evil" license
  has been imposed on modern JSHint.
- jsonlint: web/jsonlint.js from npm 1.6.3 matches after outer whitespace
  stripping; full MIT text is from that exact package's README, Zachary Carter.
- Moment: exact npm 2.30.1 min/moment.min.js, MIT, JS Foundation/contributors.
- moment-jalali.min.js is a component-style moment-jalaali bundle registering
  jalaali-js and moment-jalaali, with inherited changes. Exact release version
  is not established and is not itself a missing MIT obligation. Full original
  project copyright/permission/disclaimer notices for both included projects
  are supplied. No version-conditioned license change was identified in the
  retained release inputs. Matching project MIT notices are retained; do not label
  it exact 0.8.3 merely because that notice input is available. jalaali-js
  conversion implementation/exports are present; its separate MIT is supplied.
- qs: exact cdnjs 6.5.2 qs.min.js, SHA-256
  3c087b72da857ec5ab1a07dfad36805210a4ff0f9166c76a4f8156451fe1e3c6.
  Full BSD-3-Clause notice is from npm qs 6.5.2, Nathan LaFreniere and others.
  This version has no package runtime dependencies; build tooling is not
  automatically a bundled runtime dependency.
- persian-datepicker: actual JS exactly matches
  @majidh1/jalalidatepicker 0.9.4 dist/jalalidatepicker.min.js. MIT,
  Copyright (c) 2021 majid hooshiyar. Local CSS includes inherited custom/dark
  styling, so no CSS byte equality is asserted. It is not the unrelated
  babakhani/persian-datepicker library.
- Vazirmatn-UI-NL-Regular.woff2: exact npm vazirmatn 33.0.3
  misc/UI-Non-Latin/fonts/webfonts/Vazirmatn-UI-NL-Regular.woff2; SHA-256
  1270a82ccd9a773092f3f89cfc803fdb2b3c598f6406a420bb552006c2739c62.
  Full OFL-1.1 and project copyright supplied. No font modification.
- qrious2: see third_party/qrious2/README.md for exact fork, GPL and embedded
  Nevis MIT source notices. Readable fork and a working standalone minifier
  are supplied. src/qrious2.js is the project's preferred editable source and
  the actual build input; source delivery is closed on that maintenance basis,
  not on an assertion about the author's unpublished modular workflow.

AntD inherited source-map evidence identifies Babel runtime/helper, Ant Design
icons/icons-vue/colors, omit.js, raf, warning, vue-ref, shallowequal, dom-align,
Lodash, core-js, resize-observer-polyfill, component-classes/indexof,
array-tree-filter, process, async-validator, json2mq, enquire.js,
add-dom-event-listener, is-mobile, shallow-equal, dom-closest, performance-now,
object-assign, TinyColor, mutationobserver-shim, string-convert, dom-matches,
and dom-scroll-into-view. run82 supplements the original 39 notice files with
nine files: Ant Design icons (also covering icons-vue in that monorepo),
array-tree-filter, component-indexof, omit.js, TinyColor, is-mobile,
component-classes, JSX merge helper and dom-scroll-into-view.

For icons/array-tree-filter/indexof the full notice is retrieved from the same
upstream project and its digest recorded; no exact runtime release equality
is inferred from a current branch. omit.js/TinyColor/is-mobile full notices
come from retained package LICENSE or README text. For component-classes,
JSX helper and dom-scroll-into-view, the distributed upstream package actually
supplies only an MIT declaration (and no copyright notice). Those exact
package.json/available README declarations are preserved under
third_party/frontend-declarations/. Their supplemental files explicitly
identify the standard full MIT terms as supplemental, not a recovered
copyright grant; no names/years are fabricated. There is no known omitted
copyright line in those inputs that must be invented or newly authorized.

Known FRONTEND-NOTICES obligations are CLOSED on this evidence and the
upstream project licenses. This is not an exhaustive authorship/legal warranty.
The upstream map remains a dependency lead, not proof the modified bundle
contains no other component. Unchanged inherited GPL code does not need fresh
per-file permission. No runtime library upgrade was made.

Source URLs:

- npm exact-version metadata/tarballs: https://registry.npmjs.org/NAME/VERSION
  (scoped names retain their scope). Full concrete download URLs, versions and
  archive hashes are preserved in run80 frontend/*downloads.json evidence.
- https://cdnjs.cloudflare.com/ajax/libs/qs/6.5.2/qs.min.js
- https://github.com/TaraRostami/qrious2/tree/49d72d54f872a355b349eb7ef4a0b0da43ce8ea8
- https://raw.githubusercontent.com/babel/babel/v6.26.0/LICENSE

Packaging boundary:

All original frontend runtime bytes are unchanged. run81 rebuilt both binaries
and verified that the restored AntD sidecar is actually served. Its fixed
852359bb packages contain run80 materials but NOT the run82 supplement or new
maintenance-source contract. A separately hashed matching source/material
companion must accompany those fixed payloads; do not relabel their embedded
source_commit or claim they contain later files. Include this file, LICENSES,
both notice manifests, third_party/ and the root GPL license; provide browser
recipients access to applicable notices/source. See docs/frontend-closure.md
for exact readiness and delivery conditions. Public publication is separately
unauthorized, not an outstanding version-number or modular-source defect.
