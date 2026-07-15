# figmaToTaroPage Skill

当使用 figma-mcp 生成页面时自动应用的规则集，处理尺寸转换和主题色适配。

## 📋 功能概述

这是一个**自动应用**的规则集，在使用 Figma 相关工具生成页面时自动生效。

- ✅ **自动尺寸转换（x2 规则）** - 所有尺寸自动乘以 2 以适配项目编译规则
- ✅ **主题色自动适配** - 识别并替换为 TailwindCSS 主题色类名
- ✅ **组件智能映射** - 优先使用项目已有组件
- ✅ **完整类型定义** - 类型文件放在 src/types/pages/ 目录
- ✅ **必备组件检查** - 确保 NavHeader 和 DetailLoginHOC 正确使用

## 🎯 使用场景

**触发时机**：

- 使用 `figma-implement-design` 从 Figma 实现页面
- 使用 `figma-generate-design` 创建设计
- 使用任何 Figma MCP 工具生成代码

**不需要**：

- 用户手动调用此 skill
- 额外的命令或参数

**作用**：

- 在 Figma MCP 生成的代码基础上
- 自动应用项目特定的转换规则

## 🔧 核心规则

### 规则 1: 尺寸 x2

所有 Figma 设计中的尺寸数值需要 **乘以 2**：

| Figma 值 | TailwindCSS      | 说明      |
| -------- | ---------------- | --------- |
| 8px      | `w-[16px]`       | 宽度 x2   |
| 15px     | `px-[30px]`      | 内边距 x2 |
| 12px     | `text-[24px]`    | 字号 x2   |
| 8px      | `rounded-[16px]` | 圆角 x2   |

**原因**：项目设计稿基于 750px 宽度，编译时会自动 2:1 转换（1px = 2rpx）。

### 规则 2: 主题色适配

识别 Figma 中的主题色并替换为 TailwindCSS 主题色类名：

| Figma 颜色      | TailwindCSS                | 说明         |
| --------------- | -------------------------- | ------------ |
| #21b874（绿色） | `bg-primary`               | 微信端主题色 |
| #1890ff（蓝色） | `bg-primary`               | H5 端主题色  |
| #edfef7（浅绿） | `bg-primary bg-opacity-10` | 选中背景     |

**原因**：项目支持多端，不同端使用不同主题色。

### 规则 3: 组件优先

优先使用项目已有组件：

| Figma 元素 | 项目组件        |
| ---------- | --------------- |
| 导航栏     | `<NavHeader>`   |
| 底部按钮   | `<BlockButton>` |
| 弹窗       | `<CustomModal>` |
| 列表       | `<List>`        |

## 📁 生成的页面结构

```typescript
import { FC } from 'react'
import { View, ScrollView } from '@tarojs/components'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'

const PageName: FC = () => {
  useMount(() => {
    // 首次加载逻辑
  })

  return (
    <View className="flex h-screen flex-col bg-white">
      {/* ⭐ 必须：导航栏 */}
      <NavHeader title="页面标题" />

      <ScrollView scrollY className="flex-1">
        {/* ✅ 所有尺寸已 x2 */}
        {/* ✅ 主题色使用 bg-primary */}
        {/* ✅ 使用项目组件 */}
      </ScrollView>
    </View>
  )
}

// ⭐ 必须：登录验证 HOC
export default DetailLoginHOC(PageName)
```

## 📖 文档

- **[SKILL.md](./SKILL.md)** - 完整的规则说明和示例
- **[QUICK_START.md](./QUICK_START.md)** - 快速参考指南
- **[EXAMPLES.md](./EXAMPLES.md)** - 详细使用示例

## ✅ 自动检查清单

应用此规则后，确保：

### 尺寸转换

- [ ] 所有宽高数值 x2
- [ ] 所有 padding/margin 数值 x2
- [ ] 所有字号数值 x2
- [ ] 所有圆角数值 x2

### 主题色

- [ ] 主要按钮使用 `bg-primary`
- [ ] 主要文字使用 `text-primary`
- [ ] 选中状态使用 `bg-primary bg-opacity-10`

### 必备组件

- [ ] 页面包含 `<NavHeader>` 组件
- [ ] 页面使用 `DetailLoginHOC` 包裹
- [ ] 优先使用项目已有组件

### 代码规范

- [ ] 使用 `useMount` 进行首次加载
- [ ] 类型定义在 `src/types/pages/`
- [ ] 不使用 enum，使用字面量联合类型
- [ ] 通过 TypeScript 和 ESLint 检查

## 🔍 转换示例

### 按钮转换

**Figma 设计**：

- 宽度: 343px，高度: 44px，圆角: 8px，背景: #21b874

**❌ 错误**：

```typescript
<View className="w-[343px] h-[44px] rounded-[8px] bg-[#21b874]">
```

**✅ 正确**：

```typescript
<BlockButton onClick={handleClick}>确认</BlockButton>
// 或者
<View className="w-[686px] h-[88px] rounded-[16px] bg-primary">
```

**说明**：343→686 (x2), 44→88 (x2), 8→16 (x2), #21b874→bg-primary

## 🐛 常见问题

### Q: 为什么要 x2？

A: 项目设计稿基于 750px 宽度，编译时 Taro 会自动 2:1 转换。

### Q: 如何判断是否为主题色？

A:

- 绿色系（#01c176, #21b874 等）→ 是主题色
- 蓝色系（#1890ff）→ 是主题色
- 浅绿背景（#edfef7）→ 是主题色浅色
- 黑白灰、红黄等 → 不是主题色

### Q: 这个规则会自动生效吗？

A: 是的，当使用 Figma MCP 工具时自动应用，无需手动调用。

---

**版本**: 1.0.0  
**最后更新**: 2026-04-01
