# 开发记录

## 前端全黑页面排查

### 问题
启动前端后页面全黑，无内容渲染。

### 排查思路
- 后端 `/health` 返回 200，运行正常
- 前端 Vite 开发服务器运行正常，HTML 正常返回
- Vite proxy 正常工作，`/api/v1/auto_login` 可获取 token
- `index.html` 中 `<body class="dark">` 默认启用暗色模式
- `LoadingPage` 使用 `bg-background`，在暗色模式下为 `hsl(240, 6%, 10%)`（深灰色）
- `LoadingPage` 嵌套 `LoadingComponent`，包含 SVG 旋转动画和 "Loading..." 文字
- 首页实际处于 `AppInitPage` 初始化阶段，需等待多个 API 请求完成后才进入主页面

### 结论
"全黑" 实际是暗色主题下 `LoadingPage` 的正常深色背景 + 初始化加载状态。前端需等待后端多个 API（auto_login、config、version 等）响应完成后才会跳转主页面。后端运行正常时短暂停留后即可进入。

---

## 前端报错：Error: Unknown variable dynamic import: ./locales/zh.json

### 问题
浏览器控制台报错 `Error: Unknown variable dynamic import: ./locales/zh.json`，中文用户进入页面时触发。

### 根因分析
文件调用链路：
1. `src/frontend/src/index.tsx` 第 18 行：
   ```ts
   navigator.language.split("-")[0]
   ```
   浏览器语言 `zh-CN` 被截取为 `zh`。

2. `src/frontend/src/i18n.ts` 第 19 行：
   ```ts
   const messages = await import(`./locales/${lang}.json`);
   ```
   动态导入尝试加载 `./locales/zh.json`。

3. 但实际 locale 文件命名为 `zh-Hans.json`，不存在 `zh.json`，导致 Vite 无法解析此动态导入路径。

### 解决方案

**修改 1** — 创建 `src/frontend/src/locales/zh.json`：
```bash
cp src/frontend/src/locales/zh-Hans.json src/frontend/src/locales/zh.json
```

**修改 2** — `src/frontend/src/i18n.ts` 加入静态导入并注册资源 bundle：
```ts
import zh from "./locales/zh.json";

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    zh: { translation: zh },  // 新增
  },
  // ...
});
```

### 修复原理
- `zh` bundle 在 i18n 初始化时已静态注册
- `loadLanguage("zh")` 调用时，`i18n.hasResourceBundle("zh", "translation")` 返回 `true`
- 直接跳过动态导入，不再触发 Vite 解析异常

### 涉及文件
- `src/frontend/src/locales/zh-Hans.json`（源文件，388 行）
- `src/frontend/src/locales/zh.json`（新建，内容同 zh-Hans.json）
- `src/frontend/src/i18n.ts`（添加 import 和 resource 注册）
- `src/frontend/src/index.tsx`（语言检测逻辑，`zh-CN` → `zh`）
- `src/frontend/src/constants/languages.ts`（支持的语言列表，code 为 `zh-Hans`）

### 官方状态
官方已了解此问题，不会对已发行版本打补丁，预计在 **v1.10.0** 版本中修复。
