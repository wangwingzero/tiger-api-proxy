# 发布工作流

执行完整的发布流程，包括版本更新、测试、提交、打包和发布。

> **强制规则**：执行此发布流程时，**必须升级版本号**（至少 PATCH +1），确保每次发布都有唯一的版本标识。

## 执行步骤

### 1. 分析改动内容

首先检查 git 状态和改动：

```bash
git status
git diff --stat
git diff
```

### 2. 确定版本号

根据语义化版本规范判断版本升级类型：

| 改动类型            | 版本变化 | 示例           |
| ------------------- | -------- | -------------- |
| 重大变更/不兼容 API | MAJOR +1 | 1.0.0 → 2.0.0 |
| 新功能（feat）      | MINOR +1 | 1.0.0 → 1.1.0 |
| Bug 修复（fix）     | PATCH +1 | 1.0.0 → 1.0.1 |
| 性能优化（perf）    | PATCH +1 | 1.0.0 → 1.0.1 |

**版本号只需修改一个文件**：
```
cf_proxy_manager/__init__.py   → __version__ = "x.x.x"
```

### 3. 更新 Steering 文档（按需）

检查 `.kiro/steering/` 下的文档是否需要更新：

| 变更类型             | 需更新的文件     |
| -------------------- | ---------------- |
| 新增/删除/重命名模块 | `structure.md` |
| 新增/删除功能        | `product.md`   |
| 依赖变更             | `tech.md`      |
| 构建命令变更         | `tech.md`      |

### 4. 更新 README（按需）

如果涉及新功能、重大 Bug 修复、依赖变更、使用方式变更，则更新 `README.md`：

| 变更类型      | 需更新的 README 章节             |
| ------------- | -------------------------------- |
| 新增功能      | `功能特点`、`使用说明` |
| 界面变更      | `界面预览`                  |
| 新增/删除模块 | `项目结构`                  |
| 依赖变更      | `快速开始`                  |

### 5. 运行测试

```powershell
python -m pytest cf_proxy_manager/tests/ -v
```

确保所有测试通过后再继续。

### 6. 提交到 GitHub

```bash
git add .
git commit -m "<type>: <简短描述>"
git push origin main
```

**Commit 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `perf`: 性能优化
- `refactor`: 代码重构
- `docs`: 文档更新
- `test`: 测试相关
- `chore`: 构建/工具变更

### 7. 打包 EXE

```powershell
# 清理旧版本
Remove-Item dist\*.exe -ErrorAction SilentlyContinue

# 打包（EXE 文件名自动带版本号）
python -m PyInstaller cf_proxy_manager.spec --noconfirm --clean
```

打包产物：`dist/虎哥API反代-vx.x.x.exe`

### 8. 发布 Release

```powershell
# 获取版本号
$version = (Get-Content cf_proxy_manager/__init__.py | Select-String '__version__').ToString() -replace '.*"(.+)".*', '$1'

# 创建 Release
gh release create "v$version" "dist/虎哥API反代-v$version.exe" --repo wangwingzero/tiger-api-proxy --title "v$version - <简短描述>" --notes-file release-notes.md
```

## 快速检查清单

执行完成后确认：
- [ ] 版本号已更新（`cf_proxy_manager/__init__.py`）
- [ ] Steering 文档已更新（如需要）
- [ ] README 已更新（如需要）
- [ ] 测试全部通过
- [ ] 代码已提交并推送
- [ ] EXE 已打包
- [ ] Release 已创建并上传

## 注意事项

- **版本号只需改一处**：`cf_proxy_manager/__init__.py`
- EXE 文件名和程序标题会自动同步版本号
- 如果测试失败，必须先修复再继续
