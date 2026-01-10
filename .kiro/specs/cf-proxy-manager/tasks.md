# Implementation Plan: CF Proxy Manager

## Overview

使用 Python + Tkinter 实现 CF Proxy Manager GUI 工具，采用模块化设计，先实现核心服务层，再构建 GUI 层。

## Tasks

- [x] 1. 项目初始化和数据模型
  - [x] 1.1 创建项目结构和数据模型文件 `models.py`
    - 定义 `IPEntry`, `TestResult`, `ProxyConfig`, `Config` 数据类
    - 定义默认配置常量 `DEFAULT_TARGET_NODE`, `DEFAULT_IPS`
    - _Requirements: 3.2_

- [x] 2. 实现配置管理模块
  - [x] 2.1 创建 `config_manager.py` 实现 ConfigManager 类
    - 实现 `load()`, `save()`, `get_default_config()` 方法
    - 支持 JSON 序列化/反序列化
    - _Requirements: 6.1, 6.2, 6.3_
  - [x] 2.2 编写配置管理的属性测试
    - **Property 7: Configuration Round Trip**
    - **Validates: Requirements 6.1, 6.3**

- [x] 3. 实现 URL 和 IP 解析模块
  - [x] 3.1 创建 `parsers.py` 实现 URLParser 和 IPParser 类
    - URLParser: `parse_proxy_url()`, `build_proxy_url()`, `extract_domain()`
    - IPParser: `parse()`, `parse_multiple()`, `format()`
    - _Requirements: 1.3, 2.2, 2.3, 3.3, 3.4_
  - [x] 3.2 编写解析模块的属性测试
    - **Property 1: URL/Domain Parsing Round Trip**
    - **Property 2: IP Entry Parsing Consistency**
    - **Validates: Requirements 1.3, 2.2, 2.3, 3.3, 3.4**

- [x] 4. 实现测速模块
  - [x] 4.1 创建 `speed_tester.py` 实现 SpeedTester 类
    - 实现 `test_ip()`, `test_all()`, `get_best_ip()` 方法
    - 使用 socket 测试 TCP 连接延迟
    - 支持异步测试和进度回调
    - _Requirements: 4.1, 4.2, 4.5, 4.6, 4.7_
  - [x] 4.2 编写测速模块的属性测试
    - **Property 3: Best IP Selection Correctness**
    - **Property 4: Failed IP Exclusion**
    - **Property 5: Test Results Sorting**
    - **Validates: Requirements 4.5, 4.6, 4.7**

- [x] 5. 实现 Hosts 管理模块
  - [x] 5.1 创建 `hosts_manager.py` 实现 HostsManager 类
    - 实现 `read_hosts()`, `get_entry()`, `update_entry()`, `remove_entry()` 方法
    - 实现 `backup()`, `flush_dns()` 方法
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.8_
  - [x] 5.2 编写 Hosts 管理的属性测试
    - **Property 6: Hosts Entry Format Correctness**
    - **Validates: Requirements 5.2**

- [x] 6. Checkpoint - 核心模块测试
  - 确保所有核心模块测试通过，如有问题请询问用户

- [x] 7. 实现 GUI 主界面
  - [x] 7.1 创建 `gui.py` 实现主窗口框架
    - 创建主窗口和三个主要区域的 LabelFrame
    - 实现基本布局结构
    - _Requirements: 7.1, 7.2_
  - [x] 7.2 实现目标反代节点区域
    - 下拉选择框 + 添加按钮
    - 节点列表管理
    - _Requirements: 1.1, 1.2, 1.4, 1.5_
  - [x] 7.3 实现 CF 反代配置区域
    - 输入框 + 自动解析显示
    - 完整代理地址预览
    - _Requirements: 2.1, 2.4_
  - [x] 7.4 实现优选 IP 管理区域
    - IP 列表 Treeview (IP, 延迟, 状态)
    - 添加 IP 输入框
    - 测速、应用、删除、清除 hosts 按钮
    - _Requirements: 3.1, 3.5, 4.3, 4.4_
  - [x] 7.5 实现状态显示区域
    - 当前 hosts 配置显示
    - 操作状态消息
    - _Requirements: 5.6, 5.7_

- [x] 8. 集成和功能连接
  - [x] 8.1 连接 GUI 与核心模块
    - 绑定按钮事件到对应功能
    - 实现配置自动保存
    - 实现测速进度更新
    - _Requirements: 4.3, 6.4_
  - [x] 8.2 实现管理员权限请求
    - 检测是否需要管理员权限
    - 提示用户以管理员身份运行
    - _Requirements: 5.4_

- [x] 9. 创建程序入口
  - [x] 9.1 创建 `main.py` 作为程序入口
    - 初始化所有模块
    - 启动 GUI 主循环
    - 处理异常和退出

- [x] 10. Final Checkpoint
  - 确保所有功能正常工作，如有问题请询问用户

## Notes

- Tasks marked with `*` are optional property-based tests
- 使用 Python 3.8+ 和 Tkinter (无需额外安装)
- 属性测试使用 `hypothesis` 库
- 测速使用多线程避免 GUI 卡顿
