# Design Document: Proxy Comparison Feature

## Overview

本设计为 CF Proxy Manager 添加反代效果对比功能，让用户能够直观地比较不同反代方案的延迟效果。该功能将作为主界面的一个新区域，提供一键对比测试、结果可视化展示和快速应用的能力。

## Architecture

### 组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CFProxyManagerCTk                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              📊 效果对比区域 (新增)                    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │         ComparisonSection (新组件)           │    │   │
│  │  │  ┌─────────────────────────────────────┐    │    │   │
│  │  │  │     ComparisonCard (结果卡片)        │    │    │   │
│  │  │  └─────────────────────────────────────┘    │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户点击"开始对比"
       │
       ▼
┌──────────────────┐
│ ComparisonTester │ ──并行测试──▶ [直连, 优选IP, 对比服务...]
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ ComparisonResult │ ──计算提升百分比──▶ 排序结果
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ ComparisonCard   │ ──渲染──▶ UI 展示
└──────────────────┘
```

## Components and Interfaces

### 1. ComparisonService (数据模型)

```python
@dataclass
class ComparisonService:
    """对比服务"""
    name: str           # 服务名称，如 "宁波节点"
    url: str            # 服务 URL
    description: str    # 描述，如 "阿里云函数计算"
    is_default: bool    # 是否为默认服务
    
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> "ComparisonService"
```

### 2. ComparisonResult (数据模型)

```python
@dataclass
class ComparisonResult:
    """对比测试结果"""
    service: ComparisonService
    latency_ms: Optional[float]  # None 表示失败
    success: bool
    error_message: str = ""
    improvement_pct: Optional[float] = None  # 相对基准的提升百分比
    is_baseline: bool = False  # 是否为基准测试
    is_optimized: bool = False  # 是否为优选IP测试
    
    @property
    def latency_level(self) -> str:
        """返回延迟等级: 'fast', 'medium', 'slow'"""
        if self.latency_ms is None:
            return 'failed'
        if self.latency_ms < 200:
            return 'fast'
        if self.latency_ms < 500:
            return 'medium'
        return 'slow'
```

### 3. ComparisonTester (测试器)

```python
class ComparisonTester:
    """对比测试器"""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
    
    def test_https_latency(self, url: str) -> Tuple[Optional[float], str]:
        """
        测试 HTTPS 连接延迟（包含 SSL 握手）
        
        Returns:
            (latency_ms, error_message) - 成功时 error_message 为空
        """
    
    def test_via_ip(self, domain: str, ip: str, port: int = 443) -> Tuple[Optional[float], str]:
        """
        通过指定 IP 测试域名连接延迟
        """
    
    def run_comparison(
        self,
        user_domain: str,
        optimized_ip: Optional[str],
        services: List[ComparisonService],
        callback: Optional[Callable[[int, int, ComparisonResult], None]] = None
    ) -> List[ComparisonResult]:
        """
        运行完整对比测试
        
        Args:
            user_domain: 用户反代域名
            optimized_ip: 优选 IP（可选）
            services: 对比服务列表
            callback: 进度回调
        
        Returns:
            排序后的对比结果列表
        """
    
    @staticmethod
    def calculate_improvement(baseline_ms: float, test_ms: float) -> float:
        """计算相对基准的提升百分比"""
        return ((baseline_ms - test_ms) / baseline_ms) * 100
    
    @staticmethod
    def sort_results(results: List[ComparisonResult]) -> List[ComparisonResult]:
        """按延迟排序结果（成功的在前，按延迟升序）"""
```

### 4. ComparisonCard (UI 组件)

```python
class ComparisonCard(ctk.CTkFrame):
    """对比结果卡片"""
    
    def __init__(
        self,
        parent,
        result: ComparisonResult,
        is_best: bool = False,
        on_select: Optional[Callable] = None
    ):
        """
        Args:
            result: 对比结果
            is_best: 是否为最佳选项
            on_select: 选中回调
        """
    
    def _get_latency_color(self) -> str:
        """根据延迟等级返回颜色"""
    
    def _format_improvement(self) -> str:
        """格式化提升百分比显示"""
```

### 5. ComparisonSection (UI 区域)

```python
class ComparisonSection(ctk.CTkFrame):
    """效果对比区域"""
    
    def __init__(self, parent, config: Config, on_apply: Callable):
        """
        Args:
            config: 应用配置
            on_apply: 应用选中结果的回调
        """
    
    def _create_widgets(self):
        """创建界面组件"""
    
    def _on_start_comparison(self):
        """开始对比测试"""
    
    def _on_manage_services(self):
        """管理对比服务"""
    
    def _on_reset_defaults(self):
        """恢复默认服务"""
    
    def _display_results(self, results: List[ComparisonResult]):
        """显示对比结果"""
