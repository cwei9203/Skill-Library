---
name: figmaToTaroPage
description: 当使用 figma-mcp 生成页面时自动应用的规则集。处理尺寸转换（x2）和主题色适配。这是一个自动应用的规则，不需要手动调用。
---

# figmaToTaroPage — Figma 转 Taro 页面规则

## 规则说明

这是一个**自动应用**的规则集，当使用 figma-mcp 工具生成页面时，Codex 会自动检查并应用以下转换规则。

### 工作流程

```
1. 用户使用 figma-implement-design 或其他 Figma MCP 工具
   ↓
2. Figma MCP 生成初始代码（使用 Figma 原始尺寸）
   ↓
3. Codex 自动读取此 skill 规则
   ↓
4. Codex 自动修改生成的代码：
   - 所有尺寸 x2
   - 主题色替换为 primary
   - 添加必备组件
   ↓
5. 输出符合项目规范的最终代码
```

### 触发时机

- 使用 `figma-implement-design` 实现设计
- 使用 `figma-generate-design` 生成设计
- 使用任何 Figma MCP 工具生成页面代码

### 不需要

- 用户手动调用此 skill
- 用户手动修改尺寸

## 核心规则

### 规则 1: 尺寸转换（x2 规则）

**原因**：项目设计稿基于 750px 宽度（iPhone 6），编译时会自动按照 2:1 比例转换（1px = 2rpx）。

**规则**：Figma 中的所有尺寸数值需要 **乘以 2** 才能正确对应到 TailwindCSS 类名。

**包括**：宽度、高度、padding、margin、gap、font-size、border-radius、border-width、line-height、letter-spacing、阴影偏移和模糊半径等。

#### 快速转换表

| Figma 值 | TailwindCSS      | 用途       |
| -------- | ---------------- | ---------- |
| 4px      | `[8px]`          | 最小间距   |
| 8px      | `[16px]`         | 小间距     |
| 12px     | `[24px]`         | 标准间距   |
| 15px     | `[30px]`         | 页面内边距 |
| 20px     | `[40px]`         | 大间距     |
| 10px     | `[20px]`         | 最小字号   |
| 12px     | `[24px]`         | 小字号     |
| 14px     | `[28px]`         | 正文字号   |
| 16px     | `[32px]`         | 大字号     |
| 18px     | `[36px]`         | 标题字号   |
| 4px      | `rounded-[8px]`  | 小圆角     |
| 8px      | `rounded-[16px]` | 标准圆角   |
| 12px     | `rounded-[24px]` | 大圆角     |

#### 转换示例

```typescript
// ❌ Figma MCP 直接生成（错误）
<View className="w-[200px] h-[100px] px-[15px] py-[10px] gap-[10px] text-[14px] rounded-[8px]">

// ✅ 应用规则后（正确）- 所有数值 x2
<View className="w-[400px] h-[200px] px-[30px] py-[20px] gap-[20px] text-[28px] rounded-[16px]">
```

**应用方式**：在 figma-mcp 生成代码后，自动将所有尺寸数值乘以 2。

---

### 规则 2: 主题色使用

**原因**：项目支持多端（微信、H5、钉钉），不同端使用不同主题色。使用 TailwindCSS 主题色类名可以自动适配。

**主题色定义**：

- **微信端**: `primary: #21b874`（绿色）
- **H5 端**: `primary: #1890ff`（蓝色）
- **CSS 变量**: `--color-brand: #01c176`（品牌主色）

#### 颜色映射表

**⚠️ 重要规则**：只有以下 4 个颜色值使用主题色类名，其他所有颜色都保持固定色值。

| Figma 颜色       | 判断             | TailwindCSS 类名                                       |
| ---------------- | ---------------- | ------------------------------------------------------ |
| #1890ff          | H5 主题色        | `bg-primary` / `text-primary` / `border-primary`       |
| #21b874          | 微信主题色       | `bg-primary` / `text-primary` / `border-primary`       |
| #e6f7f0          | 主题浅色         | `bg-primary bg-opacity-10`                             |
| #edf6ff          | 主题浅色（蓝）   | `bg-primary bg-opacity-10`                             |
| **其他所有颜色** | **保持固定色值** | `bg-[#颜色值]` / `text-[#颜色值]` / `border-[#颜色值]` |

**示例**：

- `#01c176` → `bg-[#01c176]`（固定色值）
- `#43bf8c` → `bg-[#43bf8c]`（固定色值）
- `#212121` → `text-[#212121]`（固定色值）
- `#ff0000` → `bg-[#ff0000]`（固定色值）
- `rgba(33,184,116,0.4)` → `bg-[rgba(33,184,116,0.4)]`（固定色值）

#### 转换示例

