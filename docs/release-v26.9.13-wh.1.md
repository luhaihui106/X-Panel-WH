# v26.9.13-wh.1 安装、更新与恢复

[正式发行及完整资产](https://github.com/luhaihui106/X-Panel-WH/releases/tag/v26.9.13-wh.1) · [源码](https://github.com/luhaihui106/X-Panel-WH/tree/v26.9.13-wh.1) · [第三方声明](https://github.com/luhaihui106/X-Panel-WH/blob/v26.9.13-wh.1/THIRD-PARTY-NOTICES.md)

## 版本与支持范围

首个完整社区派生发行，基于上游免费 v26.9.13：客户端独立月重置、移除自动推广与脚本广告、清理 Telegram 抽奖/美图等娱乐入口，保留管理员管理与用户自行配置的通知。不是 Pro 解锁版。

本次直接发布已经验证的固定载荷，不重新构建或修改旧包：

- AMD64：`x-panel-wh-852359bb-linux-amd64.tar.gz`，SHA256 `0f7568f2b9fdbedef52d273b658127b78783855f6ce3f2c7e14aa63ab8be278c`。
- ARM64：`x-panel-wh-852359bb-linux-arm64.tar.gz`，SHA256 `e1dc0b712679d7b3d6632229dbb0923485178b2592e997fe6b3d6714e6fd7297`。
- 两架构载荷/二进制构建源码：`852359bb5f9265003243c2d0300d9e4fe12b9229`；完整源码/许可 companion：`10829d28da38ab252cfb40054fd8cd604a7f9c2a`。发行 tag 还包含后续安装说明，不冒称旧载荷嵌入了这些材料。
- 必须配套保存 `x-panel-wh-source-materials-10829d28.tar.gz`、`geodata-inputs-and-source-run81.tar.gz`、`delivery-binding.json`、`SHA256SUMS`。GitHub 自动 source.zip 不能替代此完整材料集合。`native.py` 是与固定载荷配套的真实安装器，不是继承的上游 install.sh。

Linux AMD64/ARM64、Python 3.10+、systemd、curl、可用的目标 libc。AMD64 已在原生 Ubuntu 24.04/systemd 255 做受隔离的生成 unit、空库、完整 core、HTTP/SQLite、停启持久化验收；两架构固定包有独立运行/HTTP/SQLite/署名验证。ARM64 未做等价的原生新装 systemd 全链路验收。没有全发行版、主机重启、断电或 Docker/Windows 支持承诺；QEMU/隔离验收不等于所有真实主机安装通过。

## 下载与核验

在新的私有工作目录中操作，不要直接管道执行网络脚本。以下下载两架构及必需材料，方便完整校验、存档和再分发（约数百 MB）：

```sh
mkdir -m 700 x-panel-wh-v26.9.13-wh.1
cd x-panel-wh-v26.9.13-wh.1
BASE=https://github.com/luhaihui106/X-Panel-WH/releases/download/v26.9.13-wh.1
for FILE in SHA256SUMS native.py INSTALL.zh-CN.md delivery-binding.json x-panel-wh-852359bb-linux-amd64.tar.gz x-panel-wh-852359bb-linux-arm64.tar.gz x-panel-wh-source-materials-10829d28.tar.gz geodata-inputs-and-source-run81.tar.gz; do
  curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 -O "$BASE/$FILE" || exit 1
done
sha256sum -c SHA256SUMS
```

SHA256 校验检测损坏，不是发布者数字签名；此版不提供签名。检查安装器源码，确认主机架构、依赖、防火墙及恢复策略后再安装。

## 全新安装

以下为真实 CLI；只能用于没有现有面板目的地的新安装，不能用于接管已有 x-ui/3x-ui。默认路径为 `/usr/local/lib/x-panel-wh`、`/var/lib/x-panel-wh`、`/var/log/x-panel-wh`，服务 `x-panel-wh.service`。程序内部版本仍为 26.9.13，派生身份以本发行与 manifest 为准。

AMD64 主机：

```sh
sudo python3 native.py install --package "$PWD/x-panel-wh-852359bb-linux-amd64.tar.gz" --sha256 0f7568f2b9fdbedef52d273b658127b78783855f6ce3f2c7e14aa63ab8be278c
```

ARM64 主机：

```sh
sudo python3 native.py install --package "$PWD/x-panel-wh-852359bb-linux-arm64.tar.gz" --sha256 e1dc0b712679d7b3d6632229dbb0923485178b2592e997fe6b3d6714e6fd7297
```

安装后不自动启动或 enable。先限制面板入站为管理来源或 SSH 隧道，确认端口（默认 13688）和 HTTPS/反代，再 `sudo systemctl start x-panel-wh.service`。上游空库默认 admin/admin，首次受限登录后立即修改用户名和密码。核对面板、core、数据库与真实代理业务，再 `sudo systemctl enable x-panel-wh.service`。不要先向公网开放默认凭据。

已有安装、数据、日志或服务均拒绝，不覆盖、不自动迁移。自定义路径须每次调用都使用相同的 `--install-dir`、`--data-dir`、`--log-dir`。不要执行继承的 install.sh/x-ui.sh 更新，会转向上游。Telegram 重启面板及订阅转换安装中依赖 `/usr/bin/x-ui` 的旧功能不在此原生安装路线提供；用 systemctl 管理面板。

## 更新与匹配恢复

仅对已经由此安装器管理、路径和生成 unit 一致的独立安装使用 update；没有新版本时不要为“升级”重复安装相同载荷。未来版本先完整下载其固定包与必需材料，校验该版本真实摘要后：

```sh
sudo python3 native.py update --package "$PACKAGE" --sha256 "$SHA256"
sudo python3 native.py restore --backup /var/lib/x-panel-wh/backups/实际ID
sudo python3 native.py uninstall
```

update/restore/uninstall 会停服务，保存程序、core/配置、SQLite 一致快照及 unit；失败尝试匹配恢复并启动旧版。restore 会回退快照后的业务状态，不能保证内存流量零损失。卸载保留数据、core、日志和快照，不 purge。存在 pending/遗留 stage 或恢复再次失败时停止盲重试，保留故障证据；没有断电自动恢复保证。已有旧 unit 与新 unit 不一致时必须人工核对，不强行绕过检查。细节见 [安装器说明](../install/README.md)。

## 给浏览器用户提供声明与源码

固定载荷包含之前的嵌入式前端，但补全后的声明和可编辑 qrious2 构建材料在独立 companion 中。部署者应在面板入口、使用说明或自己的分发页面显著提供以下公开链接，并与载荷一起保持可用：

- [GPL 与第三方声明](https://github.com/luhaihui106/X-Panel-WH/blob/v26.9.13-wh.1/THIRD-PARTY-NOTICES.md)
- [完整源码、许可及 QR 可编辑构建材料](https://github.com/luhaihui106/X-Panel-WH/releases/download/v26.9.13-wh.1/x-panel-wh-source-materials-10829d28.tar.gz)
- [GeoData 输入、转换源码与声明](https://github.com/luhaihui106/X-Panel-WH/releases/download/v26.9.13-wh.1/geodata-inputs-and-source-run81.tar.gz)

保留 GPLv3、上游署名、Xray MPL 及第三方 notices。GeoSite 来自固定 MIT DLC；GeoIP 为 DB-IP Country Lite/私网转换，保留 CC BY 4.0 署名。与旧聚合数据的覆盖、标签和国家归属可能不同，不包含原 provider/ASN/Tor 等特定数据，不承诺自动更新。详见 [GeoData](geodata.md) 与 [前端材料](frontend-closure.md)。

发布不等于部署：本次不替换任何现有服务器程序或业务数据。
