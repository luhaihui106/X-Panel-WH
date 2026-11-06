# v26.9.13-wh.2 安全发行：安装、更新与恢复

基于上游免费 v26.9.13，继续保留 wh.1 的功能；不是 Pro 解锁版。

## 安全修复与边界

面板模块固定 `github.com/xtls/xray-core v1.260327.1-0.20260710210335-64fada32b5b9`（官方修复 commit `64fada32b5b9e6ae064a038fa0e4e2b766499bd5`），修复 GHSA-5wf9-h793-w73c 的 CA pinning 身份校验问题。本版包含同样已修复的独立 Xray v26.7.11 核心（源码 `50231eaff98ccc31b5cbd247a721c16e97fe5ec1`），版本、来源和摘要以 `delivery-binding.json` 为准，不能仅凭面板 go.mod 宣称核心已修复。

REALITY 服务端默认最低客户端版本改为 **26.3.27**，更旧客户端可能被拒绝；升级前确认客户端覆盖。本次修复 GHSA-5wf9-h793-w73c，不保证修复此后的全部漏洞。固定 CA 但没有有效校验名称的连接升级后会拒绝；应正确设置 serverName/目标名称，不得靠跳过证书校验兼容。本版本不更换线上服务或配置。程序内部版本可能仍为 26.9.13，派生身份看 manifest、源码 SHA 与此发行。

Linux amd64/arm64，Python 3.10+、systemd、curl、**glibc >= 2.34**。交叉编译或 QEMU 验证不代表原生 systemd 全链路和全发行版兼容性。

## 下载与核验

新建私有目录，从本版 Release 下载全部资产（不要执行继承的 install.sh/x-ui.sh）：

```sh
mkdir -m 700 x-panel-wh-v26.9.13-wh.2
cd x-panel-wh-v26.9.13-wh.2
gh release download v26.9.13-wh.2 -R luhaihui106/X-Panel-WH
sha256sum -c SHA256SUMS
```

必须同时保存两架构包、`native.py`、`INSTALL.zh-CN.md`、完整源码/许可 companion、GeoData 输入/源码、独立核心源码、`delivery-binding.json` 与 `SHA256SUMS`。GitHub 自动 Source code 不能代替全套。SHA256 只验证内容一致，不是数字签名。包名按**新构建源码 SHA**生成，不沿用 852359bb 或 wh.1 摘要。

## 安装与更新

检查安装器源码、防火墙、备份与摘要后，用绑定文件挑选当前主机的真实包名和摘要：

```sh
ARCH=$(uname -m)
case "$ARCH" in x86_64) ARCH=amd64;; aarch64|arm64) ARCH=arm64;; *) exit 1;; esac
PACKAGE=$(python3 -c 'import json,sys; b=json.load(open("delivery-binding.json")); print(next(x["filename"] for x in b["payloads"] if x["arch"]==sys.argv[1]))' "$ARCH")
SHA256=$(python3 -c 'import json,sys; b=json.load(open("delivery-binding.json")); print(next(x["sha256"] for x in b["payloads"] if x["arch"]==sys.argv[1]))' "$ARCH")
# 全新安装，不覆盖已有 x-ui/3x-ui：
sudo python3 native.py install --package "$PWD/$PACKAGE" --sha256 "$SHA256"
# 已经由 native.py 管理的同路径独立安装：用下面一条替代 install
# sudo python3 native.py update --package "$PWD/$PACKAGE" --sha256 "$SHA256"
```

安装不自动启动/enable。先限制默认 13688 管理入口为管理源或 SSH 隧道，配置 HTTPS/反代；启动后立即更改空库默认 admin/admin，再核对面板、核心和数据库。unit 为 `x-panel-wh.service`，默认路径 `/usr/local/lib/x-panel-wh`、`/var/lib/x-panel-wh`、`/var/log/x-panel-wh`。

update 会停服务并备份程序、独立核心/配置、SQLite 一致快照和 unit；已有 unit 不匹配不得绕过检查。恢复用 `sudo python3 native.py restore --backup /var/lib/x-panel-wh/backups/实际ID`，会回退业务状态，且可能恢复有漏洞的旧核心，仅限明确接受风险的故障恢复。恢复失败或 pending/stage 残留时停止盲重试。无断电/零流量损失保证。见 [安装器契约](../install/README.md)。

## 许可与源码

部署者应向浏览器用户显著提供本版 `THIRD-PARTY-NOTICES.md`、完整源码/许可 companion、独立 Xray MPL 来源与 GeoData 输入/转换源码链接；这些资产必须在旧版删除后仍可获取。新包嵌入当前完整源码，但不能据此省略外部数据输入或独立核心源码。GeoData 保持固定锁定来源，见 [GeoData](geodata.md)。