```typescript
// ❌ Figma MCP 直接生成（错误）
<View className="bg-[#21b874] text-white">
  <Text>确认</Text>
</View>

// ✅ 应用规则后（正确）
<View className="bg-primary text-white">
  <Text>确认</Text>
</View>

// ❌ Figma MCP 直接生成（错误）
<View className="bg-[#edfef7]">选中项</View>

// ✅ 应用规则后（正确）
<View className="bg-primary bg-opacity-10">选中项</View>
```

**应用方式**：在 figma-mcp 生成代码后，根据颜色映射表自动替换主题色类名。

---

### 规则 3: 项目组件优先

**原因**：项目已有 97 个通用组件 + 25 个业务组件，经过充分测试和多端适配。

#### 必备组件（所有页面必须使用）

- **`<NavHeader>`** - 自定义导航栏（必须放在页面最顶部）
- **`DetailLoginHOC`** - 登录验证 HOC（必须包裹页面组件）
- **`<SafeArea>`** - 底部安全区域（可选）

#### 高频组件映射

| Figma 元素   | 项目组件                        | 说明            |
| ------------ | ------------------------------- | --------------- |
| 底部固定按钮 | `<BlockButton>`                 | 底部 fixed 按钮 |
| 弹窗         | `<CustomModal>` 或 `<ModalApi>` | 弹窗组件        |
| 底部弹出层   | `<CustomBottomPopup>`           | 底部弹出        |
| 操作菜单     | `<ActionSheetApi>`              | 操作菜单        |
| 加载状态     | `<Loading>`                     | 加载动画        |
| 空状态       | `<CommonEmpty>`                 | 空页面          |
| 图片预览     | `<PreviewImage>`                | 图片预览        |
| 列表         | `<List>`                        | 列表组件        |

#### 组件选择优先级

1. 项目已有组件（`src/components/`, `src/components-pro/`）
2. `@tarojs/components` 基础组件（View, Text, Image, ScrollView）
3. Taroify 组件（小程序端推荐）
4. Ant Design Mobile 组件（H5 端推荐）

---

### 规则 4: 图标规范

**原因**：项目有统一的 iconfont 字体库（169 个图标），使用 iconfont 比内联 SVG 更轻量、更灵活。

**规则**：

- ⭐ **优先使用项目现有的 iconfont**
- 格式：`<View className="icon {图标类名} text-[尺寸] text-[颜色]" />`
- 如果没有对应的图标，使用 `ic_help` 作为占位符

**常用图标映射**：

| 功能      | 图标类名         | 示例                                                                  |
| --------- | ---------------- | --------------------------------------------------------------------- |
| 添加      | `ic_add`         | `<View className="icon ic_add text-[32px] text-[#01c176]" />`         |
| 删除      | `ic_delete_tool` | `<View className="icon ic_delete_tool text-[32px] text-[#ff0000]" />` |
| 编辑      | `bianji`         | `<View className="icon bianji text-[28px] text-[#212121]" />`         |
| 搜索      | `ic_search`      | `<View className="icon ic_search text-[28px] text-[#999]" />`         |
| 返回      | `ic_back`        | `<View className="icon ic_back text-[32px] text-[#212121]" />`        |
| 下拉      | `xiala`          | `<View className="icon xiala text-[24px] text-[#999]" />`             |
| 选中      | `ic_selected`    | `<View className="icon ic_selected text-[24px] text-white" />`        |
| 帮助/占位 | `ic_help`        | `<View className="icon ic_help text-[24px] text-[#999]" />`           |

**应用方式**：

- 将 Figma 中的图标 SVG 替换为对应的 iconfont 类名
- 如果找不到完全匹配的图标，选择语义相近的图标
- 实在没有合适的图标时，使用 `ic_help` 占位

---

### 规则 5: 样式规范

**原因**：Tailwind CSS 的 border 相关类名只设置 border-width 和 border-color，不会自动设置 border-style，导致边框不显示。

**规则**：

- ⚠️ **使用 border 相关类名时，必须明确添加 `border-solid`**
- 只设置 border-width 和 border-color 不会显示边框
- 这是 Tailwind CSS 的默认行为，所有端（H5、小程序）都需要遵守

#### 转换示例

```typescript
// ❌ Figma MCP 直接生成（错误）- 边框不会显示
<View className="border-[2px] border-[#eaf5f1]">内容</View>

// ✅ 应用规则后（正确）- 必须添加 border-solid
<View className="border-[2px] border-solid border-[#eaf5f1]">内容</View>

// ❌ 错误：使用默认 border
<View className="border border-[#e5e5e5]">内容</View>

// ✅ 正确：使用默认 border + border-solid
<View className="border border-solid border-[#e5e5e5]">内容</View>

// ❌ 错误：只设置某一边的边框
<View className="border-b-[2px] border-b-[#f0f0f0]">内容</View>

// ✅ 正确：只设置某一边的边框 + border-solid
<View className="border-b-[2px] border-solid border-b-[#f0f0f0]">内容</View>
```

