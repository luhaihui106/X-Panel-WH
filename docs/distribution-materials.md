# Distribution material closure — task t_684fddfa / run 80

Baseline: 6bd7f6a3b4f3379081b2bf324b87e1c04fec1c84. No runtime code,
GeoData, installer or production service changes. No push, main, tag or Release.

## FRONTEND-NOTICES: PARTIAL, source-side corrections saved

Restored the exact 295-byte AntD sidecar referenced by inherited JS. Added 39
full retrieved MIT/BSD/OFL notice texts and a SHA-256/source map manifest.
THIRD-PARTY-NOTICES.md maps actual files and precisely separates exact-byte,
outer-whitespace, normalized-code and project-identity evidence. In particular:
font = Vazirmatn 33.0.3 exactly; qs = cdnjs 6.5.2 exactly; datepicker JS =
@majidh1/jalalidatepicker 0.9.4 exactly; jsonlint = 1.6.3 browser file ignoring
outer whitespace. Existing embedded notices are unchanged. No library upgrade.

Remaining: AntD actual modified bundle is not npm 1.7.8 verbatim. Normalized
comparison identifies changed classnames, DOM measurement, core-js version
string and TinyColor implementation, not just different whitespace. Exact
upstream source-map modules were compared with npm source files; that map is
only a lead for the modified bundle. Several inherited dependency packages
supply MIT metadata/short README declarations but no full copyright notice in
their exact archives/commit trees (icons/icons-vue, array-tree-filter,
component-classes/indexof, JSX merge helper, dom-scroll-into-view). Do not
invent copyright names or claim the 39 texts close those unresolved modules.
Moment-jalaali release is not exactly identified; its actual two project
identities and appropriate MIT notices are supplied without false versioning.
These are materials not closed, not infringement findings. No request for
fresh permission on every unchanged GPL upstream file is implied.

## GPL-FRONTEND-SOURCE: PARTIAL, exact fork found and supplied

TaraRostami/qrious2 commit 49d72d54f872a355b349eb7ef4a0b0da43ce8ea8
and npm qrious2 5.1.1 contain the byte-identical deployed asset. Supplied the
readable 74,463-byte dist/qrious2.js with actual corner/separator changes,
original GPL/MIT headers, modular sources, original Gruntfile and lockfile.
A pinned, separate Terser build script works; 40 drawing-operation cases match
original minified, unminified and rebuilt code. Runtime bytes stay unchanged.

The inherited modular build fails, and stock qrious-core does not contain the
fork additions. Readable dist is a usable editable form but has not been
confirmed as the author's preferred form; the report does not certify full
GPL corresponding-source closure. This is not a minification/source-map
requirement imposed on every MIT library. See third_party/qrious2/README.md.
The smallest remaining source decision is accepting the exact readable fork
as the maintained editable form after GPL review, or obtaining the author's
actual modified modular inputs. Do not substitute unrelated qrious 4.0.2.

## DATA-EVIDENCE: OPEN; bounded history search finished

Superseded for new run81 candidates only: the user approved replacement A.
See docs/geodata.md and docs/geodata-lock.json for the implemented pinned
DLC/DB-IP build, labels, attribution and tests. Original historical packages
and the historical evidence below remain unchanged/unresolved. This does not
close the independent FRONTEND-NOTICES or GPL-FRONTEND-SOURCE items.

Both original dat hashes remain unchanged. Date-bounded release-branch lookup
returned no commits; four dated March tags resolve to recipe commit
b74d235f909125256d8b6d3bfbb8cf55872b8f10, whose dat checksum paths return
404. This does not prove no historical output existed, but does not map the
bundled bytes to applicable input terms. No further archaeology is proposed.

Only a functional/distribution choice remains for the data:

A. New candidate using v2fly/domain-list-community alone (MIT, GeoSite format)
plus DB-IP Country Lite only (CC BY 4.0, monthly) converted with documented
v2fly/geoip tools (CC BY-SA 4.0 for the converter). Pin source/input snapshots,
config/output and notices. Country/private routing can remain, but labels,
country assignments and coverage differ; lose aggregated provider/ASN/Tor
and special CN feeds. Check every existing referenced label before adoption.
This is the recommended functionality-preserving direction, not yet tested
or substituted. Sources:
https://github.com/v2fly/domain-list-community/blob/e8f6d1e5c4a01cda943c0784ffa834340eeab5ae/LICENSE
https://github.com/v2fly/geoip/tree/fd96fbac6cffc06ab9a10d6ee8fad61afe9b771c
https://db-ip.com/db/lite.php
https://db-ip.com/faq.php
https://creativecommons.org/licenses/by/4.0/legalcode.en

B. Do not bundle the two dat in a first release; require explicit user-supplied
licensed data, with a genuinely data-free default or disabled data-dependent
presets. This changes out-of-box country/category routing and can break
existing geoip:/geosite: rules if simply deleted. Must be chosen by the user;
not implemented. Automatic first-start fetching the same unresolved files
would not establish their rights chain.

## Frozen package impact

AMD64 x-panel-wh-25f94fca-linux-amd64.tar.gz SHA-256
5f34d06cdd6264553c0ea9650d68e9bee7b785127865c75310d1ad18ef045596 stays
unchanged. Its source archive is still 25f94fca, binary still 04b204cc;
run79's companion installer remains 6bd7f6a3. Existing ARM64 packages and
local-candidate-run79 source deliveries similarly do NOT contain this new
material commit. No old archive has been silently relabeled or refreshed.
A final separately authorized packaging step must add notices/source and
resolve data selection. Old embedded binaries still cannot serve the newly
added sidecar automatically. No public-ready assertion.

## Verification and evidence

Five focused Python material tests verify notice digests, sidecar reference,
all original frontend bytes unchanged, exact fork source/features and exact
font/qs digests. Separate Node tests exercise 40 QR drawing-operation cases.
No broad/platform/systemd/VM/fault suite or panel rebuild repeated.
Evidence: /root/.hermes/cache/scratch/xpanel-launch-20261021/distribution-run80/
Original reports and summary.json remain untouched. Downloads/build caches
stay in scratch, not staged into product source. All named runtime/data paths
are preserved; RN-5 was not contacted or changed by this run.
