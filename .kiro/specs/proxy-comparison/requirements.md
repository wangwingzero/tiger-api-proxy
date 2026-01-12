# Requirements Document

## Introduction

本功能为 CF Proxy Manager 添加反代效果对比功能，让用户能够直观地比较不同反代方案的延迟效果，从而做出最佳选择。用户可以对比：
1. 直连原始反代域名（不优选 IP）
2. 通过优选 IP 连接反代域名
3. 其他公共反代服务（如宁波节点、BetterClaude 等）

## Glossary

- **Comparison_Service**: 用于对比的反代服务，包含名称、URL 和描述
- **Comparison_Result**: 对比测试结果，包含延迟、成功状态和相对基准的提升百分比
- **Baseline**: 基准测试，即用户自己的反代域名直连延迟
- **Optimized_Connection**: 通过优选 IP 连接用户反代域名的方式
- **Default_Services**: 默认的对比服务列表

## Requirements

### Requirement 1: 对比服务管理

**User Story:** As a user, I want to manage comparison services, so that I can customize which services to compare against.

#### Acceptance Criteria

1. THE System SHALL provide a default list of comparison services:
   - 上海节点: `https://a-ocnfniawgw.cn-shanghai.fcapp.run`
   - 宁波节点: `https://pmpjfbhq.cn-nb1.rainapp.top`
   - AnyRouter: `https://anyrouter.top`
   - BetterClaude: `https://betterclau.de/claude/anyrouter.top`
2. WHEN a user adds a custom comparison service, THE System SHALL validate the URL format and add it to the list
3. WHEN a user removes a comparison service, THE System SHALL remove it from the list
4. WHEN a user clicks "恢复默认", THE System SHALL reset the comparison services to the default list
5. THE System SHALL persist the comparison services list to configuration

### Requirement 2: 延迟对比测试

**User Story:** As a user, I want to test and compare latency across different proxy options, so that I can choose the fastest one.

#### Acceptance Criteria

1. WHEN a user initiates a comparison test, THE System SHALL test the following in parallel:
   - 用户反代域名直连（基准）
   - 用户反代域名 + 优选 IP（如果已配置）
   - 所有对比服务
2. WHEN testing each service, THE System SHALL perform HTTPS connection test with SSL handshake
3. WHEN a test completes, THE System SHALL display latency in milliseconds
4. WHEN a test fails, THE System SHALL display "连接失败" with error reason
5. THE System SHALL calculate and display the improvement percentage relative to baseline

### Requirement 3: 对比结果展示

**User Story:** As a user, I want to see comparison results in a clear and intuitive way, so that I can easily identify the best option.

#### Acceptance Criteria

1. THE System SHALL display results in a card-based layout with visual indicators
2. WHEN displaying results, THE System SHALL show:
   - 服务名称
   - 延迟值（毫秒）
   - 相对基准的提升/下降百分比
   - 延迟等级颜色（绿色 <200ms, 黄色 200-500ms, 红色 >500ms）
3. THE System SHALL sort results by latency (fastest first)
4. THE System SHALL highlight the fastest option with a "最佳" badge
5. WHEN baseline test fails, THE System SHALL still display other results without percentage comparison

### Requirement 4: 选择并应用

**User Story:** As a user, I want to select and apply a comparison result, so that I can use the best proxy option.

#### Acceptance Criteria

1. WHEN a user selects a comparison result, THE System SHALL highlight the selected card
2. WHEN a user clicks "应用选中", THE System SHALL:
   - IF selected is "优选 IP 反代": apply the best IP to hosts file
   - IF selected is a public service: copy the URL to clipboard and show usage instructions
3. WHEN applying optimized IP, THE System SHALL update hosts file and flush DNS
4. IF hosts file modification fails, THEN THE System SHALL display an error message with admin privilege hint

### Requirement 5: UI/UX 设计

**User Story:** As a user, I want an intuitive and visually appealing interface, so that I can easily understand and use the comparison feature.

#### Acceptance Criteria

1. THE System SHALL add a new "📊 效果对比" section in the main window
2. THE System SHALL provide a "开始对比" button to initiate comparison tests
3. WHILE testing is in progress, THE System SHALL show a progress indicator and disable the test button
4. THE System SHALL use consistent styling with the existing application theme
5. THE System SHALL support dark/light theme modes for the comparison section
