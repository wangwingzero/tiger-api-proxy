---
inclusion: always
---

# CustomTkinter UI 开发规范

## 对话框窗口设计

### 窗口尺寸

- **始终设置 minsize**: 防止窗口被压缩到内容无法显示
- **预留足够高度**: 计算所有组件高度总和，额外预留 50-100px 余量
- **允许调整大小**: 除非有特殊原因，否则设置 `resizable(True, True)`

```python
# ✅ 正确做法
self.geometry("520x550")
self.minsize(520, 550)
self.resizable(True, True)

# ❌ 错误做法 - 可能导致内容被压扁
self.geometry("520x500")
self.resizable(False, False)
```

### 按钮区域

- **固定高度**: 按钮设置明确的 `height` 参数（建议 32-40px）
- **底部间距**: 按钮区域使用 `pady=(10, 0)` 确保与上方内容有间隔
- **不要依赖自动高度**: 按钮可能因为空间不足被压扁

```python
# ✅ 正确做法
button_frame.pack(fill="x", pady=(10, 0))
ctk.CTkButton(frame, text="确定", width=100, height=36)

# ❌ 错误做法 - 按钮可能被压扁
button_frame.pack(fill="x")
ctk.CTkButton(frame, text="确定", width=100)
```

### 布局优先级

1. 固定高度的组件（标题、按钮）使用 `pack()` 不带 `expand`
2. 可变高度的组件（文本框、列表）使用 `pack(fill="both", expand=True)`
3. 按钮区域始终放在最后 pack，确保不会被挤压

### 高度计算参考

| 组件类型 | 建议最小高度 |
|---------|-------------|
| 标题标签 | 30px |
| 输入框 | 36px |
| 多行文本框 | 150-200px |
| 复选框 | 30px |
| 按钮 | 36px |
| 间距 (pady) | 10-20px |

### 对话框高度估算公式

```
总高度 = 顶部边距(20) + 标题(30) + 文本框(180) + 选项区(70) + 预览区(100) + 状态(30) + 按钮(50) + 底部边距(20) + 余量(50)
       ≈ 550px
```

## 常见问题排查

### 按钮被压扁或不可见

1. 检查窗口 `geometry` 高度是否足够
2. 检查是否设置了 `minsize`
3. 检查按钮是否设置了明确的 `height`
4. 检查上方组件是否使用了过多的 `expand=True`

### 内容溢出窗口

1. 增加窗口高度
2. 将可滚动内容放入 `CTkScrollableFrame`
3. 设置 `resizable(True, True)` 允许用户调整
