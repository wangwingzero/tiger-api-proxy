# 🎨 虎哥API反代 - AI 绘图提示词

用于生成项目图标和 GitHub 展示图片的 AI 提示词。

---

## 1. 应用图标 (icon.ico / icon.png)

### 提示词 (English)

```
A modern app icon for a network proxy tool called "Tiger API Proxy". 
Design: A cute cartoon tiger face with tech elements, wearing small glasses or headphones.
The tiger has orange fur with black stripes, friendly expression.
Background: Cloudflare orange (#F6821F) gradient to white.
Include subtle network/cloud symbols around the tiger.
Style: Flat design, iOS app icon style, rounded corners.
Size: 512x512, clean vector-like appearance.
No text in the icon.
```

### 提示词 (中文)

```
一个现代化的应用图标，用于名为"虎哥API反代"的网络代理工具。
设计：一只可爱的卡通老虎头像，带有科技元素，戴着小眼镜或耳机。
老虎有橙色毛皮和黑色条纹，表情友好。
背景：Cloudflare 橙色 (#F6821F) 渐变到白色。
在老虎周围添加微妙的网络/云符号。
风格：扁平化设计，iOS 应用图标风格，圆角。
尺寸：512x512，干净的矢量外观。
图标中不要有文字。
```

---

## 2. GitHub 仓库封面图 (banner.png)

### 提示词 (English)

```
A wide banner image for a GitHub repository.
Theme: Network proxy optimization tool with Cloudflare.
Left side: Cute cartoon tiger mascot (orange with black stripes) holding a network cable or router.
Center: Large text "虎哥API反代" in bold modern Chinese font.
Right side: Cloudflare logo style cloud icons, speed meter showing fast connection.
Background: Gradient from dark blue (#1a1a2e) to Cloudflare orange (#F6821F).
Include subtle circuit board patterns and network nodes.
Style: Modern tech, clean, professional.
Size: 1280x640 pixels, suitable for GitHub social preview.
```

### 提示词 (中文)

```
一张 GitHub 仓库的宽幅横幅图片。
主题：Cloudflare 网络代理优化工具。
左侧：可爱的卡通老虎吉祥物（橙色带黑色条纹），手持网线或路由器。
中间：大号文字"虎哥API反代"，使用粗体现代中文字体。
右侧：Cloudflare 风格的云图标，显示快速连接的速度表。
背景：从深蓝色 (#1a1a2e) 渐变到 Cloudflare 橙色 (#F6821F)。
包含微妙的电路板图案和网络节点。
风格：现代科技感，干净，专业。
尺寸：1280x640 像素，适合 GitHub 社交预览。
```

---

## 3. README 功能展示图 (feature-icons/)

### 3.1 测速功能图标

```
A simple flat icon representing speed testing.
Design: A stopwatch or speedometer with lightning bolt.
Colors: Cloudflare orange (#F6821F) and white.
Style: Minimalist, flat design, no gradients.
Size: 128x128, transparent background.
```

### 3.2 Hosts 管理图标

```
A simple flat icon representing hosts file management.
Design: A document/file icon with network nodes or IP address symbols.
Colors: Blue (#007AFF) and white.
Style: Minimalist, flat design, iOS style.
Size: 128x128, transparent background.
```

### 3.3 配置保存图标

```
A simple flat icon representing configuration saving.
Design: A gear/settings icon combined with a save/disk symbol.
Colors: Green (#34C759) and white.
Style: Minimalist, flat design.
Size: 128x128, transparent background.
```

---

## 4. 界面截图装饰框 (screenshot-frame.png)

### 提示词

```
A modern macOS/Windows style window frame mockup.
Design: Clean window chrome with minimize, maximize, close buttons.
Title bar shows "🐯 虎哥API反代".
Background: Subtle gradient, professional look.
Style: Modern OS window decoration, drop shadow.
Size: 800x600, with transparent center area for screenshot placement.
```

---

## 5. 老虎吉祥物完整形象 (mascot.png)

### 提示词 (English)

```
A full-body cartoon tiger mascot for a tech project.
Design: Cute, friendly tiger standing upright.
- Orange fur with black stripes
- Wearing a small hoodie with cloud/network pattern
- Holding a laptop or tablet
- Big friendly eyes, slight smile
- Tech-savvy appearance
Background: Transparent or light gradient.
Style: Modern cartoon, suitable for tech branding.
Size: 1024x1024, high quality.
```

### 提示词 (中文)

```
一个科技项目的全身卡通老虎吉祥物。
设计：可爱、友好的老虎直立站姿。
- 橙色毛皮带黑色条纹
- 穿着带有云/网络图案的小卫衣
- 手持笔记本电脑或平板
- 大大的友好眼睛，微微微笑
- 科技感外观
背景：透明或浅色渐变。
风格：现代卡通，适合科技品牌。
尺寸：1024x1024，高质量。
```

---

## 6. 社交媒体分享图 (og-image.png)

### 提示词

```

```

---

## 📝 使用建议

1. **图标格式**：生成后转换为 .ico 格式用于 EXE 打包
2. **推荐工具**：
   - Midjourney / DALL-E 3 / Stable Diffusion
   - 图标转换：https://convertio.co/png-ico/
3. **颜色参考**：
   - Cloudflare 橙：#F6821F
   - iOS 蓝：#007AFF
   - iOS 绿：#34C759
   - iOS 红：#FF3B30

---

## 📁 建议的文件结构

```
assets/
├── icon.ico              # 应用图标 (256x256)
├── icon.png              # 应用图标 PNG 版本
├── banner.png            # GitHub 横幅 (1280x640)
├── mascot.png            # 吉祥物完整形象
├── og-image.png          # 社交分享图
└── screenshots/
    ├── main-window.png   # 主界面截图
    └── hosts-viewer.png  # Hosts 查看器截图
```
