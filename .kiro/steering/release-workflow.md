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
3. 如需升级，同步更新以下 2 个文件：

```
cf_proxy_manager/__init__.py   → __version__ = "x.x.x"
.kiro/steering/product.md      → 当前版本 vx.x.x（如有）
```

## 2. 更新 Steering 文档（按需）

根据本次改动类型，检查并更新 `.kiro/steering/` 下的文档：

| 变更类型             | 需更新的文件   |
| -------------------- | -------------- |
| 新增/删除/重命名模块 | `structure.md` |
| 新增/删除功能        | `product.md`   |
| 依赖变更             | `tech.md`      |
| 构建命令变更         | `tech.md`      |

### 触发场景

- 在 `cf_proxy_manager/` 目录下新增/删除/重命名模块 → 更新 `structure.md`
- 新增核心功能或功能重大变更 → 更新 `product.md`
- 修改 `requirements.txt` 添加新依赖 → 更新 `tech.md`
- 修改打包配置或命令 → 更新 `tech.md`

## 3. 更新 README（按需）

如果本次修改涉及：

- 新功能
- 重大 Bug 修复
- 依赖变更
- 使用方式变更

则更新 `README.md` 相应章节。

## 4. 运行测试

提交前运行测试，确保代码质量：

```powershell
# 运行所有测试
python -m pytest cf_proxy_manager/tests/ -v

# 或只运行特定模块测试
python -m pytest cf_proxy_manager/tests/test_parsers.py -v
```

确保所有测试通过后再提交。

## 5. 提交 GitHub

```bash
git add .
git commit -m "<type>: <简短描述>

<详细说明（可选）>"
git push origin main
```

### Commit 类型规范

| 类型     | 说明                   |
| -------- | ---------------------- |
| feat     | 新功能                 |
| fix      | Bug 修复               |
| perf     | 性能优化               |
| refactor | 代码重构（不影响功能） |
| docs     | 文档更新               |
| style    | 代码格式调整           |
| test     | 测试相关               |
| chore    | 构建/工具变更          |

### Commit 示例

```
feat: 添加 Hosts 查看器功能

- iOS 风格界面，支持搜索过滤
- 支持隐藏本地回环条目
- 支持单条/批量删除
```

```
fix: 修复 IP 测速超时问题

- 增加连接超时时间
- 优化并发测试逻辑
```

## 6. 打包 EXE

### 清理旧版本

打包前先删除 `dist/` 目录下的旧版本 EXE 文件：

```powershell
# 删除旧版本 EXE
Remove-Item dist\*.exe -ErrorAction SilentlyContinue
```

### 打包命令

```powershell
# 使用打包脚本（推荐）
build.bat

# 或手动打包
python -m PyInstaller cf_proxy_manager.spec --noconfirm --clean
```

### 打包产物

- `dist/虎哥API反代.exe` - 约 11MB

## 7. 发布 Release

使用 GitHub CLI 创建 Release：

```powershell
# 创建 Release 并上传 EXE
gh release create vx.x.x dist/虎哥API反代.exe --repo wangwingzero/tiger-api-proxy --title "vx.x.x - <简短描述>" --notes-file release-notes.md
```

或手动操作：

1. 访问 https://github.com/wangwingzero/tiger-api-proxy → Releases → Draft a new release
2. 填写信息：
   - Tag: `vx.x.x`（如 v1.0.0）
   - Title: `vx.x.x - <简短描述>`
   - Description: 本次更新内容
3. 上传文件：`虎哥API反代.exe`
4. 点击 Publish release

### Release Notes 模板

```markdown
## ✨ 新功能 / 🐛 Bug 修复 / ⚡ 性能优化

- 具体改动内容

## 📦 下载

下载 `虎哥API反代.exe` 即可使用。

## 使用说明

1. 下载 EXE 文件
2. 双击运行，允许 UAC 管理员权限请求
3. 配置目标节点和 CF 反代域名
4. 点击「开始测速」找到最快 IP
5. 点击「应用最佳 IP」写入 hosts
```

## 快速检查清单

- [ ] 版本号已按语义化版本规范处理
- [ ] Steering 文档已更新（如需要）
- [ ] README 已更新（如需要）
- [ ] 测试全部通过
- [ ] 代码已提交并推送
- [ ] 旧版本 EXE 已删除
- [ ] EXE 已打包测试
- [ ] Release 已创建并上传（仅版本升级时）

## 注意事项

- 重构、文档更新、测试等不影响功能的改动，无需升级版本号
- feat/fix/perf 类型的改动需要升级版本并创建 Release
- 新增模块或功能时，记得同步更新 steering 文档
