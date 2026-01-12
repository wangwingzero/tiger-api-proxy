# Implementation Plan: Proxy Comparison Feature

## Overview

为 CF Proxy Manager 添加反代效果对比功能，让用户能够直观地比较不同反代方案的延迟效果。

## Tasks

- [x] 1. 创建数据模型
  - [x] 1.1 在 models.py 中添加 ComparisonService 数据类
    - 包含 name, url, description, is_default 字段
    - 实现 to_dict/from_dict 方法
    - _Requirements: 1.1, 1.5_
  - [x] 1.2 在 models.py 中添加 ComparisonResult 数据类
    - 包含 service, latency_ms, success, error_message, improvement_pct 字段
    - 实现 latency_level 属性（fast/medium/slow/failed）
    - _Requirements: 3.2_
  - [x] 1.3 添加 DEFAULT_COMPARISON_SERVICES 常量
    - 包含 4 个默认对比服务
    - _Requirements: 1.1_
  - [x] 1.4 扩展 Config 类添加 comparison_services 字段
    - 更新 to_dict/from_dict 方法
    - _Requirements: 1.5_
  - [x] 1.5 编写属性测试：配置序列化往返
    - **Property 4: Configuration Round-Trip**
    - **Validates: Requirements 1.5**

- [x] 2. 实现对比测试器
  - [x] 2.1 创建 comparison_tester.py 模块
    - 实现 ComparisonTester 类
    - _Requirements: 2.1, 2.2_
  - [x] 2.2 实现 test_https_latency 方法
    - HTTPS 连接测试（含 SSL 握手）
    - 返回延迟和错误信息
    - _Requirements: 2.2, 2.3, 2.4_
  - [x] 2.3 实现 test_via_ip 方法
    - 通过指定 IP 连接域名
    - SNI 使用域名
    - _Requirements: 2.1_
  - [x] 2.4 实现 run_comparison 方法
    - 并行测试所有服务
    - 支持进度回调
    - _Requirements: 2.1_
  - [x] 2.5 实现 calculate_improvement 静态方法
    - 计算相对基准的提升百分比
    - _Requirements: 2.5_
  - [x] 2.6 实现 sort_results 静态方法
    - 按延迟排序（成功在前，按延迟升序）
    - _Requirements: 3.3_
  - [x] 2.7 编写属性测试：提升百分比计算
    - **Property 5: Improvement Percentage Calculation**
    - **Validates: Requirements 2.5**
  - [x] 2.8 编写属性测试：结果排序顺序
    - **Property 6: Results Sorting Order**
    - **Validates: Requirements 3.3**
  - [x] 2.9 编写属性测试：最佳结果选择
    - **Property 7: Best Result Selection**
    - **Validates: Requirements 3.4**

- [x] 3. Checkpoint - 确保核心逻辑测试通过
  - 运行 pytest 确保所有测试通过
  - 如有问题请询问用户

- [x] 4. 实现服务管理功能
  - [x] 4.1 在 parsers.py 中添加 URL 验证方法
    - 验证 HTTPS URL 格式
    - _Requirements: 1.2_
  - [x] 4.2 实现服务列表管理方法
    - 添加、删除、重置默认
    - _Requirements: 1.2, 1.3, 1.4_
  - [x] 4.3 编写属性测试：URL 验证
    - **Property 1: URL Validation Correctness**
    - **Validates: Requirements 1.2**
  - [x] 4.4 编写属性测试：服务列表移除
    - **Property 2: Service List Removal Invariant**
    - **Validates: Requirements 1.3**
  - [x] 4.5 编写属性测试：重置默认幂等性
    - **Property 3: Reset to Defaults Idempotence**
    - **Validates: Requirements 1.4**

- [x] 5. 创建 UI 组件
  - [x] 5.1 创建 components/comparison_card.py
    - 实现 ComparisonCard 组件
    - 显示服务名、延迟、提升百分比
    - 延迟颜色指示
    - _Requirements: 3.1, 3.2, 3.4_
  - [x] 5.2 创建 components/comparison_section.py
    - 实现 ComparisonSection 组件
    - 包含对比按钮、服务管理、结果展示区
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 6. 集成到主界面
  - [x] 6.1 在 gui_ctk.py 中集成 ComparisonSection
    - 添加到主界面布局
    - 连接配置和回调
    - _Requirements: 5.1, 5.4, 5.5_
  - [x] 6.2 实现应用选中结果功能
    - 优选 IP：更新 hosts
    - 公共服务：复制 URL
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 6.3 更新 config_manager.py 支持新配置字段
    - 加载/保存 comparison_services
    - _Requirements: 1.5_

- [x] 7. Final Checkpoint - 完整功能测试
  - 运行 pytest 确保所有测试通过
  - 手动测试 UI 功能
  - 如有问题请询问用户

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
