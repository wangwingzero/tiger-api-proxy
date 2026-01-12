# V2Ray 订阅导入功能需求文档

## 简介

为 CF Proxy Manager 添加从 V2Ray/Xray 订阅链接批量导入优选 IP 的功能，支持解析 vless、trojan、vmess 协议链接，提取 IP 地址和反代域名。

## 术语表

- **V2Ray_Parser**: V2Ray 链接解析器
- **IP_Importer**: IP 导入器组件
- **CNAME_Resolver**: 域名解析器

## 需求

### 需求 1: 解析 V2Ray 订阅链接

**用户故事:** 作为用户，我想粘贴 V2Ray 订阅内容，自动提取其中的 IP 和域名。

#### 验收标准

1. WHEN 用户粘贴包含 vless:// 链接的文本 THEN V2Ray_Parser SHALL 提取服务器地址和端口
2. WHEN 用户粘贴包含 trojan:// 链接的文本 THEN V2Ray_Parser SHALL 提取服务器地址和端口
3. WHEN 用户粘贴包含 vmess:// 链接的文本 THEN V2Ray_Parser SHALL 解码 Base64 并提取服务器地址和端口
4. WHEN 服务器地址是 IP 格式 THEN V2Ray_Parser SHALL 直接添加到 IP 列表
5. WHEN 服务器地址是域名格式 THEN V2Ray_Parser SHALL 标记为待解析域名

### 需求 2: 域名解析为 IP

**用户故事:** 作为用户，我想自动解析反代域名获取当前最优 IP。

#### 验收标准

1. WHEN 检测到域名地址 THEN CNAME_Resolver SHALL 执行 DNS 解析获取 IP
2. WHEN DNS 解析成功 THEN CNAME_Resolver SHALL 返回解析到的 IP 地址
3. WHEN DNS 解析失败 THEN CNAME_Resolver SHALL 记录错误并跳过该域名
4. WHEN 解析到多个 IP THEN CNAME_Resolver SHALL 返回所有 IP 地址

### 需求 3: 批量导入 IP

**用户故事:** 作为用户，我想一键导入所有提取的 IP 到优选列表。

#### 验收标准

1. WHEN 用户点击导入按钮 THEN IP_Importer SHALL 将所有提取的 IP 添加到配置
2. WHEN IP 已存在于列表中 THEN IP_Importer SHALL 跳过重复项
3. WHEN 导入完成 THEN IP_Importer SHALL 显示导入统计（新增/跳过/失败）
4. WHEN 导入过程中 THEN IP_Importer SHALL 显示进度状态

### 需求 4: 导入界面

**用户故事:** 作为用户，我想有一个清晰的界面来管理导入过程。

#### 验收标准

1. WHEN 用户点击"导入订阅" THEN 系统 SHALL 显示导入对话框
2. WHEN 对话框打开 THEN 系统 SHALL 显示文本输入区域和选项
3. WHEN 用户粘贴内容 THEN 系统 SHALL 实时预览提取结果
4. WHEN 显示预览 THEN 系统 SHALL 分类显示 IP 和域名数量
