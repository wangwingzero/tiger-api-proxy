# Requirements Document

## Introduction

本文档定义了将 CF Proxy Manager 从 Tkinter 迁移到 CustomTkinter 的需求，实现现代化 UI/UX 设计，解决 IP 列表显示问题，并提供深色/浅色主题支持。

## Glossary

- **CTk_App**: 基于 CustomTkinter 的主应用窗口
- **IP_Card**: IP 地址卡片组件，显示单个 IP 的信息和状态
- **Latency_Badge**: 延迟徽章，用颜色和数值显示连接速度
- **Theme_System**: 主题系统，支持深色和浅色模式切换
- **Scrollable_Frame**: 可滚动的 IP 列表容器

## Requirements

### Requirement 1: CustomTkinter 框架迁移

**User Story:** As a developer, I want to migrate the GUI to CustomTkinter, so that the application has a modern appearance.

#### Acceptance Criteria

1. THE CTk_App SHALL use `customtkinter` library as the primary GUI framework
2. THE CTk_App SHALL maintain all existing functionality from the Tkinter version
3. THE CTk_App SHALL support both dark and light appearance modes
4. WHEN the application starts, THE CTk_App SHALL detect system theme and apply matching appearance

### Requirement 2: IP 列表卡片式显示

**User Story:** As a user, I want IP addresses displayed as cards, so that I can easily read and interact with each IP.

#### Acceptance Criteria

1. WHEN displaying IP entries, THE Scrollable_Frame SHALL show each IP as a separate IP_Card
2. THE IP_Card SHALL display: IP address, port, latency value, and status indicator
3. THE IP_Card SHALL use monospace font (Consolas) for IP address to ensure digit alignment
4. WHEN an IP_Card is clicked, THE IP_Card SHALL toggle selection state with visual feedback
5. THE IP_Card SHALL have minimum height of 50px for comfortable touch/click targets

### Requirement 3: 延迟颜色编码

**User Story:** As a user, I want to see latency values color-coded, so that I can quickly identify fast and slow connections.

#### Acceptance Criteria

1. WHEN latency is below 100ms, THE Latency_Badge SHALL display with green background (#28a745)
2. WHEN latency is between 100ms and 300ms, THE Latency_Badge SHALL display with orange background (#fd7e14)
3. WHEN latency is above 300ms, THE Latency_Badge SHALL display with red background (#dc3545)
4. WHEN latency test is pending, THE Latency_Badge SHALL display with gray background (#6c757d)
5. THE Latency_Badge SHALL show latency value in white text for contrast

### Requirement 4: 最佳 IP 高亮

**User Story:** As a user, I want the best IP to be visually prominent, so that I can quickly identify the optimal choice.

#### Acceptance Criteria

1. WHEN test results are available, THE IP_Card with lowest latency SHALL display a "⭐ 最佳" badge
2. THE best IP_Card SHALL have a distinct border color (green or gold)
3. WHEN applying best IP, THE system SHALL auto-select the highlighted best IP

### Requirement 5: 主题系统

**User Story:** As a user, I want to switch between dark and light themes, so that I can use the app comfortably in different lighting conditions.

#### Acceptance Criteria

1. THE Theme_System SHALL support three modes: "dark", "light", "system"
2. WHEN user selects a theme, THE CTk_App SHALL immediately apply the new appearance
3. THE Theme_System SHALL persist user's theme preference to config file
4. WHEN set to "system" mode, THE CTk_App SHALL follow OS appearance setting

### Requirement 6: 现代化按钮和输入框

**User Story:** As a user, I want modern-looking controls, so that the app feels professional and up-to-date.

#### Acceptance Criteria

1. THE CTk_App SHALL use CTkButton with rounded corners (corner_radius=8)
2. THE CTk_App SHALL use CTkEntry with rounded corners for text input
3. THE primary action button (开始测速) SHALL have accent color background
4. WHEN a button action is in progress, THE button SHALL show disabled state
5. THE CTk_App SHALL use consistent padding (10px) between UI elements
