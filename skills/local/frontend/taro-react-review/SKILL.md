---
name: taro-react-review
description: >
  Performs an expert code review for this Taro + React blended-mode project (react-taro-teacher),
  covering project-specific conventions, Taro pitfalls, and React/TypeScript best practices.
  Trigger this skill whenever the user asks to review, audit, check, or give feedback on
  code — even if they just say "帮我看看这段代码", "review 一下", "有什么问题", "check my component",
  or paste code without explanation. Also trigger for "这样写对吗", "有没有 bug", "怎么优化",
  or any time the user shares React/Taro/TSX/JSX code snippets.
---

# react-taro-teacher Code Review Skill

你是一个深度了解本项目（react-taro-teacher）架构和约定的高级工程师。Review 代码时，优先检查**项目特有规范**，再覆盖通用最佳实践。

---

## Input Modes

**Mode A — Single snippet**（用户贴代码）：直接 review。

**Mode B — File-based**（用户给文件路径）：先读文件再 review。

**Mode C — Git diff**（review 当前改动）：`git diff` 获取变更，聚焦变更部分。

---

## Review 维度

### 1. 🔴 项目约定检查（Project Conventions）

这是最重要的维度，违反项目约定 = 必须修复。

| 检查项 | 正确做法 | 常见错误 |
|---|---|---|
| **导航函数** | 使用 `navigateToEnhance` / `navigateBackEnhance` / `redirectToEnhance` / `reLaunchEnhance` | 直接用 `Taro.navigateTo` / `Taro.navigateBack` 等原生 API |
| **API 调用** | 通过 `src/api/` 下的模块文件调用，底层用 `requestWithNewUrl` / `requestWithOldUrl` | 组件内直接 `Taro.request` 或自建请求 |
| **状态管理** | Zustand store（`src/store/`），每个模块独立 store，字段有独立 setter | 用 React Context 做全局状态、组件间用 prop drilling 超 3 层 |
| **Toast + 导航** | `Taro.showToast` 后用 `setTimeout`（成功 ~500ms，错误 ~1500ms）再导航 | 在 `showToast({ complete })` 回调中导航（真机上用户看不到 toast） |
| **滚动条隐藏** | ScrollView 加 `showScrollbar={false}` + CSS 隐藏；普通 View 用 CSS 兼容方案 | 滚动区域显示默认滚动条 |
| **组件显隐** | 条件渲染 `{open && <Component />}` 控制挂载/卸载 | 用 `ref.show()` / `visible` prop 控制显隐 |
| **样式方案** | TailwindCSS 优先 + `twMerge` 合并类名；复杂样式用 CSS Modules（`.module.scss`） | 内联 style 对象写大量样式、className 字符串硬编码不用 CSS Modules |

### 2. 🔴 Taro 兼容性（Taro-Specific）

| 检查项 | 说明 |
|---|---|
| HTML 原生标签 | `<div>` `<span>` `<img>` → 必须用 `<View>` `<Text>` `<Image>` |
| 条件渲染 `&&` | `{count && <X/>}` 当 count=0 渲染 `"0"` → 用 `{!!count && <X/>}` 或 `{count > 0 && <X/>}` |
| 事件命名 | `bindtap` `catchtap` → `onClick` `onChange` |
| 页面配置 | 导航标题、背景色等必须在 `.config.ts` 中，不能在组件内设置 |
| Taro API | 使用 `Taro.xxx` 而非 `wx.xxx`；导航用项目封装函数而非 `Taro.navigateTo` |
| 样式单位 | 使用 TailwindCSS 的 rpx 值（项目已配置），或手写 `rpx` |
| WxNav | 小程序页面必须使用 `WxNav` 组件管理自定义导航栏 |

### 3. ⚡ React Hooks & 生命周期

| 原生小程序 | Taro 正确写法 | 常见错误 |
|---|---|---|
| `onLoad(options)` | `useEffect(() => {}, [])` + `useRouter().params` | 漏取参数 |
| `onShow` | `useDidShow(() => {})` | 用 `useEffect` — 页面返回时不触发 |
| `onHide` | `useDidHide(() => {})` | 省略 → 定时器/监听器泄露 |
| `onPullDownRefresh` | `usePullDownRefresh()` + config 启用 | 漏写 `enablePullDownRefresh: true` |
| `onReachBottom` | `useReachBottom()` | 改成 scroll 事件监听 |

**Hooks 通用：**
- `useEffect` 依赖数组缺失或不完整（stale closure）
- `useEffect` 内 async 直接标记（应内部定义 async 函数再调用）
- 条件语句/循环中调用 Hook
- 项目有 ahooks（`useRequest`、`useMemoizedFn` 等），适当场景应优先使用

### 4. 📘 TypeScript 规范

- **禁止 `any`**：用 `unknown` + 类型收窄代替
- **接口命名**：Props → `XxxProps`，API 返回 → `XxxResponse` / `XxxData`
- **非空断言 `!`**：过度使用掩盖 null 问题 → 用 `?.` 替代
- **泛型约束**：缺少约束时加 `extends` 限定
- **导出 Props 类型**：组件 Props 建议 `export`

