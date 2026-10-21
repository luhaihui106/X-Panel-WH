# 本地原生候选验收与发行边界（2026-10-21）

本文件只描述本地候选，不承诺公开 Release、curl 一键入口或完整平台矩阵。

## 固定身份

- 已验收 panel 原构建源码：`04b204ccb17d501946e5f5abfa9208e6072fe5e5`。
- AMD64 固定完整包源码：`25f94fcaf9b5a210d8584456e3d1ddb1b61e62bc`。
- 包名：`x-panel-wh-25f94fca-linux-amd64.tar.gz`。
- 包 SHA256：`5f34d06cdd6264553c0ea9650d68e9bee7b785127865c75310d1ad18ef045596`。
- panel SHA256：`fa34f28bcf6879d6ee90afce61e0a2921539e75e6bfa9755e5f36b2ef6b7fe15`。
- 随包 Xray v26.3.27 SHA256：`8255dd939c34cf966cc91517b6324dd3c8d0bcf49ffac8beca049a38c46845ed`。

运行时源码从 panel 构建提交到包源码提交未变；后续修复只涉及安装器 unit、回归与文档。保留已验证二进制，不为文档重建。包内 source.tar.gz 对应包源码提交，不包含后续安装器修复；使用本文件所在修复提交的 install/native.py，不使用旧安装器。完整包不包含独立安装器入口，必须与明确标识的安装器配套交付。

panel 为 Go 1.27.0、CGO_ENABLED=1、GOAMD64=v1、GCC 11.4.0 交叉构建，依赖目标 libc；原 buildinfo 的 vcs.modified=true 已如实保留，来源记录核对运行时输入不变，不将该标志改写成干净构建声明。

## 本轮修复与实际验收

旧 unit 的 WorkingDirectory 是只读程序目录。默认 core 模板写 ./access.log 与 ./error.log，真实新库启动因此失败。修复为可写日志目录；ExecStart、DB、bin 保持绝对路径。没有放宽 ProtectSystem=strict，也没有改 panel/core。

原生 Linux AMD64 / Ubuntu 24.04 / systemd 255 上，以真实安装器 --root 生成默认目录及 unit，再将生成 unit 原字节装入临时服务。隔离附加项为 RootDirectory、私有网络/设备、只读 libc/loader 绑定、明确的数据/日志可写绑定、旧路径不可见及资源/时间限制；服务名为临时名，未 enable。未改变生成 unit 的 ExecStart、WorkingDirectory、环境或 ReadWritePaths。

真实完整 panel 与随包 core 在独立空库启动，两次 HTTP 200、SQLite quick_check=ok、1 初始用户/0 入站；stop/start 后新 PID 与持久化哨兵均核实。此为生成路径/unit 的受控真实 systemd 验收，不是主机根直接安装、不证明 enable/开机自启、断电或全平台。初次 RootDirectory 的可写映射缺失导致 SQLite 失败，补明确 BindPaths 后定位出上述真实日志缺陷；保留失败证据。

已有实例的原生二进制替换、浏览器和真实代理流量已有独立记录，本轮不重复、不冒称新装空库发生代理业务流量。ARM64 保留先前离线生命周期与运行证据；没有本轮等价原生新装 systemd/full-core 验收，不列为本轮完成的服务平台。

## 操作入口

从配套源码/交付目录执行 Python 入口；具体 install/update/restore/uninstall、路径参数、匹配备份及异常处置见 [install/README.md](../install/README.md)。默认不启动、不 enable；先限制访问，再启动并修改默认凭据。现有 x-ui/3x-ui 默认拒绝，不自动迁移。已有旧生成 unit 的独立受管安装需要先人工核对该工作目录差异，不能直接假定新 installed() 校验接受旧 unit。卸载保留数据、core 与快照。

## 公开分发前具体缺口

保留 GPLv3、xeefei/X-Panel 等来源及 Xray MPL-2.0。当前候选仅供本地受控验收，不能作为全部第三方权利已闭合的公开包。

1. bin/geoip.dat、bin/geosite.dat：精确 Xray tag workflow 从可变 Loyalsoldier release 分支/cache 取数据；固定哈希只证明字节。补足适用的数据归属/许可及必要对应来源，确认历史 GeoLite 条款；若无法识别，最小替代是另做有明确合规来源的固定数据包，而非改变现包或宣称所有数据都受 MPL 覆盖。
2. 前端 notices：antd.min.js 指向缺失的 antd.min.js.LICENSE.txt；补实际继承 bundle 的 MIT/BSD/OFL 归属全文，包含依赖及 Vazirmatn 字体。不要仅用项目名推导未知版本。原 antd 与 npm 同版本字节不同，不以同版 sidecar 冒充完整闭合。
3. qrious2.min.js：有 GPLv3 与 fork 版权头，但实际 fork 的首选修改源码及必要构建材料未在包中证实；补实际对应源码/合规提供方式，不以不同 fork 的链接替代。

这些是具体证据/材料缺口，不是侵权判决，也不要求全部未变上游文件重新授权。保留候选、全部原证据与用户备份；禁止 push/main/公开 Release，公开发布须另获授权并关闭上述具体缺口。

## run80 定点补充（不重打包）

已恢复源码中的 AntD 同名 sidecar，补 39 份完整前端许可正文与实际文件映射；找到字节完全相同的 qrious2 5.1.1 / TaraRostami 精确提交，加入可读 fork、原构建材料和独立可工作的压缩脚本，40 项绘图操作对比通过。所有旧前端运行文件字节保持，面板及已测包未重建，线上未触碰。

上述两项为实质补齐但仍 PARTIAL：修改过的 AntD 内嵌依赖 notice 覆盖尚有小范围缺口；qrious2 原模块源码未包含 fork 修改，不能仅凭可读 dist 和行为对比冒称已证实作者首选源码完整。GeoData 一轮有界历史查询未能证明固定数据的适用来源/条款，停止考古；需用户选择明确许可的新固定数据（MIT DLC + DB-IP-only，覆盖/更新有差异）或首次发行不随附而明确安装。均未擅自替换/删除。详见 [distribution-materials.md](distribution-materials.md) 与 [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md)。现有 25f94fca 包/source 和 run79 交付目录均不含这些新材料，不称 public ready。
