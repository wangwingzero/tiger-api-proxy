# Requirements Document

## Introduction

CF Proxy Manager 是一个 Windows GUI 工具，用于管理 Cloudflare 反向代理配置和优选 IP。用户可以配置目标反代节点、CF 反代域名，并通过自动测速选择最佳的 Cloudflare IP，最终自动修改系统 hosts 文件以优化访问速度。

## Glossary

- **Target_Node**: 目标反代节点，如 `anyrouter.top`，是实际提供 API 服务的地址
- **CF_Proxy_Domain**: Cloudflare 反代域名，如 `betterclau.de`，用于中转访问 Target_Node
- **Optimized_IP**: 优选 IP，经过测速后延迟最低的 Cloudflare 节点 IP
- **Hosts_File**: Windows 系统的 hosts 文件，位于 `C:\Windows\System32\drivers\etc\hosts`
- **Speed_Tester**: 测速模块，用于测试多个 IP 的延迟并选出最佳 IP

## Requirements

### Requirement 1: 目标反代节点配置

**User Story:** As a user, I want to configure target proxy nodes, so that I can switch between different API endpoints.

#### Acceptance Criteria

1. THE GUI SHALL provide an input field for entering target proxy node URLs
2. THE GUI SHALL set `https://anyrouter.top` as the default target node
3. WHEN a user enters a new target node URL, THE System SHALL validate the URL format
4. THE GUI SHALL allow users to save multiple target nodes for quick switching
5. WHEN a user selects a saved target node, THE System SHALL update the current configuration

### Requirement 2: CF 反代域名配置

**User Story:** As a user, I want to configure CF proxy domains flexibly, so that I can use different proxy services.

#### Acceptance Criteria

1. THE GUI SHALL provide an input field for CF proxy domain configuration
2. WHEN a user enters a full URL like `https://betterclau.de/claude/anyrouter.top`, THE System SHALL parse and extract the domain automatically
3. WHEN a user enters only a domain like `betterclau.de`, THE System SHALL accept it and construct the full proxy URL
4. THE System SHALL display the constructed full proxy URL for user confirmation
5. WHEN the CF proxy domain is configured, THE System SHALL use it as the target for hosts file modification

### Requirement 3: 优选 IP 管理

**User Story:** As a user, I want to manage and test multiple Cloudflare IPs, so that I can find the fastest one for my network.

#### Acceptance Criteria

1. THE GUI SHALL provide a text area for entering multiple IPs (one per line or comma-separated)
2. THE System SHALL provide default IPs:
   - `103.21.244.78` (🇩🇪 法兰克福)
   - `103.21.244.106` (🇩🇪 法兰克福)
   - `104.25.235.32` (🇺🇸 洛杉矶)
   - `188.114.98.205` (🇺🇸 洛杉矶)
   - `104.21.52.82` (🇭🇰 香港)
3. WHEN a user adds new IPs, THE System SHALL parse and validate the IP format
4. THE System SHALL support IP format with or without port and location tags (e.g., `103.21.244.78:443#🇩🇪 法兰克福`)
5. THE GUI SHALL display all configured IPs in a list with their location tags

### Requirement 4: IP 测速功能

**User Story:** As a user, I want to automatically test IP speeds, so that I can select the fastest one without manual testing.

#### Acceptance Criteria

1. WHEN a user clicks the "Test Speed" button, THE Speed_Tester SHALL test all configured IPs
2. THE Speed_Tester SHALL measure TCP connection latency to each IP on port 443
3. THE GUI SHALL display real-time testing progress and results
4. THE GUI SHALL show latency (ms) for each IP after testing
5. THE Speed_Tester SHALL automatically identify and highlight the fastest IP
6. IF an IP fails to connect, THEN THE System SHALL mark it as "Failed" and exclude it from selection
7. WHEN testing completes, THE System SHALL sort IPs by latency (fastest first)

### Requirement 5: Hosts 文件自动修改

**User Story:** As a user, I want the tool to automatically update my hosts file, so that I don't need to manually edit system files.

#### Acceptance Criteria

1. WHEN a user clicks "Apply Best IP", THE System SHALL modify the Hosts_File
2. THE System SHALL add or update the entry mapping CF_Proxy_Domain to the selected Optimized_IP
3. THE System SHALL backup the original hosts file before modification
4. THE System SHALL request administrator privileges if needed
5. WHEN hosts file is modified, THE System SHALL flush DNS cache automatically
6. THE GUI SHALL display the current hosts file entry for the CF proxy domain
7. IF modification fails, THEN THE System SHALL display an error message with the reason
8. WHEN a user clicks "Clear hosts", THE System SHALL remove the CF proxy domain entry from hosts file and restore default DNS resolution

### Requirement 6: 配置持久化

**User Story:** As a user, I want my configurations to be saved, so that I don't need to re-enter them every time.

#### Acceptance Criteria

1. THE System SHALL save all configurations to a local JSON file
2. WHEN the application starts, THE System SHALL load saved configurations
3. THE System SHALL save: target nodes, CF proxy domain, IP list, and last selected IP
4. WHEN configuration changes, THE System SHALL auto-save after a short delay

### Requirement 7: 用户界面布局

**User Story:** As a user, I want a clear and intuitive interface, so that I can easily manage all settings.

#### Acceptance Criteria

1. THE GUI SHALL organize settings into logical sections: Target Node, CF Proxy, IP Management
2. THE GUI SHALL provide clear labels and tooltips for all input fields
3. THE GUI SHALL display status messages for all operations
4. THE GUI SHALL use a modern, clean visual style
5. THE GUI SHALL be responsive and not freeze during speed testing
