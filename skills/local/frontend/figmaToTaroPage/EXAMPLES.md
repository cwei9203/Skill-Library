# figmaToTaroPage Skill 使用示例

本文档展示在使用 Figma MCP 工具时，如何自动应用转换规则。

## 规则概述

当使用 Figma MCP 工具（如 figma-implement-design）时，会自动应用以下规则：

1. **尺寸 x2** - 所有数值乘以 2
2. **主题色适配** - 替换为 `primary` 类名
3. **组件优先** - 使用项目已有组件

---

## 示例 1：简单按钮页面

### Figma 设计

```
页面尺寸: 375px × 667px
导航栏高度: 44px
按钮宽度: 343px
按钮高度: 44px
按钮圆角: 8px
按钮背景: #21b874（绿色）
按钮文字: 白色，16px，"确认"
页面内边距: 15px
```

### 自动转换后的代码

```typescript
import { FC } from 'react'
import { View } from '@tarojs/components'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import BlockButton from '@/components/BlockButton'

const ConfirmPage: FC = () => {
  useMount(() => {
    // 首次加载逻辑
  })

  const handleConfirm = () => {
    // 确认逻辑
  }

  return (
    <View className="flex h-screen flex-col bg-white">
      {/* ⭐ 必须：导航栏 */}
      <NavHeader title="确认页面" />

      {/* 页面内容：内边距 15px → 30px */}
      <View className="flex-1 px-[30px] py-[30px]">
        {/* ✅ 使用项目组件：BlockButton */}
        <BlockButton onClick={handleConfirm}>确认</BlockButton>
      </View>
    </View>
  )
}

// ⭐ 必须：登录验证 HOC
export default DetailLoginHOC(ConfirmPage)
```

### 转换说明

- ✅ 内边距：15px → 30px (x2)
- ✅ 按钮：使用 `<BlockButton>` 项目组件（自动处理尺寸和主题色）
- ✅ 导航栏：使用 `<NavHeader>` 必备组件
- ✅ HOC：使用 `DetailLoginHOC` 包裹

---

## 示例 2：卡片列表页面

### Figma 设计

```
卡片间距: 12px
卡片内边距: 15px
卡片圆角: 8px
卡片阴影: 0 2px 8px rgba(0,0,0,0.1)
标题字号: 16px
副标题字号: 14px
标签高度: 24px
标签圆角: 4px
标签背景: #edfef7（浅绿）
选中边框: #21b874，2px
```

### 自动转换后的代码

```typescript
import { FC, useState } from 'react'
import { View, ScrollView, Text } from '@tarojs/components'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import clsx from 'clsx'

interface CardItem {
  id: string
  title: string
  subtitle: string
  tags: string[]
  selected: boolean
}

const CardListPage: FC = () => {
  const [list, setList] = useState<CardItem[]>([])

  useMount(() => {
    loadList()
  })

  const loadList = async () => {
    // 加载列表数据
  }

  return (
    <View className="flex h-screen flex-col bg-[#f5f5f5]">
      <NavHeader title="卡片列表" />

      <ScrollView scrollY className="flex-1">
        {/* 列表容器：间距 12px → 24px，内边距 15px → 30px */}
        <View className="flex flex-col gap-[24px] p-[30px]">
          {list.map(item => (
            <View
              key={item.id}
              className={clsx(
                // 卡片：内边距 15px → 30px，圆角 8px → 16px
                'rounded-[16px] bg-white p-[30px] shadow-md',
                // 选中边框：2px → 4px，颜色使用 primary
                item.selected && 'border-[4px] border-primary'
              )}
            >
              {/* 标题：16px → 32px */}
              <Text className="text-[32px] font-medium text-[#212121]">
                {item.title}
              </Text>

              {/* 副标题：14px → 28px，间距 12px → 24px */}
              <Text className="mt-[24px] text-[28px] text-[#666]">
                {item.subtitle}
              </Text>

              {/* 标签列表：间距 8px → 16px */}
              <View className="mt-[24px] flex flex-row flex-wrap gap-[16px]">
                {item.tags.map((tag, index) => (
                  <View
                    key={index}
                    // 标签：高度 24px → 48px，圆角 4px → 8px
                    // 背景：#edfef7 → bg-primary bg-opacity-10
                    className="h-[48px] rounded-[8px] bg-primary bg-opacity-10 px-[20px] flex items-center justify-center"
                  >
                    <Text className="text-[24px] text-primary">
                      {tag}
                    </Text>
                  </View>
                ))}
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  )
}

export default DetailLoginHOC(CardListPage)
```

