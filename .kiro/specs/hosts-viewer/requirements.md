# Requirements Document

## Introduction

Hosts Viewer 是 CF Proxy Manager 的一个新功能模块，提供一个精美的 iOS 风格界面，用于查看和管理当前 Windows hosts 文件中已配置的所有 CF 反代域名条目。用户可以通过这个界面快速了解已有的配置，并进行删除等管理操作。

## Glossary

- **Hosts_Entry**: hosts 文件中的一条记录，格式为 `IP 域名`
- **Hosts_Viewer**: 用于展示 hosts 文件中所有条目的查看器组件
- **iOS_Style_UI**: 采用 iOS 设计语言的用户界面，特点包括圆角卡片、柔和阴影、简洁配色
- **Entry_Card**: 展示单个 hosts 条目的卡片组件

## Requirements

### Requirement 1: Hosts 条目读取

**User Story:** As a user, I want to see all configured hosts entries, so that I can know which CF proxy domains are already set up.

#### Acceptance Criteria

1. WHEN the Hosts_Viewer opens, THE System SHALL read and parse all entries from the hosts file
2. THE System SHALL filter and display only valid IP-domain mappings (excluding comments and empty lines)
3. WHEN the hosts file changes externally, THE Hosts_Viewer SHALL provide a refresh button to reload entries
4. IF the hosts file cannot be read, THEN THE System SHALL display an appropriate error message

### Requirement 2: iOS 风格界面设计

**User Story:** As a user, I want a beautiful iOS-style interface, so that the viewing experience is pleasant and modern.

#### Acceptance Criteria

1. THE Hosts_Viewer SHALL use a card-based layout with rounded corners (8-12px radius)
2. THE Hosts_Viewer SHALL use a clean color scheme with soft backgrounds (#F5F5F7 or similar)
3. THE Entry_Card SHALL display domain name prominently with IP address as secondary text
4. THE Hosts_Viewer SHALL use smooth transitions and hover effects for interactive elements
5. THE Hosts_Viewer SHALL use modern sans-serif fonts (Segoe UI on Windows)
6. THE Hosts_Viewer SHALL have consistent padding and spacing following iOS design guidelines

### Requirement 3: 条目管理功能

**User Story:** As a user, I want to manage hosts entries from the viewer, so that I can quickly remove outdated configurations.

#### Acceptance Criteria

1. WHEN a user clicks on an Entry_Card, THE System SHALL highlight the selected entry
2. THE Entry_Card SHALL provide a delete button with confirmation dialog
3. WHEN a user confirms deletion, THE System SHALL remove the entry from hosts file and refresh the view
4. WHEN deletion fails due to permissions, THE System SHALL display an error message suggesting admin privileges
5. THE Hosts_Viewer SHALL provide a "Delete All" button with confirmation for bulk removal

### Requirement 4: 搜索和过滤

**User Story:** As a user, I want to search and filter hosts entries, so that I can quickly find specific configurations.

#### Acceptance Criteria

1. THE Hosts_Viewer SHALL provide a search input field at the top
2. WHEN a user types in the search field, THE System SHALL filter entries in real-time by domain or IP
3. WHEN no entries match the search, THE System SHALL display a "No results" message
4. THE search field SHALL have a clear button to reset the filter

### Requirement 5: 窗口集成

**User Story:** As a user, I want to access the hosts viewer from the main application, so that I can easily check my configurations.

#### Acceptance Criteria

1. THE main GUI SHALL provide a button to open the Hosts_Viewer window
2. THE Hosts_Viewer SHALL open as a separate modal or top-level window
3. WHEN the Hosts_Viewer window closes, THE main GUI SHALL refresh its hosts status display
4. THE Hosts_Viewer window SHALL be resizable with a minimum size constraint

### Requirement 6: 管理员权限处理

**User Story:** As a user, I want the application to handle administrator privileges gracefully, so that I can modify hosts file without manual elevation.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL check if running with administrator privileges
2. THE main GUI SHALL display current privilege status (admin mode or normal mode)
3. WHEN a user attempts to modify hosts without admin privileges, THE System SHALL offer to restart with elevated privileges
4. IF the user confirms restart, THEN THE System SHALL restart itself with administrator privileges via UAC
5. WHEN packaged as EXE, THE application SHALL request administrator privileges at startup via UAC manifest

