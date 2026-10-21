# X-Panel-WH 最小原生候选交付

当前只支持 Linux ARM64，Python 3.10+、systemd、SQLite（Python 标准库）和 HTTPS 下载时的 curl。面板候选是 Go 1.27.0 linux/arm64 CGO 本机构建，不承诺静态跨发行版兼容。本工具不执行继承的 install.sh/x-ui.sh，不自动查询 latest，不创建公开 URL。

## 固定本地包

在仓库根执行（PACKAGE 与 SHA256 替换成已核实的绝对路径和完整摘要）：

```sh
python3 install/native.py install --package "$PACKAGE" --sha256 "$SHA256"
```

真实主机流程需要 root 和运行中的 systemd；默认安装后不启动、不 enable，避免默认凭据立即暴露。先限制防火墙/反代访问，再执行 `systemctl start x-panel-wh.service`，验证本地登录并更改默认凭据，确认服务/真实代理流量后再 `systemctl enable x-panel-wh.service` 和开放入口。保留数据库初始化的上游 admin/admin 契约，不添加首次初始化产品流程。程序内部版本仍是上游版本；派生候选身份看包 manifest、源码提交和 SHA256。

默认路径：

- 程序 /usr/local/lib/x-panel-wh/x-panel
- 服务 /etc/systemd/system/x-panel-wh.service
- 数据库 /var/lib/x-panel-wh/db/x-ui.db
- core /var/lib/x-panel-wh/bin/xray-linux-arm64
- 生成的 core 配置 /var/lib/x-panel-wh/bin/config.json
- geoip.dat/geosite.dat 同 bin 目录
- 日志 /var/log/x-panel-wh
- 匹配恢复快照 /var/lib/x-panel-wh/backups/<随机ID>

可显式设置 --install-dir、--data-dir、--log-dir，后续每次生命周期调用必须使用相同值；只允许互不重叠的绝对规范路径，不允许空格、systemd 转义或符号链接。目录创建使用 0700，服务 UMask=0077。服务沿用 root（core 低端口/网络能力），不偷偷创建账户；本工具不是非 root 运行改造。自定义 core 模板引用上述根以外的文件/证书/日志时，必须先人工核对 ProtectSystem/ProtectHome 和额外备份策略；不会自动收集外部秘密。

已有程序、数据、日志、服务目的地均拒绝；发现已知 x-ui/3x-ui 安装也拒绝，不自动迁移或覆盖。RN-5 如果仍是历史 x-ui 路径，必须由后续已授权部署步骤停写、保护原实例并明确迁移，不能直接用本工具绕过保护。

全新独立安装不提供 `/usr/bin/x-ui` 兼容脚本。继承的 Telegram“重启面板”和订阅转换安装仍可能依赖该脚本，在本安装路线当前不可用；本轮不实现兼容脚本。请在主机使用 `systemctl restart x-panel-wh.service` 重启面板，使用 `systemctl status/start/stop x-panel-wh.service` 查看或管理服务；这不替代订阅转换安装功能。

包为严格白名单 x-panel-wh/ 根下常规文件：x-panel、bin/xray-linux-arm64、bin/{geoip,geosite}.dat、LICENSE、NOTICE、xray-LICENSE、xray-README.md、source.tar.gz、manifest.json。拒绝重复、缺失、额外、错误架构、链接、特殊文件和危险路径。外部 --sha256 必填；manifest 再逐文件校验。摘要检测损坏，不等同发布者签名。

未来公开资产准备好后可用 `--url https://.../固定版本/固定资产.tar.gz --sha256 ...` 替代 --package。只接受显式 HTTPS，curl 开启证书/TLS 校验，重定向也只允许 HTTPS；不允许 latest、查询参数或 URL 凭据。这里没有可用的公开安装下载承诺。

## 更新、恢复、卸载

```sh
python3 install/native.py update --package "$PACKAGE" --sha256 "$SHA256"
python3 install/native.py restore --backup /var/lib/x-panel-wh/backups/实际ID
python3 install/native.py uninstall
```

update/restore/uninstall 是显式停服务操作。停服务成功后先保存程序、完整 bin（含配置）、SQLite backup API 一致快照、其他 db 目录文件、服务定义和摘要/权限清单。SQLite 快照包括已提交 WAL 数据，并转为 DELETE journal 便于离线校验。更新失败会停止候选并恢复匹配程序/DB/core/config/unit，然后尝试启动旧版；恢复再次失败时返回非零并保留 pending 标记和快照，禁止盲重试。

显式 restore 会先备份当前状态，再恢复所选完整快照。恢复会回退快照后的业务状态，不保证停机前内存计数零损失。备份不是认证签名，信任独占 root 操作者和不可被其他用户写入的管理目录。不抵抗恶意同 UID/root 进程替换文件。

卸载先快照、停止并 disable 服务、删除程序和本工具服务定义，保留 DB、bin/config、全部快照和日志；不提供 purge。再次 install 因遗留数据默认拒绝。未知操作（含自动 recover）明确拒绝。

.operation-pending 保留中断证据；不提供断电日志恢复保证。进程在目录替换中被强杀可能留下 .x-panel-wh-stage-* 或 .x-panel-wh-old-*，不自动清除。常规异常路径已测试自动恢复；强杀/断电后先停服务，核对快照/程序/DB/unit，若安装收据和路径完整可显式 restore，否则由操作者按快照匹配恢复并保留故障证据。不得删除 pending 标记后盲目重试。没有完整有效快照的初装中断需要人工核对后恢复，不会自动删除数据。

## 安全测试与证据层级

```sh
TMPDIR=/root/.hermes/cache/scratch PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s install -p test_native.py -v
python3 install/native.py install --root /已有/scratch/synthetic-root --package "$PACKAGE" --sha256 "$SHA256"
```

--root 必须为非 / 的真实目录，完全离线，不调用账户/systemctl、不执行面板或 core。测试覆盖默认/自定义目录、布局/摘要/架构失败、旧安装保护、更新/匹配恢复、WAL、服务启动失败自动恢复、保留数据卸载、HTTPS 参数和 pending 拒绝。合成 ELF 只用于安装器测试，不能冒充真实构建。服务 is-active 不是 HTTP/认证/core 流量健康证据；真实 systemd 启停、浏览器 JS、core 流量与 RN-5 验收由后续阶段完成。

## 生成私人候选

`build-package.py` 只接受已记录摘要的 ARM64 面板，以及固定 Xray v26.3.27 原始 ZIP（内置 ZIP 摘要锁）；不执行面板/core。对应源码用 Git 受跟踪提交归档，排除 .hermes、summary.json、DB、日志和本地证据。必须从已提交且与已验收面板源码一致的提交打包；打包器不声称仅凭调用者提供的摘要即可证明构建来源。

```sh
python3 -B install/build-package.py --panel /已验收/panel --panel-sha256 完整摘要 --xray-zip /固定/Xray-linux-arm64-v8a.zip --version 本地固定版本 --output /scratch/固定资产.tar.gz
```

保留 GPL/上游署名，包含原始 Xray MPL LICENSE/README、源代码及 NOTICE。前端/data 等最终再分发核查属于后续公开发行阶段；本包只是本地测试候选，不是公开 Release 或许可结论。不得 push/main/Release/部署作为本脚本副作用。
