# Implementation Plan: Hosts Viewer

## Overview

为 CF Proxy Manager 添加 iOS 风格的 Hosts 查看器功能，包括 hosts 条目展示、搜索过滤、删除管理，以及管理员权限处理优化。

## Tasks

- [x] 1. 创建 iOS 风格 UI 组件
  - [x] 1.1 创建 `ios_widgets.py` 实现 iOS 风格组件
    - 定义颜色常量 (BACKGROUND, CARD_BG, ACCENT, DESTRUCTIVE 等)
    - 实现 `RoundedFrame` 圆角边框组件
    - 实现 `IOSButton` iOS 风格按钮
    - 实现 `IOSSearchEntry` iOS 风格搜索框
    - _Requirements: 2.1, 2.2, 2.5, 2.6_

- [x] 2. 实现 Hosts 条目数据模型和解析
  - [x] 2.1 在 `models.py` 中添加 `HostsEntry` 数据类
    - 实现 `matches(query)` 搜索匹配方法
    - _Requirements: 1.1, 4.2_
  - [x] 2.2 在 `hosts_manager.py` 中添加 `get_all_entries()` 方法
    - 解析所有有效 hosts 条目
    - 过滤注释和空行
    - _Requirements: 1.1, 1.2_
  - [x] 2.3 编写 hosts 解析的属性测试
    - **Property 1: Hosts File Parsing Completeness**
    - **Validates: Requirements 1.1, 1.2**

- [x] 3. 实现 Hosts Viewer 主窗口
  - [x] 3.1 创建 `hosts_viewer.py` 实现 `HostsViewer` 类
    - 创建 iOS 风格窗口框架
    - 实现搜索栏区域
    - 实现条目卡片列表区域 (使用 Canvas + Scrollbar)
    - 实现底部操作栏
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_
  - [x] 3.2 实现 `EntryCard` 条目卡片组件
    - 显示域名 (主标题) 和 IP (副标题)
    - 实现悬停效果和选中状态
    - 添加删除按钮
    - _Requirements: 2.3, 2.4, 3.1, 3.2_

- [x] 4. 实现搜索和过滤功能
  - [x] 4.1 实现实时搜索过滤
    - 绑定搜索框输入事件
    - 实现 `_filter_entries()` 过滤方法
    - 显示过滤后的结果
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 4.2 编写搜索过滤的属性测试
    - **Property 3: Search Filter Accuracy**
    - **Validates: Requirements 4.2**

- [x] 5. 实现条目管理功能
  - [x] 5.1 实现单个条目删除
    - 点击删除按钮弹出确认对话框
    - 调用 `hosts_manager.remove_entry()` 删除
    - 刷新列表显示
    - _Requirements: 3.2, 3.3, 3.4_
  - [x] 5.2 实现批量删除功能
    - 添加 "删除全部" 按钮
    - 弹出确认对话框
    - 循环删除所有条目
    - _Requirements: 3.5_
  - [x] 5.3 编写删除功能的属性测试
    - **Property 2: Entry Deletion Correctness**
    - **Validates: Requirements 3.3**

- [x] 6. 实现管理员权限处理
  - [x] 6.1 创建 `admin_helper.py` 实现权限辅助类
    - 实现 `is_admin()` 检测方法
    - 实现 `restart_as_admin()` 重启方法
    - 实现 `request_admin_if_needed()` 按需请求方法
    - _Requirements: 6.1, 6.3, 6.4_
  - [x] 6.2 在主界面添加权限状态显示
    - 在状态栏显示当前权限状态
    - 使用不同颜色区分 (绿色/黄色)
    - _Requirements: 6.2_

- [x] 7. 集成到主界面
  - [x] 7.1 在主界面添加 "查看 hosts" 按钮
    - 在状态区域添加按钮
    - 点击打开 Hosts Viewer 窗口
    - _Requirements: 5.1, 5.2_
  - [x] 7.2 实现窗口关闭回调
    - Hosts Viewer 关闭时刷新主界面状态
    - _Requirements: 5.3_

- [x] 8. Checkpoint - 功能测试
  - 确保所有功能正常工作，如有问题请询问用户

- [x] 9. 创建打包配置
  - [x] 9.1 创建 PyInstaller 打包脚本
    - 创建 `build.py` 或 `build.bat` 打包脚本
    - 配置 UAC 管理员权限请求
    - 配置图标和元数据
    - _Requirements: 6.5_

- [x] 10. Final Checkpoint
  - 确保所有测试通过，功能完整

## Notes

- All tasks including property-based tests are required
- iOS 风格组件使用 Tkinter Canvas 绘制圆角效果
- 属性测试使用 `hypothesis` 库
- 打包使用 PyInstaller，需要安装: `pip install pyinstaller`