### 转换说明

- ✅ 卡片间距：12px → 24px
- ✅ 卡片内边距：15px → 30px
- ✅ 卡片圆角：8px → 16px
- ✅ 标题字号：16px → 32px
- ✅ 副标题字号：14px → 28px
- ✅ 标签高度：24px → 48px
- ✅ 标签圆角：4px → 8px
- ✅ 标签背景：#edfef7 → `bg-primary bg-opacity-10`
- ✅ 选中边框：#21b874 → `border-primary`，2px → 4px

---

## 示例 3：表单页面

### Figma 设计

```
输入框高度: 48px
输入框圆角: 8px
输入框内边距: 15px
输入框边框: 1px, #e0e0e0
标签字号: 14px
输入文字字号: 16px
表单项间距: 20px
提交按钮高度: 48px
提交按钮背景: #21b874
```

### 自动转换后的代码

```typescript
import { FC, useState } from 'react'
import { View, Text, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import BlockButton from '@/components/BlockButton'

const FormPage: FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  })

  useMount(() => {
    // 初始化逻辑
  })

  const handleSubmit = async () => {
    try {
      await submitForm(formData)
      Taro.showToast({ title: '提交成功', icon: 'success' })
    } catch (error) {
      Taro.showToast({ title: '提交失败', icon: 'none' })
    }
  }

  return (
    <View className="flex h-screen flex-col bg-white">
      <NavHeader title="填写信息" />

      {/* 表单区域：内边距 15px → 30px */}
      <View className="flex-1 p-[30px]">
        {/* 表单项容器：间距 20px → 40px */}
        <View className="flex flex-col gap-[40px]">
          {/* 表单项 */}
          <View>
            {/* 标签：14px → 28px */}
            <Text className="mb-[16px] text-[28px] text-[#212121]">
              姓名
            </Text>
            {/* 输入框：高度 48px → 96px，圆角 8px → 16px，内边距 15px → 30px */}
            <Input
              className="h-[96px] rounded-[16px] border border-[#e0e0e0] px-[30px] text-[32px]"
              placeholder="请输入姓名"
              value={formData.name}
              onInput={(e) => setFormData({ ...formData, name: e.detail.value })}
            />
          </View>

          <View>
            <Text className="mb-[16px] text-[28px] text-[#212121]">
              邮箱
            </Text>
            <Input
              className="h-[96px] rounded-[16px] border border-[#e0e0e0] px-[30px] text-[32px]"
              placeholder="请输入邮箱"
              type="email"
              value={formData.email}
              onInput={(e) => setFormData({ ...formData, email: e.detail.value })}
            />
          </View>

          <View>
            <Text className="mb-[16px] text-[28px] text-[#212121]">
              手机号
            </Text>
            <Input
              className="h-[96px] rounded-[16px] border border-[#e0e0e0] px-[30px] text-[32px]"
              placeholder="请输入手机号"
              type="number"
              value={formData.phone}
              onInput={(e) => setFormData({ ...formData, phone: e.detail.value })}
            />
          </View>
        </View>
      </View>

      {/* 提交按钮：使用 BlockButton 组件（自动处理主题色和尺寸） */}
      <View className="px-[30px] pb-[30px]">
        <BlockButton onClick={handleSubmit} >提交</BlockButton>
      </View>
    </View>
  )
}

export default DetailLoginHOC(FormPage)
```

### 转换说明

- ✅ 输入框高度：48px → 96px
- ✅ 输入框圆角：8px → 16px
- ✅ 输入框内边距：15px → 30px
- ✅ 标签字号：14px → 28px
- ✅ 输入文字：16px → 32px
- ✅ 表单项间距：20px → 40px
- ✅ 提交按钮：使用 `<BlockButton>` 组件（自动处理主题色）

---

## 示例 4：复杂样式（渐变和阴影）

### Figma 设计

