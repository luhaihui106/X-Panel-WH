# qrious2 exact-fork source materials

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
build as reproducing this fork. The readable distribution source is supplied
as the practical editable form, not asserted to be the author's unpublished
preferred form. The absence of an independently confirmed preferred modular
source remains explicitly OPEN; these are exact-fork materials, not a legal
certification of GPL corresponding-source completeness.

Our separate minification path is:

    npm ci --ignore-scripts
    QRIOUS_BUILD_OUTPUT=/absolute/scratch/new-file.js npm run build
    QRIOUS_BUILD_OUTPUT=/absolute/scratch/new-file.js npm test

Build from this directory after supplying npm's pinned dependencies. Never
run the inherited upstream build in the canonical tree (its clean target
removes dist). build.cjs writes only a new explicitly named output and does
not replace the runtime asset. The minifier is Terser 5.44.0; historical
byte-for-byte minification is not claimed. Forty drawing-operation cases
compare the real runtime asset, readable fork and rebuilt output, including
Unicode, long values, four correction levels, separators, corners and setters.
This is focused behavioral evidence, not proof for every possible input.

No runtime replacement or panel rebuild is performed for these materials.
