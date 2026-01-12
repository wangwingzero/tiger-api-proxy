# Cloudflare Workers 动态 API 反代指南

## 工作原理

通过路径动态指定目标服务器，无需预先配置映射表。

**URL 格式：** `https://你的域名/claude/目标域名/路径`

| 原始地址 | 代理地址 |
|----------|----------|
| `https://anyrouter.top/v1/chat/completions` | `https://betterclau.de/claude/anyrouter.top/v1/chat/completions` |
| `https://pmpjfbhq.cn-nb1.rainapp.top/api/xxx` | `https://betterclau.de/claude/pmpjfbhq.cn-nb1.rainapp.top/api/xxx` |
| `https://a-ocnfniawgw.cn-shanghai.fcapp.run/v1/chat` | `https://betterclau.de/claude/a-ocnfniawgw.cn-shanghai.fcapp.run/v1/chat` |

---

## 🚀 动态代理 Workers 代码

```javascript
export default {
  async fetch(request, env, ctx) {
    // 1. 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, anthropic-version',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    try {
      const url = new URL(request.url);
      const pathname = url.pathname;

      // 2. 解析路径：/claude/目标域名/剩余路径
      const match = pathname.match(/^\/claude\/([^\/]+)(\/.*)?$/);
      
      if (!match) {
        return new Response(JSON.stringify({
          error: 'Not Found',
          message: '请使用正确的路径格式',
          format: '/claude/{目标域名}/{路径}',
          example: 'https://betterclau.de/claude/anyrouter.top/v1/chat/completions',
        }, null, 2), {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      const targetHost = match[1];  // 目标域名
      const targetPath = match[2] || '/';  // 剩余路径

      // 3. 构建目标 URL
      const targetUrl = new URL(targetPath, `https://${targetHost}`);
      targetUrl.search = url.search;  // 保留查询参数

      // 4. 复制请求头，清理 CF 特有头
      const headers = new Headers(request.headers);
      headers.set('Host', targetHost);
      ['cf-connecting-ip', 'cf-ipcountry', 'cf-ray', 'cf-visitor', 
       'x-real-ip', 'x-forwarded-for', 'x-forwarded-proto'].forEach(h => headers.delete(h));

      // 5. 构建代理请求
      const proxyRequest = new Request(targetUrl.toString(), {
        method: request.method,
        headers: headers,
        body: request.body,
        redirect: 'follow',
      });

      // 6. 发送请求到目标服务器
      const response = await fetch(proxyRequest);

      // 7. 构建响应头
      const responseHeaders = new Headers();
      responseHeaders.set('Access-Control-Allow-Origin', '*');

      // 8. 检测 SSE 流式响应（AI API 常用）
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('text/event-stream')) {
        responseHeaders.set('Content-Type', 'text/event-stream');
        responseHeaders.set('Cache-Control', 'no-cache');
        responseHeaders.set('Connection', 'keep-alive');
        return new Response(response.body, {
          status: response.status,
          headers: responseHeaders,
        });
      }

      // 9. 普通响应：复制原始响应头
      for (const [key, value] of response.headers.entries()) {
        if (!key.startsWith('cf-') && key !== 'set-cookie') {
          responseHeaders.set(key, value);
        }
      }

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });

    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Proxy Error',
        message: error.message,
      }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },
};
```

---

## 🔧 Claude Code 配置示例

```bash
# 使用 anyrouter 节点
ANTHROPIC_BASE_URL=https://betterclau.de/claude/anyrouter.top

# 使用 RainApp 节点
ANTHROPIC_BASE_URL=https://betterclau.de/claude/pmpjfbhq.cn-nb1.rainapp.top

# 使用阿里云函数节点
ANTHROPIC_BASE_URL=https://betterclau.de/claude/a-ocnfniawgw.cn-shanghai.fcapp.run
```

---

## 🎯 配合 CF Proxy Manager 使用

1. **目标反代节点**：填写目标域名（如 `anyrouter.top`）
2. **反代域名/URL**：填写完整代理地址（如 `https://betterclau.de/claude/anyrouter.top`）
3. **测速**：工具会测试 Cloudflare CDN IP 延迟
4. **应用最佳 IP**：将最快的 IP 写入 hosts 文件

这样访问 `betterclau.de` 时会直连最优的 CF 边缘节点，加速代理访问。

---

## 部署步骤

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 Workers & Pages
3. 创建新 Worker 或编辑已有的
4. 粘贴上述代码
5. 点击 Deploy
6. 绑定自定义域名（如 `betterclau.de`）
7. 测试：访问 `https://betterclau.de/claude/anyrouter.top/` 应返回目标服务器响应

---

## ⚠️ 注意事项

1. **动态目标**：可代理任意域名，无需修改 Workers 代码
2. **路径格式**：`/claude/目标域名/路径`，目标域名从路径中提取
3. **免费额度**：Workers 免费版每天 10 万次请求
4. **SSE 流式**：完整支持 Claude/OpenAI 的流式响应
5. **安全提示**：建议添加访问控制，避免被滥用

完成！🎉
const TARGETS = {
  '/anyrouter': 'anyrouter.top',
  '/aliyun': 'a-ocnfniawgw.cn-shanghai.fcapp.run',
  '/rainapp': 'pmpjfbhq.cn-nb1.rainapp.top',
  '/newapi': 'new-api-server.com',  // 新增
};
```

---

## 部署步骤

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 Workers & Pages
3. 选择已有 Worker 或创建新的
4. 粘贴上述代码，替换原有内容
5. 点击 Deploy
6. 测试：访问 `https://你的域名/anyrouter/` 应返回目标服务器响应

---

## ⚠️ 注意事项

1. **路径前缀会被移除**：`/anyrouter/v1/chat` → `anyrouter.top/v1/chat`
2. **免费额度**：Workers 免费版每天 10 万次请求
3. **SSE 流式**：完整支持 Claude/OpenAI 的流式响应
4. **超时**：Workers 免费版 CPU 时间限制 10ms，但 I/O 等待不计入

完成！🎉
