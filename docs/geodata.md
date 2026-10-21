# Licensed GeoData snapshot (t_c186d284 / run81)

The approved replacement is DLC-only GeoSite and DB-IP Country Lite October
2026 plus v2fly private networks. No historical Xray ZIP dat is packaged.
The independent data lock is docs/geodata-lock.json. Build-package.py requires
--geodata-dir containing the exact two dat and full NOTICE; wrong/old bytes,
missing/modified notices and missing referenced labels fail closed.

Sources and reproduction

- DLC e8f6d1e5c4a01cda943c0784ffa834340eeab5ae (MIT, V2Ray copyright),
  codeload snapshot hash in lock. Build with its unmodified go.mod/go.sum:
  go build -o dlc .; dlc -datapath data -outputdir OUTPUT -outputname geosite.dat
- v2fly/geoip fd96fbac6cffc06ab9a10d6ee8fad61afe9b771c (CC BY-SA4.0),
  go build -o geoip .; geoip -c geoip-config.json. Only dbipCountryMMDB and
  private inputs, v2rayGeoIPDat output; no test/MaxMind/ASN/provider feeds.
- DB-IP Country Lite 2026-10 MMDB (CC BY4.0), official download HTTP403;
  jcjc-dev/mmdb-latest dbip-latest mirror asset retrieved and SHA256 pinned.
  Mirror API digest matches. Uncompressed MD5 b8647f712bcabbe01f8afe3ff9e7569e
  and SHA1 e515b63075ad48847f9c4332b724742e8ba15b0e match the official
  download-page values independently retrieved by web search. These are
  integrity/identity evidence, not a publisher-signature claim.
- Full original notices and CC legalcodes: LICENSES/geodata. Converter
  software terms do not automatically license its output. DB-IP country input
  keeps CC BY4.0; copied private definitions keep CC BY-SA4.0. Combined GeoIP
  adaptation is conservatively distributed under CC BY-SA4.0, retaining
  underlying attribution/terms. No assertion this relicenses panel code.
- Original archives, MMDB, converter source, config, retrieval metadata and
  built data are retained together in the local run81 delivery source bundle.
  Toolchains used: DLC Go1.25.12, GeoIP Go1.26.0 (auto-resolved module tools).

Compatibility

All 24 distinct geoip:/geosite: labels actually referenced by settings.html,
xray.html and default service config exist and pass Xray v26.3.27 run -test.
252 IP groups and 1549 site groups were generated. No aliases or deleted
rules needed. RN-5 read-only saved and active config references only
geoip:private; no data/config/service writes were performed there.

Country assignments, category coverage and monthly updates differ from the
old merged feed; aggregated ASN/provider/Tor labels are not promised. In
particular CN is DB-IP geography, not a special CN feed. This is the approved
functional difference, not drop-in semantic identity.

Nine ext:* references in the advanced editor are separate operator-supplied
regional files, not groups in either replaced base dat. The previous native
package already omitted these optional files. They remain unchanged and must
be explicitly installed under their own terms before selecting those rules.
No external label is silently mapped to a non-equivalent base country/list;
no claim the regional malware/phishing/cryptominer lists are replaced by DLC.

DB-IP attribution link is included in desktop/mobile sidebar. This and the
previously restored AntD sidecar are embedded assets, so both panel binaries
must be rebuilt; old 04b204cc binaries are not relabeled as containing them.
The native installer remains the tested 6bd7f6a3 implementation. New packages
include current tracked source and full data NOTICE. This data closure does
not close the separate modified AntD notices / qrious2 preferred-source issues
recorded in docs/distribution-materials.md, and is not public-release approval.
