# figmaToTaroPage Skill - 快速参考

> 当使用 figma-mcp 生成页面时自动应用的规则

## 🎯 使用场景

这是一个**自动应用**的规则集，不需要手动调用。

**触发时机**：

- 使用 `figma-implement-design` 实现 Figma 设计
- 使用 `figma-generate-design` 生成设计
- 使用任何 Figma MCP 工具

**作用**：

- 自动将 Figma 尺寸 x2
- 自动替换主题色
- 自动添加必备组件

## 📝 三个核心规则

### 1️⃣ 尺寸 x2

**规则**：Figma 中的所有尺寸数值 × 2。

**为什么**：项目设计稿基于 750px，编译时自动 2:1 转换（1px = 2rpx）。

**速查表**：

| Figma | TailwindCSS      | 说明        |
| ----- | ---------------- | ----------- |
| 8px   | `[16px]`         | 小间距 x2   |
| 15px  | `[30px]`         | 标准间距 x2 |
| 12px  | `[24px]`         | 小字号 x2   |
| 14px  | `[28px]`         | 正文字号 x2 |
| 16px  | `[32px]`         | 大字号 x2   |
| 8px   | `rounded-[16px]` | 圆角 x2     |

**实际代码**：

```typescript
// ❌ 错误：直接使用 Figma 数值
<View className="w-[200px] px-[15px] text-[14px] rounded-[8px]">

// ✅ 正确：所有数值 x2
<View className="w-[400px] px-[30px] text-[28px] rounded-[16px]">
```

---

### 2️⃣ 主题色适配

**规则**：主题色使用 TailwindCSS 类名，不用固定色值。

**为什么**：项目支持多端，微信用绿色，H5 用蓝色。

**速查表**：

| Figma 颜色      | TailwindCSS                | 说明       |
| --------------- | -------------------------- | ---------- |
| #21b874（绿）   | `bg-primary`               | 微信主题色 |
| #1890ff（蓝）   | `bg-primary`               | H5 主题色  |
| #edfef7（浅绿） | `bg-primary bg-opacity-10` | 选中背景   |
| 黑白灰          | `bg-[#xxx]`                | 固定色值   |

**实际代码**：

```typescript
// ❌ 错误：硬编码颜色
<View className="bg-[#21b874] text-white">确认</View>

// ✅ 正确：使用主题色类名
<View className="bg-primary text-white">确认</View>
```

---

### 3️⃣ 组件优先

**规则**：优先使用项目已有组件。

**常用组件映射**：

| Figma 元素 | 项目组件                     |
| ---------- | ---------------------------- |
| 导航栏     | `<NavHeader title="标题" />` |
| 底部按钮   | `<BlockButton />`            |
| 列表       | `<List>`                     |
| 空状态     | `<CommonEmpty>`              |

**必备组件**（所有页面必须）：

```typescript
// ⭐ 必须：导航栏
<NavHeader title="页面标题" />

// ⭐ 必须：登录验证 HOC
export default DetailLoginHOC(PageName)
```

---

## 🔍 快速验证

生成页面后，检查：

```bash
✅ 尺寸数值是 Figma 的 2 倍
✅ 主题色使用了 primary 类名
✅ 包含 <NavHeader> 组件
✅ 使用 DetailLoginHOC 包裹
✅ 类型文件在 src/types/pages/
✅ 无 TypeScript 错误
```

---

## 📋 转换示例

### 示例 1：按钮转换

**Figma 设计**：

```
宽度: 343px
高度: 44px
圆角: 8px
背景: #21b874
文字: 白色，16px
```

**✅ 正确转换**：

```typescript
// 方案 1：使用项目组件（推荐）
<BlockButton onClick={handleClick}>确认</BlockButton>

// 方案 2：使用 TailwindCSS
<View className="w-[686px] h-[88px] rounded-[16px] bg-primary">
  <Text className="text-white text-[32px]">确认</Text>
</View>
```

**转换说明**：

- 343px → 686px (**x2**)
- 44px → 88px (**x2**)
- 8px → 16px (**x2**)
- 16px → 32px (**x2**)
- #21b874 → **bg-primary**

---

### 示例 2：卡片转换

**Figma 设计**：

```
卡片间距: 12px
卡片内边距: 15px
卡片圆角: 8px
标题: 16px
副标题: 14px
选中背景: #edfef7
```

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
      <Text className="text-[32px]">{item.title}</Text>
      <Text className="mt-[24px] text-[28px]">{item.subtitle}</Text>
    </View>
  ))}
</View>
```

**转换说明**：

- gap: 12px → 24px (**x2**)
- padding: 15px → 30px (**x2**)
- rounded: 8px → 16px (**x2**)
- title: 16px → 32px (**x2**)
- subtitle: 14px → 28px (**x2**)
- 选中背景: #edfef7 → **bg-primary bg-opacity-10**

---

## 🚨 常见错误

### 错误 1：忘记 x2

```typescript
// ❌ 错误
<View className="px-[15px] text-[14px]">

// ✅ 正确
<View className="px-[30px] text-[28px]">
```

### 错误 2：硬编码主题色

```typescript
// ❌ 错误
<View className="bg-[#21b874]">

// ✅ 正确
<View className="bg-primary">
```

### 错误 3：重新实现组件

```typescript
// ❌ 错误：重新实现按钮
<View className="..." onClick={...}>
  <Text>确认</Text>
</View>

// ✅ 正确：使用项目组件
<BlockButton onClick={...}>确认</BlockButton>
```

---

## 📞 常见问题

**Q: 为什么要 x2？**

A: 项目设计稿基于 750px 宽度，编译时 Taro 自动 2:1 转换。

**Q: 如何判断颜色是否为主题色？**

A:

- 绿色系（#01c176, #21b874 等）→ 是主题色
- 蓝色系（#1890ff）→ 是主题色
- 浅绿背景（#edfef7）→ 是主题色浅色
- 黑白灰、红黄等 → 不是主题色

**Q: 这个规则会自动生效吗？**

A: 是的，使用 Figma MCP 工具时自动应用，无需手动调用。

**Q: 可以不用项目组件吗？**

A: 不推荐。项目组件已充分测试并处理了多端兼容性。

---

## 📚 查看完整文档

- **[SKILL.md](./SKILL.md)** - 完整规则说明
- **[EXAMPLES.md](./EXAMPLES.md)** - 详细使用示例
- **[README.md](./README.md)** - 功能概览

---

**版本**: 1.0.0  
**最后更新**: 2026-04-01
