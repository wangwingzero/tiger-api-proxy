---
inclusion: manual
---
# 发布工作流

代码修改完成后，按以下步骤执行发布流程。

## 1. 更新版本号（自动判断）

根据 [语义化版本](https://semver.org/lang/zh-CN/) 规范自动判断版本号：

| 改动类型            | 版本变化 | 示例           |
| ------------------- | -------- | -------------- |
| 重大变更/不兼容 API | MAJOR +1 | 1.0.0 → 2.0.0 |
| 新功能（feat）      | MINOR +1 | 1.0.0 → 1.1.0 |
| Bug 修复（fix）     | PATCH +1 | 1.0.0 → 1.0.1 |
| 性能优化（perf）    | PATCH +1 | 1.0.0 → 1.0.1 |
| 重构/文档/测试      | 不升级   | 1.0.0 → 1.0.0 |

**判断规则：**

1. 查看 `git diff` 或 `git status` 确定改动内容
2. 根据改动类型决定是否升级版本
3. **版本号只需修改一个文件**，其他地方自动同步：

```
cf_proxy_manager/__init__.py   → __version__ = "x.x.x"
```

**版本号自动同步机制：**
- `cf_proxy_manager.spec` 会自动读取 `__init__.py` 中的版本号
- EXE 文件名自动变为 `虎哥API反代-vx.x.x.exe`
- 程序标题自动显示 `🐯 虎哥API反代 vx.x.x`

## 2. 更新 Steering 文档（按需）

根据本次改动类型，检查并更新 `.kiro/steering/` 下的文档：

| 变更类型             | 需更新的文件   |
| -------------------- | -------------- |
| 新增/删除/重命名模块 | `structure.md` |
| 新增/删除功能        | `product.md`   |
| 依赖变更             | `tech.md`      |
| 构建命令变更         | `tech.md`      |

## 3. 更新 README（按需）

如果本次修改涉及新功能、重大 Bug 修复、依赖变更、使用方式变更，则更新 `README.md`。

### README 更新检查清单

| 变更类型 | 需更新的 README 章节 |
| -------- | -------------------- |
| 新增功能 | `✨ 功能特点`、`📖 使用说明` |
| 界面变更 | `📸 界面预览` |
| 新增/删除模块 | `📁 项目结构` |
| 依赖变更 | `🚀 快速开始` |
| 打包方式变更 | `🔧 打包说明` |
| 重要注意事项 | `⚠️ 注意事项` |

### README 章节说明

- **功能特点**：简洁列出核心功能，使用 emoji 图标
- **界面预览**：描述主界面包含的功能区域
- **下载**：指向 GitHub Releases 页面
- **快速开始**：EXE 运行和源码运行两种方式
- **使用说明**：分步骤说明操作流程
- **打包说明**：PyInstaller 打包命令
- **项目结构**：主要文件和目录说明
- **注意事项**：权限、杀毒、备份等提醒

### 更新原则

1. 保持简洁，避免冗长描述
2. 新功能需同时更新「功能特点」和「使用说明」
3. 确保项目结构与实际文件一致
4. 使用一致的 emoji 风格

## 4. 运行测试

```powershell
python -m pytest cf_proxy_manager/tests/ -v
```

确保所有测试通过后再提交。

## 5. 提交 GitHub

```bash
git add .
git commit -m "<type>: <简短描述>"
git push origin main
```

### Commit 类型

| 类型     | 说明                   |
| -------- | ---------------------- |
| feat     | 新功能                 |
| fix      | Bug 修复               |
| perf     | 性能优化               |
| refactor | 代码重构               |
| docs     | 文档更新               |
| style    | 代码格式               |
| test     | 测试相关               |
| chore    | 构建/工具变更          |

## 6. 打包 EXE

```powershell
# 清理旧版本
Remove-Item dist\*.exe -ErrorAction SilentlyContinue

# 打包（EXE 文件名自动带版本号）
python -m PyInstaller cf_proxy_manager.spec --noconfirm --clean
```

打包产物：`dist/虎哥API反代-vx.x.x.exe`

## 7. 发布 Release

```powershell
# 获取版本号
$version = (Get-Content cf_proxy_manager/__init__.py | Select-String '__version__').ToString() -replace '.*"(.+)".*', '$1'

# 创建 Release
gh release create "v$version" "dist/虎哥API反代-v$version.exe" --repo wangwingzero/tiger-api-proxy --title "v$version - <简短描述>" --notes-file release-notes.md
```

或手动操作：
1. 访问 https://github.com/wangwingzero/tiger-api-proxy/releases
2. 点击 Draft a new release
3. Tag: `vx.x.x`，Title: `vx.x.x - <描述>`
4. 上传 `虎哥API反代-vx.x.x.exe`
5. 点击 Publish release

### Release Notes 模板

```markdown
## ✨ 新功能 / 🐛 Bug 修复 / ⚡ 性能优化

- 具体改动内容

## 📦 下载

下载 `虎哥API反代-vx.x.x.exe` 即可使用。
```

## 快速检查清单

- [ ] 版本号已更新（`cf_proxy_manager/__init__.py`）
- [ ] 测试全部通过
- [ ] 代码已提交并推送
- [ ] EXE 已打包测试
- [ ] Release 已创建并上传

## 注意事项

- 重构、文档、测试等不影响功能的改动，无需升级版本号
- feat/fix/perf 类型的改动需要升级版本并创建 Release
- **版本号只需改一处**：`cf_proxy_manager/__init__.py`
