# Implementation Plan: V2Ray 订阅导入功能

## Overview

实现 V2Ray 订阅链接解析和批量 IP 导入功能，包括 vless/trojan/vmess 协议解析、DNS 域名解析和导入对话框 UI。

## Tasks

- [x] 1. 创建 V2Ray 解析器模块
  - [x] 1.1 创建 ParsedNode 数据类和 V2RayParser 类框架
    - 新建 `cf_proxy_manager/v2ray_parser.py`
    - 实现 ParsedNode dataclass
    - 实现 is_ip_address() 静态方法
    - _Requirements: 1.4, 1.5_
  - [x] 1.2 实现 vless:// 链接解析
    - 使用 urllib.parse.urlparse() 解析 URL
    - 提取 address、port、name
    - _Requirements: 1.1_
  - [x] 1.3 实现 trojan:// 链接解析
    - 使用 urllib.parse.urlparse() 解析 URL
    - 提取 address、port、name
    - _Requirements: 1.2_
  - [x] 1.4 实现 vmess:// 链接解析
    - Base64 解码
    - JSON 解析提取 add、port、ps 字段
    - _Requirements: 1.3_
  - [x] 1.5 实现 parse() 主方法
    - 按行分割内容
    - 根据协议前缀调用对应解析方法
    - _Requirements: 1.1, 1.2, 1.3_
  - [ ]* 1.6 编写 V2Ray 解析器属性测试
    - **Property 3: IP 地址识别准确性**
    - **Validates: Requirements 1.4, 1.5**

- [x] 2. 创建 DNS 解析器模块
  - [x] 2.1 实现 DNSResolver 类
    - 新建 `cf_proxy_manager/dns_resolver.py`
    - 实现 resolve() 单域名解析方法
    - 实现 resolve_batch() 批量解析方法
    - 添加超时和错误处理
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. 检查点 - 核心模块完成
  - 确保 V2Ray 解析器和 DNS 解析器模块可以独立工作
  - 如有问题请询问用户

- [x] 4. 创建导入对话框 UI
  - [x] 4.1 创建 ImportDialog 类框架
    - 新建 `cf_proxy_manager/components/import_dialog.py`
    - 继承 ctk.CTkToplevel
    - 设置窗口标题和大小
    - _Requirements: 4.1, 4.2_
  - [x] 4.2 实现界面布局
    - 多行文本输入框 (CTkTextbox)
    - 选项复选框（自动解析域名、跳过重复）
    - 预览区域 (CTkLabel)
    - 按钮区域（取消、解析并导入）
    - _Requirements: 4.2_
  - [x] 4.3 实现实时预览功能
    - 绑定文本变化事件
    - 调用 V2RayParser.parse() 解析内容
    - 更新预览标签显示 IP/域名数量
    - _Requirements: 4.3, 4.4_
  - [x] 4.4 实现导入逻辑
    - 解析内容获取节点列表
    - 可选：解析域名为 IP
    - 调用回调函数传递 IP 列表
    - _Requirements: 3.1, 3.2, 3.3_
  - [ ]* 4.5 编写预览统计属性测试
    - **Property 6: 预览统计准确性**
    - **Validates: Requirements 4.4**

- [x] 5. 集成到主界面
  - [x] 5.1 在主界面添加导入按钮
    - 修改 `cf_proxy_manager/gui_ctk.py`
    - 在 IP 列表区域添加"导入订阅"按钮
    - _Requirements: 4.1_
  - [x] 5.2 实现导入回调处理
    - 实现 _on_import_ips() 方法
    - 去重添加 IP 到配置
    - 保存配置并刷新列表
    - 显示导入统计
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 5.3 更新 components/__init__.py
    - 导出 ImportDialog 类
    - _Requirements: 4.1_
  - [ ]* 5.4 编写导入去重属性测试
    - **Property 4: 导入去重正确性**
    - **Property 5: 导入统计准确性**
    - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 6. 最终检查点 - 功能完成
  - 确保所有功能正常工作
  - 手动测试导入流程
  - 如有问题请询问用户

## Notes

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 开发
- 每个任务引用具体需求以便追溯
- 检查点确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证特定示例和边界情况