**应用方式**：在 figma-mcp 生成代码后，自动检查所有 border 相关类名，确保包含 `border-solid`。

---

## 自动转换流程

```
1. Figma MCP 获取设计数据
   ↓
2. 应用尺寸 x2 转换
   - 所有数值 × 2
   ↓
3. 应用主题色替换
   - 识别并替换主题色
   ↓
4. 应用图标转换
   - SVG 图标 → iconfont 类名
   - 无匹配图标 → ic_help 占位
   ↓
5. 应用样式规范检查
   - 所有 border 类名添加 border-solid
   ↓
6. 应用组件映射
   - 使用项目组件
   ↓
7. 生成符合规范的代码
   - 添加 NavHeader 和 DetailLoginHOC
   - 类型定义放在 src/types/pages/
   ↓
8. 使用 createNewPage 创建文件
```

---

## 生成的页面结构

**页面文件**（`index.tsx`）：

```typescript
import { FC } from 'react'
import { View, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMount, useDebounceFn } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import SafeArea from '@/components/SafeArea'
import usePageLog from '@/hooks/useLog'
import styles from './index.module.scss'

const PageName: FC = () => {
  // 埋点 Hook（页面级初始化，action 埋点待开发者按需补充）
  usePageLog('PageName', {
    type: 'page',
    external_source: Taro.getApp()?.globalData?.external_source
  })

  const loadInitialData = () => {
    // TODO: 加载数据
  }

  // ⭐ 首次加载（必须放在 useMount）
  useMount(() => {
    loadInitialData()
  })

  // 事件处理（关键按钮必须使用 useDebounceFn 防抖）
  const { run: handleClick } = useDebounceFn(
    () => {
      // TODO: 处理逻辑（action 埋点待开发者按需补充）
    },
    { wait: 500, leading: true, trailing: false }
  )

  return (
    <View className="flex h-screen flex-col bg-white">
      {/* ⭐ 必须：导航栏 */}
      <NavHeader title="页面标题" />

      {/* ⭐ ScrollView 配合 CSS 隐藏滚动条 */}
      <ScrollView scrollY className={`flex-1 ${styles.pageScroll}`}>
        {/* ✅ Figma 设计转换后的内容 */}
        {/* ✅ 所有尺寸已 x2 */}
        {/* ✅ 主题色使用 bg-primary, text-primary */}
        {/* ✅ 使用项目组件 */}
      </ScrollView>

      <SafeArea position="bottom" />
    </View>
  )
}

// ⭐ 必须：登录验证 HOC
export default DetailLoginHOC(PageName)
```

**样式文件**（`index.module.scss`）：

```scss
// ⭐ 移动端隐藏滚动条（所有 Taro 页面必须）
.pageScroll {
  &::-webkit-scrollbar {
    display: none;
  }
}

// 其他复杂样式（渐变、动画等）
```

---

## 快速检查清单

### ✅ 尺寸转换（必须 x2）

- [ ] 宽度/高度：`w-[]`, `h-[]`
- [ ] 内边距：`p-[]`, `px-[]`, `py-[]`, `pt-[]`, `pr-[]`, `pb-[]`, `pl-[]`
- [ ] 外边距：`m-[]`, `mx-[]`, `my-[]`, `mt-[]`, `mr-[]`, `mb-[]`, `ml-[]`
- [ ] 间距：`gap-[]`, `gap-x-[]`, `gap-y-[]`
- [ ] 字号：`text-[]`
- [ ] 圆角：`rounded-[]`, `rounded-t-[]`, `rounded-b-[]`, `rounded-l-[]`, `rounded-r-[]`
- [ ] 边框：`border-[]`, `border-t-[]`, `border-b-[]`, `border-l-[]`, `border-r-[]`

### ✅ 主题色转换（必须使用 primary）

- [ ] 按钮背景：`bg-primary`（不是 `bg-[#21b874]`）
- [ ] 主要文字：`text-primary`（不是 `text-[#21b874]`）
- [ ] 边框颜色：`border-primary`（不是 `border-[#21b874]`）
- [ ] 选中状态：`bg-primary bg-opacity-10`（不是 `bg-[#edfef7]`）

### ✅ 必备组件

- [ ] `<NavHeader>` - 导航栏（必须在页面最顶部）
- [ ] `DetailLoginHOC` - 登录验证包裹（必须导出时使用）
- [ ] 优先使用项目组件（`<BlockButton>`, `<CustomModal>` 等）

### ✅ 代码规范