```
头部背景: 线性渐变 #21b874 → #01c176
头部高度: 200px
卡片阴影: 0 4px 12px rgba(0,0,0,0.15)
按钮阴影: 0 2px 8px rgba(33,184,116,0.3)
```

### 自动转换后的代码

```typescript
// index.tsx
import { FC } from 'react'
import { View, Text } from '@tarojs/components'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import styles from './index.module.scss'

const GradientPage: FC = () => {
  useMount(() => {
    // 初始化
  })

  return (
    <View className="flex h-screen flex-col">
      <NavHeader title="渐变页面" />

      {/* 头部：高度 200px → 400px，使用 CSS Modules 实现渐变 */}
      <View className={`${styles.headerGradient} px-[30px] py-[60px]`}>
        <Text className="text-[40px] font-bold text-white">
          欢迎使用
        </Text>
      </View>

      {/* 内容区域 */}
      <View className="flex-1 p-[30px]">
        {/* 带阴影的卡片：使用 CSS Modules */}
        <View className={`${styles.shadowCard} rounded-[24px] bg-white p-[30px]`}>
          <Text className="text-[32px] font-medium">
            卡片标题
          </Text>
        </View>

        {/* 带阴影的按钮 */}
        <View className={`${styles.shadowButton} mt-[40px]`}>
          <View className="h-[96px] rounded-[16px] bg-primary flex items-center justify-center">
            <Text className="text-white text-[32px]">
              立即体验
            </Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default DetailLoginHOC(GradientPage)
```

```scss
// index.module.scss
@import '@/css/custom-variables-weapp.scss';

// 头部渐变：使用 CSS 变量（主题色）
.headerGradient {
  background: linear-gradient(
    135deg,
    var(--color-brand) 0%,
    // #01c176
    var(--color-brand-light) 100% // #43bf8c
  );
}

// 卡片阴影：数值 x2（0 4px 12px → 0 8px 24px）
.shadowCard {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

// 按钮阴影：数值 x2，使用 CSS 变量
.shadowButton {
  box-shadow: 0 4px 16px var(--color-brand-select);
  // Figma: 0 2px 8px rgba(33,184,116,0.3) → x2 → 0 4px 16px
}
```

### 转换说明

- ✅ 头部高度：200px → 400px
- ✅ 渐变：使用 CSS 变量（`var(--color-brand)`）而非固定色值
- ✅ 卡片阴影：0 4px 12px → 0 8px 24px (x2)
- ✅ 按钮阴影：0 2px 8px → 0 4px 16px (x2)
- ✅ 按钮背景：使用 `bg-primary` 而非 #21b874

---

## 最佳实践

### 1. 尺寸转换速查

**间距**：4px→8px, 8px→16px, 12px→24px, 15px→30px, 20px→40px

**字号**：10px→20px, 12px→24px, 14px→28px, 16px→32px, 18px→36px

**圆角**：4px→8px, 8px→16px, 12px→24px

### 2. 主题色判断

- 绿色系（#01c176, #21b874, #43bf8c）→ `primary`
- 蓝色系（#1890ff）→ `primary`
- 浅绿背景（#edfef7, #e6f7f0）→ `bg-primary bg-opacity-10`
- 其他颜色 → 保持固定色值

### 3. 组件选择

1. 检查项目组件库（优先）
2. 使用 @tarojs/components 基础组件
3. 小程序端使用 Taroify
4. H5 端使用 Ant Design Mobile

---

## 故障排除

### 问题 1：尺寸看起来不对

**原因**：未正确应用 x2 规则

**解决**：检查所有尺寸数值是否 x2

### 问题 2：主题色在不同端不一致

**原因**：使用了固定色值

**解决**：搜索 `bg-[#21b874]` 替换为 `bg-primary`

### 问题 3：复杂样式无法实现

**原因**：TailwindCSS 无法实现

**解决**：使用 CSS Modules，尺寸依然 x2

---

## 总结

使用 Figma MCP 工具时，会自动应用：

1. **尺寸 x2** - 所有数值 × 2
2. **主题色适配** - 使用 `primary` 类名
3. **组件优先** - 使用项目组件

遵循这些规则，可以快速生成高质量、符合项目规范的页面代码。
