# qrious2 maintained corresponding source — run82, 2026-10-21

The runtime asset is unchanged. Its SHA-256 is
2303386046f790f19339ec1b161ac2edfd45d31ba7f8060dc3779745fdc4e7ce.
It equals dist/qrious2.min.js in TaraRostami/qrious2 commit
49d72d54f872a355b349eb7ef4a0b0da43ce8ea8 and npm qrious2 5.1.1.
The header's 5.0.0 is not the npm package version.

Source: https://github.com/TaraRostami/qrious2/tree/49d72d54f872a355b349eb7ef4a0b0da43ce8ea8
Unminified fork source: upstream/dist/qrious2.js, SHA-256
528afc4d52510d19ac39fc957c94e8dc8c3e8aff3d8925e7c04133c9ae4ff219.
The file contains the fork's actual custom drawing/options, readable function
names, comments and embedded notices, including Nevis's MIT notice.
All original copyright/license statements remain intact. Root LICENSE and
upstream/LICENSE.md supply GPLv3. The upstream file allows GPLv3 or later.

Upstream's modular src/QRious.js imports stock qrious-core@4.0.0 and does not
carry the fork changes present in dist/qrious2.js. Its preserved Gruntfile
still emits qrious.*, not qrious2.*. The original npm build fails with
"You must supply output.name for UMD bundles". Do not represent that modular
build as reproducing this fork.

X-Panel-WH now maintains src/qrious2.js as its preferred editable source.
It is initially byte-identical to the readable exact fork above, not a
decompilation or stock 4.x replacement. Make future QR implementation edits
there, review them, then build with build.cjs. That script actually consumes
this file (including edits), reports its input digest and uses the pinned
package-lock.json/Terser toolchain. The historical upstream/ tree is preserved
only as provenance; its broken modular build is not a required build input.

Downstream modification notice, 2026-10-21: X-Panel-WH adopted the existing
readable fork as its maintained source and added a working pinned minifier
and tests; no QR implementation or original runtime bytes were changed.
Retain original copyright, GPLv3-or-later and embedded Nevis MIT statements
when editing or distributing. Root LICENSE supplies the complete GPLv3 text.

For this project's maintenance and source delivery, the source-material item
is CLOSED: the shipped implementation is present in readable editable form,
with all actual standalone build inputs and instructions. The original fork
author's private workflow is unknown, not asserted to have been recovered;
GPL does not intrinsically require modular files or the historical minifier.
This is a documented engineering/source-delivery assessment, not a legal
warranty or an assertion that every possible QR input was tested.

Our separate minification path is:

    npm ci --ignore-scripts
    QRIOUS_BUILD_OUTPUT=/absolute/scratch/new-file.js npm run build
    QRIOUS_BUILD_OUTPUT=/absolute/scratch/new-file.js npm test

Build from this directory after supplying npm's pinned dependencies. Never
run the inherited upstream build in the canonical tree (its clean target
removes dist). build.cjs writes only a new explicitly named output and does
not replace the runtime asset. The minifier is Terser 5.44.0; historical
byte-for-byte minification is not claimed. Forty drawing-operation cases
compare the real runtime asset, maintained readable source and rebuilt output, including
Unicode, long values, four correction levels, separators, corners and setters.
This is focused behavioral evidence, not proof for every possible input.

The output is reproducible with the locked toolchain; it is not byte-identical
to the inherited runtime's historical minification. Deliver the original
runtime, src/, build.cjs, package.json, package-lock.json, test.cjs, this README,
upstream provenance and GPL license together. No runtime replacement or panel
rebuild is performed for these materials.