```

## Data Models

### Config 扩展

```python
@dataclass
class Config:
    # ... 现有字段 ...
    
    # 新增字段
    comparison_services: List[ComparisonService] = field(default_factory=list)
```

### 默认对比服务

```python
DEFAULT_COMPARISON_SERVICES = [
    ComparisonService(
        name="上海节点",
        url="https://a-ocnfniawgw.cn-shanghai.fcapp.run",
        description="阿里云函数计算",
        is_default=True
    ),
    ComparisonService(
        name="宁波节点",
        url="https://pmpjfbhq.cn-nb1.rainapp.top",
        description="RainApp",
        is_default=True
    ),
    ComparisonService(
        name="AnyRouter",
        url="https://anyrouter.top",
        description="AnyRouter 反代",
        is_default=True
    ),
    ComparisonService(
        name="BetterClaude",
        url="https://betterclau.de/claude/anyrouter.top",
        description="BetterClaude 反代",
        is_default=True
    ),
]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: URL Validation Correctness

*For any* string input, the URL validator should accept only valid HTTPS URLs with proper format (scheme, host, optional path) and reject malformed URLs.

**Validates: Requirements 1.2**

### Property 2: Service List Removal Invariant

*For any* list of comparison services and any service in that list, after removal, the resulting list should not contain that service and should have length decreased by exactly 1.

**Validates: Requirements 1.3**

### Property 3: Reset to Defaults Idempotence

*For any* modified comparison services list, resetting to defaults should produce a list equal to DEFAULT_COMPARISON_SERVICES, and resetting multiple times should produce the same result.

**Validates: Requirements 1.4**

### Property 4: Configuration Round-Trip

*For any* valid Config object with comparison_services, serializing to dict then deserializing should produce an equivalent Config object.

**Validates: Requirements 1.5**

### Property 5: Improvement Percentage Calculation

*For any* baseline latency > 0 and test latency >= 0, the improvement percentage should equal `(baseline - test) / baseline * 100`. Positive values indicate improvement, negative values indicate degradation.

**Validates: Requirements 2.5**

### Property 6: Results Sorting Order

*For any* list of ComparisonResults, after sorting:
- All successful results appear before failed results
- Successful results are ordered by latency_ms in ascending order

**Validates: Requirements 3.3**

### Property 7: Best Result Selection

*For any* non-empty list of ComparisonResults with at least one successful result, the "best" result should have the minimum latency_ms among all successful results.

**Validates: Requirements 3.4**

## Error Handling

| 场景 | 处理方式 |
|------|----------|
| 网络超时 | 显示 "连接超时"，继续测试其他服务 |
| SSL 握手失败 | 显示 "SSL 错误"，记录详细错误信息 |
| DNS 解析失败 | 显示 "DNS 解析失败" |
| 用户域名未配置 | 禁用对比按钮，提示先配置域名 |
| 无优选 IP | 跳过优选 IP 测试，只测试直连和对比服务 |
| 所有测试失败 | 显示 "所有服务均不可用" |
| Hosts 文件写入失败 | 提示需要管理员权限 |

## Testing Strategy

### 单元测试

1. **ComparisonService 序列化测试**
   - 测试 to_dict/from_dict 往返一致性
   - 测试默认值处理

2. **ComparisonResult 测试**
   - 测试 latency_level 属性计算
   - 测试边界值（0ms, 200ms, 500ms）

3. **URL 验证测试**
   - 测试有效 HTTPS URL
   - 测试无效 URL（无协议、HTTP、格式错误）

### 属性测试 (Property-Based Testing)

使用 `hypothesis` 库进行属性测试：

1. **Property 1**: URL 验证 - 生成随机字符串，验证验证器行为一致
2. **Property 2**: 列表移除 - 生成随机服务列表，验证移除后的不变量
3. **Property 3**: 重置幂等性 - 生成随机修改后的列表，验证重置结果
4. **Property 4**: 配置往返 - 生成随机 Config，验证序列化往返
5. **Property 5**: 百分比计算 - 生成随机延迟值，验证计算公式
6. **Property 6**: 排序顺序 - 生成随机结果列表，验证排序后的顺序
7. **Property 7**: 最佳选择 - 生成随机结果列表，验证最佳选择正确性

### 测试配置

- 每个属性测试运行至少 100 次迭代
- 使用 `@settings(max_examples=100)` 配置
- 测试文件: `cf_proxy_manager/tests/test_comparison.py`