### 5. 🏗️ 组件设计

- **单一职责**：页面组件负责组合，不直接写业务逻辑；UI 组件不发请求
- **组件大小**：JSX 超 150 行建议拆分；单文件超 300 行考虑拆模块
- **Props 设计**：
  - 样式覆盖优先用 `className`（外部 TailwindCSS 覆盖），不要设计大量样式 props（height/backgroundColor 等）
  - 只对有语义的配置项保留 prop
  - 布尔 props 用正向命名：`isLoading` 而非 `notReady`
- **Magic number/string**：提取为具名常量
- **条件渲染复杂**：超 3 个分支用对象映射或独立子组件
- **清理调试代码**：不留 `console.log` / 注释掉的代码

### 6. 🗂️ Zustand Store 使用规范

- **模块隔离**：每个业务模块独立 store 文件，不要把不相关的状态放同一个 store
- **独立 setter**：每个字段提供独立的 `setXxx` 方法，不要暴露通用 `set`
- **深层更新用 Immer**：复杂嵌套状态用 `produce()` 包装
- **状态派生**：能从已有 state 计算的值不要再存 store，用 `useMemo` 或直接计算
- **store 清空影响**：修改 `clearXxx` 方法时，确认被清空字段与依赖页面的实际数据来源（local state / store / API 重新拉取）是否有交集

### 7. 🌐 请求 & 数据层

- **统一走 api 层**：所有请求通过 `src/api/xxx-api.ts` → `requestWithNewUrl` / `requestWithOldUrl`，不在组件内裸调
- **ahooks useRequest**：数据请求优先考虑 `useRequest`，自带 loading/error/refresh
- **请求竞态**：快速切参数时旧请求覆盖新结果 → useEffect cleanup 设 cancelled flag，或用 `useRequest` 自动处理
- **错误上报**：catch 块不要只 `console.error`，生产环境应上报 Sentry

### 8. ⚡ 性能

- **内联对象/数组**：JSX 中 `style={{}}` 或 `value={[]}` 每次创建新引用 → 提取到组件外或用 `useMemo`
- **列表 key**：用业务唯一 ID，不用 index
- **不过度优化**：基本类型计算、简单字符串拼接不需要 `useMemo`/`useCallback`
- **大列表**：超 50 条考虑虚拟滚动或分页
- **Image**：加 `lazyLoad`，大图用 CDN

### 9. 🧩 Blended 模式注意事项

- **页面注册**：新页面需在 `src/modulePagesConfig.ts` 对应模块中注册
- **分包体积**：注意单个模块不要引入过重的依赖，用 `pnpm run analyzer` 检查
- **跨分包跳转**：路径需包含完整分包前缀
- **原生组件对齐**：从原生迁移过来的组件，要核对原生 wxml/wxss 的实际样式值和 props 默认值，不凭印象写

---

## Output Format

```
## 📋 Code Review: <文件名或描述>
**总体评估**: 🟢 可合入 / 🟡 需修复后合入 / 🔴 存在严重问题

### 📊 维度总览
| 维度 | 状态 | 问题数 |
|---|---|---|
| 项目约定 | 🟢/🟡/🔴 | N |
| Taro 兼容性 | 🟢/🟡/🔴 | N |
| Hooks & 生命周期 | 🟢/🟡/🔴 | N |
| TypeScript | 🟢/🟡/🔴 | N |
| 组件设计 | 🟢/🟡/🔴 | N |
| Zustand Store | 🟢/🟡/🔴 | N |
| 请求 & 数据层 | 🟢/🟡/🔴 | N |
| 性能 | 🟢/🟡/🔴 | N |
| Blended 模式 | 🟢/🟡/🔴 | N |

---

### 🔴 P0 — 必须修复（功能 bug / 项目约定违反）
#### [问题标题]
- **位置**: `行号` 或代码片段
- **问题**: 具体说明
- **原代码**: ```tsx ... ```
- **修复建议**: ```tsx ... ```

### 🟡 P1 — 建议修复（潜在 bug / 体验问题）
[同上格式]

### 🔵 P2 — 可选优化（代码质量 / 性能）
[同上格式]

### ✅ 做得好的地方
- [值得肯定的写法]

### 📋 行动清单
- [ ] P0: 行N — 问题描述
- [ ] P1: 行N — 问题描述
```

---

## Rules

1. **项目约定优先** — 违反项目约定的问题一律 P0，比通用最佳实践更重要
2. **有问题才说** — 没有问题的维度一句话带过，不凑字数
3. **给代码** — 每个问题必须提供修复后的代码
4. **说原因** — 解释为什么是问题，不只是"这样写不对"
5. **语言** — 报告中文，代码英文
6. **不教条** — 不强推项目不用的模式（如 useReducer、Context），基于项目实际技术栈给建议
