# 🐯 虎哥API反代

<p align="center">
  <img src="resources/mascot.png" alt="虎哥API反代" width="200">
</p>

<p align="center">
  <strong>Cloudflare 反向代理 IP 优选工具</strong>
</p>

<p align="center">
  <a href="#-功能特点">功能特点</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-使用说明">使用说明</a> •
  <a href="#-下载">下载</a>
</p>

<p align="center">
  <a href="https://github.com/wangwingzero/tiger-api-proxy/releases"><img src="https://img.shields.io/github/v/release/wangwingzero/tiger-api-proxy?style=flat-square&color=blue" alt="Release"></a>
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.8+-green?style=flat-square" alt="Python">
  <a href="https://github.com/wangwingzero/tiger-api-proxy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/wangwingzero/tiger-api-proxy?style=flat-square&color=orange" alt="License"></a>
  <a href="https://github.com/wangwingzero/tiger-api-proxy/stargazers"><img src="https://img.shields.io/github/stars/wangwingzero/tiger-api-proxy?style=flat-square" alt="Stars"></a>
</p>

---

帮助你找到最快的 Cloudflare 节点 IP，自动配置 hosts 文件优化访问速度。

## ✨ 功能特点

- 🚀 **IP 测速** - 自动测试多个 Cloudflare IP 的 TCP 延迟和丢包率，找出最稳定节点
- 📥 **V2Ray 导入** - 支持从 vless/trojan/vmess 链接批量导入 IP 地址
- 📊 **效果对比** - 对比你的反代与公共服务（宁波节点、BetterClaude 等）的延迟
- 📝 **Hosts 管理** - 一键修改系统 hosts 文件，无需手动编辑
- 🔍 **Hosts 查看器** - iOS 风格界面，查看和管理所有 hosts 配置
- 💾 **配置持久化** - 自动保存配置，下次启动自动加载
- 🔐 **管理员权限** - 自动请求管理员权限，安全修改系统文件

## 📸 界面预览

主界面包含：
- 目标反代节点配置
- CF 反代域名配置  
- 优选 IP 管理（测速、应用、删除）
- 状态显示和 Hosts 查看器入口

## 📥 下载

前往 [Releases](https://github.com/wangwingzero/tiger-api-proxy/releases) 下载最新版本的 `虎哥API反代.exe`

## 🚀 快速开始

### 方式一：直接运行 EXE（推荐）

1. 下载 `虎哥API反代.exe`
2. 双击运行，允许 UAC 管理员权限请求
3. 开始使用！

### 方式二：从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python run.py
```

## 📖 使用说明

### 1. 配置目标节点

在「目标反代节点」区域输入你的 API 节点地址，如 `anyrouter.top`

### 2. 配置 CF 反代域名

在「CF 反代配置」区域输入反代域名，支持两种格式：
- 完整 URL：`https://betterclau.de/claude/anyrouter.top`
- 仅域名：`betterclau.de`

### 3. IP 测速

1. 在「优选 IP 管理」区域可以看到预设的 Cloudflare IP
2. 点击「📥 导入」可从 V2Ray 链接批量导入 IP（支持 vless/trojan/vmess）
3. 点击「开始测速」测试所有 IP 的延迟
4. 测速完成后，IP 会按延迟从低到高排序

### 4. 应用最佳 IP

点击「应用最佳 IP」将延迟最低的 IP 写入 hosts 文件

### 5. 效果对比（新功能）

1. 点击「开始对比」测试你的反代与公共服务的延迟
2. 对比结果包括：
   - 你的反代（直连）- 作为基准
   - 你的反代（优选IP）- 使用测速最佳 IP
   - 公共服务（上海节点、宁波节点、AnyRouter、BetterClaude）
3. 结果按延迟排序，显示相对基准的提升百分比
4. 点击「管理服务」可添加/删除对比服务

### 6. 查看 Hosts 配置

点击「📋 查看 hosts」打开 iOS 风格的 Hosts 查看器：
- 查看所有已配置的 hosts 条目
- 搜索过滤域名或 IP
- 删除单个或全部条目

## 🔧 打包说明

如需自行打包 EXE：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 方式一：使用打包脚本
build.bat

# 方式二：使用 spec 文件
pyinstaller cf_proxy_manager.spec
```

打包后的 EXE 位于 `dist` 目录。

## 📁 项目结构

```
├── run.py                    # 程序入口
├── config.json               # 配置文件（自动生成）
├── requirements.txt          # Python 依赖
├── build.bat                 # 打包脚本
├── cf_proxy_manager.spec     # PyInstaller 配置
├── resources/                # 资源文件
│   ├── icon.ico              # 应用图标
│   └── mascot.png            # 吉祥物
└── cf_proxy_manager/         # 主程序包
    ├── main.py               # 入口模块
    ├── gui_ctk.py            # 主界面（CustomTkinter）
    ├── hosts_viewer.py       # Hosts 查看器
    ├── hosts_manager.py      # Hosts 文件操作
    ├── speed_tester.py       # IP 测速（含丢包率检测）
    ├── comparison_tester.py  # 效果对比测试
    ├── service_manager.py    # 对比服务管理
    ├── v2ray_parser.py       # V2Ray 链接解析
    ├── config_manager.py     # 配置管理
    ├── parsers.py            # URL/IP 解析
    ├── admin_helper.py       # 管理员权限
    ├── models.py             # 数据模型
    ├── logger.py             # 日志系统
    └── components/           # UI 组件
        ├── theme.py          # 主题配置
        ├── ip_card.py        # IP 卡片
        ├── comparison_card.py    # 对比结果卡片
        ├── comparison_section.py # 对比区域
        └── import_dialog.py  # V2Ray 导入对话框
```

## ⚠️ 注意事项

1. **管理员权限**：修改 hosts 文件需要管理员权限，程序会自动请求
2. **杀毒软件**：部分杀毒软件可能误报，请添加信任
3. **备份**：程序会在修改前自动备份 hosts 文件到 `~/.cf_proxy_manager/backups/`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

<p align="center">
  <img src="resources/icon.ico" alt="Icon" width="32">
  <br>
  Made with ❤️ by 虎哥
</p>