- [ ] 使用 `useMount` 进行首次加载
- [ ] 类型定义在 `src/types/pages/PageName.ts`
- [ ] 不使用 enum，使用字面量联合类型
- [ ] 所有变量都有类型定义（无 any）
- [ ] 优先使用 TailwindCSS，复杂样式使用 CSS Modules

### ✅ 样式规范

- [ ] ScrollView 添加样式类（`styles.pageScroll`）
- [ ] 样式文件中添加隐藏滚动条（`::-webkit-scrollbar { display: none }`）

### ✅ 交互规范

- [ ] 关键按钮点击使用 `useDebounceFn` 防抖（wait: 500, leading: true, trailing: false）
- [ ] 可以引入 `usePageLog`，但默认不实现 action 埋点
- [ ] `useDidShow` 可选，默认不提供（待开发者按需补充）

---

## 实际示例

### 示例 1：按钮转换

**Figma 设计**：

- 宽度: 343px
- 高度: 44px
- 圆角: 8px
- 背景: #21b874
- 文字: 白色，16px

**❌ 错误转换**：

```typescript
<View className="w-[343px] h-[44px] rounded-[8px] bg-[#21b874]">
  <Text className="text-white text-[16px]">确认</Text>
</View>
```

**✅ 正确转换**：

```typescript
// 方案 1：使用项目组件（推荐）
<BlockButton onClick={handleClick}>确认</BlockButton>

// 方案 2：使用 TailwindCSS（尺寸 x2 + 主题色）
<View className="w-[686px] h-[88px] rounded-[16px] bg-primary flex items-center justify-center">
  <Text className="text-white text-[32px]">确认</Text>
</View>
```

**转换说明**：

- 343px → 686px (x2)
- 44px → 88px (x2)
- 8px → 16px (x2)
- 16px → 32px (x2)
- #21b874 → `bg-primary`

---

### 示例 2：卡片列表转换

**Figma 设计**：

- 卡片间距: 12px
- 卡片内边距: 15px
- 卡片圆角: 8px
- 标题字号: 16px
- 副标题字号: 14px
- 选中背景: #e6f7f0

**✅ 正确转换**：

```typescript
<View className="flex flex-col gap-[24px]">
  {list.map(item => (
    <View
      key={item.id}
      className={clsx(
        'p-[30px] rounded-[16px]',
        item.selected ? 'bg-primary bg-opacity-10' : 'bg-white'
      )}
    >
      <Text className="text-[32px] text-[#212121]">{item.title}</Text>
      <Text className="mt-[24px] text-[28px] text-[#666]">{item.subtitle}</Text>
    </View>
  ))}
</View>
```

**转换说明**：

- gap: 12px → 24px
- padding: 15px → 30px
- rounded: 8px → 16px
- title: 16px → 32px
- subtitle: 14px → 28px
- 选中背景: #e6f7f0 → `bg-primary bg-opacity-10`

---

## 常见问题

### Q: 为什么要 x2？

A: 项目设计稿基于 750px 宽度（iPhone 6），编译时 Taro 会自动按照 2:1 比例转换单位（1px = 2rpx）。

### Q: 如何判断是否为主题色？

A: **只有以下 4 个颜色值使用主题色类名**：

- `#1890ff` → 是主题色
- `#21b874` → 是主题色
- `#e6f7f0` → 是主题色浅色
- `#edf6ff` → 是主题色浅色（蓝）

**其他所有颜色都保持固定色值**，包括：

- `#01c176`, `#43bf8c` 等绿色系 → 固定色值 `bg-[#01c176]`
- 黑白灰色系 → 固定色值 `text-[#212121]`
- 红黄等功能色 → 固定色值 `bg-[#ff0000]`

### Q: Figma 1px 边框如何处理？

A:

- 写成 `border-[2px]`（严格 x2）

### Q: 如何验证转换是否正确？

A:

1. 对比 Figma 截图和实际渲染
2. 检查所有尺寸是否是 Figma 的 2 倍
3. 检查主题色是否使用了 `primary` 类名
4. 在微信和 H5 环境分别测试

---

## 相关文档

- [figma-implement-design](../figma:figma-implement-design/SKILL.md) - Figma 实现设计的基础 skill
- [createNewPage](../createNewPage/SKILL.md) - 创建新页面的 skill
- [项目 AGENTS.md](/Users/youbao_feng/workspace/react-taro-teacher/AGENTS.md) - 项目完整规范
- [迁移规则 MIGRATION_RULES.md](/Users/youbao_feng/workspace/MIGRATION_RULES.md) - 迁移规则和最佳实践

---

## 更新日志

### 2026-04-01 - v1.0.0

- ✅ 初始版本发布
- ✅ 支持 Figma 设计到 Taro 页面的自动转换
- ✅ 实现尺寸 x2 自动转换规则
- ✅ 实现主题色自动适配规则
- ✅ 作为自动应用的规则集（不需要手动调用）
