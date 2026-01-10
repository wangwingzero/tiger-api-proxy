# Implementation Plan: CustomTkinter UI Migration

## Overview

将 CF Proxy Manager 从 Tkinter 迁移到 CustomTkinter，创建现代化卡片式 UI，支持深色/浅色主题。

## Tasks

- [x] 1. 项目配置和依赖更新
  - [x] 1.1 更新 requirements.txt 添加 customtkinter>=5.2.0
    - 添加 customtkinter 依赖
    - _Requirements: 1.1_

  - [x] 1.2 创建 components 目录结构
    - 创建 `cf_proxy_manager/components/__init__.py`
    - _Requirements: 1.1_

- [x] 2. 创建主题配置模块
  - [x] 2.1 创建 `components/theme.py`
    - 定义 AppTheme 类
    - 定义颜色常量 (success, warning, danger, muted, primary, best_border)
    - 定义延迟阈值 (LATENCY_FAST=100, LATENCY_MEDIUM=300)
    - 定义字体配置 (FONT_MONO, FONT_DEFAULT, FONT_SMALL)
    - 实现 `get_latency_color(latency_ms)` 静态方法
    - 实现 `get_status_text(result)` 静态方法
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 2.2 编写主题模块属性测试
    - **Property 1: Latency color mapping is consistent**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 3. 创建 IP 卡片组件
  - [x] 3.1 创建 `components/ip_card.py`
    - 实现 IPCard 类继承 ctk.CTkFrame
    - 实现卡片布局：IP标签(左)、延迟徽章(右)、状态文本(右)
    - 实现最佳徽章显示 (is_best=True 时)
    - 实现点击选中切换功能
    - 使用 Consolas 等宽字体显示 IP
    - 设置最小高度 50px
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2_

  - [x] 3.2 编写 IP 卡片属性测试
    - **Property 3: IP card contains all required information**
    - **Validates: Requirements 2.2**

  - [x] 3.3 编写卡片选择切换测试
    - **Property 6: Card selection toggle is idempotent after two clicks**
    - **Validates: Requirements 2.4**

- [x] 4. Checkpoint - 验证组件模块
  - 运行测试确保 theme.py 和 ip_card.py 正常工作
  - 确保所有属性测试通过

- [x] 5. 创建主 GUI 类
  - [x] 5.1 创建 `gui_ctk.py` 基础框架
    - 创建 CFProxyManagerCTk 类继承 ctk.CTk
    - 设置窗口标题、大小、最小尺寸
    - 配置 CustomTkinter 主题 (appearance_mode, color_theme)
    - 初始化现有组件 (config_manager, speed_tester, hosts_manager)
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 5.2 实现目标节点区域
    - 使用 CTkFrame 和 CTkLabel 创建区域
    - 使用 CTkComboBox 替代 ttk.Combobox
    - 使用 CTkButton 替代 ttk.Button
    - 复用原有事件处理逻辑
    - _Requirements: 6.1, 6.2_

  - [x] 5.3 实现 CF 反代配置区域
    - 使用 CTkEntry 替代 ttk.Entry
    - 保持原有功能逻辑
    - _Requirements: 6.2_

  - [x] 5.4 实现 IP 管理区域（卡片列表）
    - 使用 CTkScrollableFrame 作为容器
    - 动态创建 IPCard 组件
    - 实现 _refresh_ip_list() 方法创建/更新卡片
    - 实现最佳 IP 识别和高亮
    - _Requirements: 2.1, 4.1, 4.2_

  - [x] 5.5 编写 IP 列表映射属性测试
    - **Property 2: IP list to card mapping preserves count**
    - **Validates: Requirements 2.1**

  - [x] 5.6 编写最佳 IP 识别属性测试
    - **Property 4: Best IP identification is correct**
    - **Validates: Requirements 4.1**

- [ ] 6. 实现操作按钮和状态区域
  - [x] 6.1 实现添加 IP 输入区域
    - CTkEntry + CTkButton 组合
    - 复用原有 _on_add_ip() 逻辑
    - _Requirements: 6.2, 6.5_

  - [x] 6.2 实现操作按钮组
    - 创建 "🚀 开始测速" 按钮 (主要操作，使用强调色)
    - 创建 "✅ 应用最佳 IP" 按钮
    - 创建 "🗑️ 删除选中" 按钮
    - 创建 "🧹 清除hosts" 按钮
    - 复用原有事件处理逻辑
    - _Requirements: 6.1, 6.3, 6.5_

  - [x] 6.3 实现状态显示区域
    - 权限状态、hosts 配置状态、操作状态
    - 使用 CTkLabel 显示
    - _Requirements: 1.2_

- [x] 7. 实现主题切换功能
  - [x] 7.1 添加主题切换控件
    - 在状态区域添加主题切换按钮或下拉框
    - 支持 "深色"、"浅色"、"跟随系统" 三个选项
    - _Requirements: 5.1, 5.2_

  - [x] 7.2 实现主题持久化
    - 在 Config 模型中添加 theme_mode 字段
    - 保存和加载主题设置
    - _Requirements: 5.3_

  - [x] 7.3 编写主题持久化属性测试
    - **Property 5: Theme preference persistence round-trip**
    - **Validates: Requirements 5.3**

- [x] 8. 更新入口文件
  - [x] 8.1 修改 main.py 使用新 GUI
    - 导入 CFProxyManagerCTk 替代 CFProxyManagerGUI
    - 保持管理员权限检查逻辑
    - _Requirements: 1.2_

- [x] 9. Checkpoint - 完整功能验证
  - 运行应用确认所有功能正常
  - 确保所有测试通过
  - 验证 IP 列表显示清晰、不再挤压
  - 验证主题切换正常工作

## Notes

- 所有测试任务均为必需
- 原 `gui.py` 保留作为备份，不删除
- 复用所有现有业务逻辑模块
- 需要安装 customtkinter: `pip install customtkinter>=5.2.0`
