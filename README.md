# X-Panel-WH

基于 [xeefei/X-Panel](https://github.com/xeefei/X-Panel) 的 Xray 管理面板，管理代理入站、客户端和流量。

[下载安装](docs/release-v26.9.13-wh.1.md) · [最新发行](https://github.com/luhaihui106/X-Panel-WH/releases/tag/v26.9.13-wh.1) · [English](README.en.md) · [文档](docs/README.md)

## 功能

- 管理 VLESS、VMess、Trojan、Shadowsocks 入站，配置传输及适用的 TLS/Reality 选项。
- 为客户端分别设置流量额度、到期时间和启用状态，查看用量、在线状态与最近活动。
- 生成连接链接、二维码和订阅，导入/导出入站 JSON 配置。
- 查看系统资源、日志与 Xray 状态，停止或重启核心。
- 下载/恢复面板数据库，导出 Xray 配置，配置 Telegram 通知与数据库备份发送。

## 本版改动

- 客户端各自设置每月流量重置日（1–31 日），默认关闭；短月取月末，保留累计流量。
- 删除首页自动推广和脚本广告。
- 删除 Telegram 抽奖、美图等娱乐及推广入口，保留管理员操作和用户自行配置的通知；移除硬编码外报。

基于上游免费版，不包含 Pro 多服务器管理、远程备份等付费功能。

## 安装与更新

当前版本：[v26.9.13-wh.1](https://github.com/luhaihui106/X-Panel-WH/releases/tag/v26.9.13-wh.1)。提供 Linux amd64、arm64 安装包，需要 Python 3.10+、systemd、curl 和兼容的 libc。

按[中文安装说明](docs/release-v26.9.13-wh.1.md#下载与核验)下载并校验文件后，在下载目录执行（amd64）：

```sh
sudo python3 native.py install --package "$PWD/x-panel-wh-852359bb-linux-amd64.tar.gz" --sha256 0f7568f2b9fdbedef52d273b658127b78783855f6ce3f2c7e14aa63ab8be278c
```

arm64 命令、下载步骤与更新/恢复方法见[安装说明](docs/release-v26.9.13-wh.1.md)。安装后不会自动启动或设置自启；先限制管理入口访问，再启动服务并修改初始账号密码。

amd64 新装在 Ubuntu 24.04 上验证；arm64 安装包已验证运行，原生 systemd 新装流程尚未完整验证。其他发行版请先测试，详见[平台说明](docs/compatibility.md)。

## 界面预览

以下为隔离环境的演示截图，客户端使用示例数据。[截图说明](docs/screenshots/README.md)

<details>
<summary>查看仪表盘、客户端、月重置和手机布局</summary>

### 系统仪表盘

![系统仪表盘：隔离演示](docs/screenshots/dashboard.png)

### 入站与客户端列表

![入站与客户端列表：演示数据](docs/screenshots/clients.png)

### 每月流量重置设置

![客户端月重置编辑窗口：31 日](docs/screenshots/monthly-reset.png)

### 手机布局

<a href="docs/screenshots/mobile.png"><img src="docs/screenshots/mobile.png" alt="手机布局：隔离演示长图" width="300"></a>

</details>

## 如何使用客户端月重置

1. 在「面板设置」确认时区，例如 `Asia/Shanghai`。
2. 在「入站列表」展开客户端，打开编辑窗口。
3. 开启「每月流量重置」，填写重置日（1–31）并保存。每个客户端可设不同日期。

从下一周期开始，流量任务在指定日期零点后执行；31 日遇短月取月末。刚开启或改日期不会补做旧周期，核心停止时等待恢复。

月重置只清零周期上传/下载用量，保留累计流量，不延长有效期，也不会启用手动禁用或已过期客户端。[详细说明](docs/downstream-monthly-reset.md)

## 常见问题

- 已有 x-ui/3x-ui 能直接覆盖吗？不能。安装器会拒绝已有安装，迁移前须备份并单独验证。
- 能用上游脚本更新吗？不要执行仓库继承的 `install.sh`、`x-ui.sh` 更新，会转向上游并覆盖本版功能。请用配套 `native.py`，见[更新与恢复](docs/release-v26.9.13-wh.1.md#更新与匹配恢复)。
- 有 Docker 镜像吗？目前没有本项目的 Docker 发行版。

## 许可与致谢

遵循 [GPL v3](LICENSE)，感谢 [xeefei/X-Panel 及上游项目](docs/credits.md)。再分发请保留配套源码和许可声明；部署时也请向浏览器用户提供[第三方声明](THIRD-PARTY-NOTICES.md)与[源码材料链接](docs/release-v26.9.13-wh.1.md#给浏览器用户提供声明与源码)。[GeoData 来源](docs/geodata.md) · [前端源码与许可](docs/frontend-closure.md)
