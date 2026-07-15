---
name: createNewPage
description: 为 react-taro-teacher 项目创建新页面，遵循项目标准规范。支持创建普通页面和模块页面。用法：/createNewPage <页面名称> [模块名称]。例如：/createNewPage UserProfilePage 或 /createNewPage TaskDetailPage wordMemoryModule
---

# createNewPage — 创建标准化新页面

为 react-taro-teacher 项目创建符合规范的新页面，自动生成页面文件、类型定义、样式文件和配置路由。

## Skill 参数

此 skill 接受 1-2 个参数：`/createNewPage <页面名称> [模块名称]`

- **页面名称**（必需）：页面组件名称，使用 PascalCase，例如 `UserProfilePage`、`TaskDetailPage`
- **模块名称**（可选）：blended 模块名称，例如 `wordMemoryModule`、`growthRecordModule`

### 参数示例

```bash
# 创建普通页面（在 pages 目录下）
/createNewPage UserProfilePage

# 创建模块页面（在 pages 目录下，并配置到指定模块）
/createNewPage TaskDetailPage wordMemoryModule

# 创建新模块的页面（会自动创建模块配置）
/createNewPage HomePage myNewModule
```

## 工作流程

### 场景 1：创建普通页面（仅提供页面名称）

#### Step 1: 验证参数

1. 验证页面名称格式（PascalCase）
2. 检查页面是否已存在（检查 `src/pages/{PageName}` 目录）
3. 如果页面已存在，提示用户并停止

#### Step 2: 创建页面文件

在 `src/pages/{PageName}/` 目录下创建以下文件：

1. **index.tsx** - 页面主文件
2. **index.config.ts** - 页面配置文件（必须）
3. **index.module.scss** - CSS Modules 样式文件
4. **components/** - 页面级组件目录（用于存放页面专用的子组件）
5. **README.md** - 页面说明文档

#### Step 3: 创建类型定义文件

在 `src/types/pages/` 目录下创建 `{PageName}.ts` 文件

#### Step 4: 配置路由

更新 `src/app.config.ts`，在 `pages` 数组中添加新页面路径：

```typescript
pages.push('pages/{PageName}/index')
```

#### Step 5: 反馈结果

告知用户：

- 页面文件已创建
- 类型定义已创建
- 路由已配置
- 提供页面访问路径

---

### 场景 2：创建模块页面（提供页面名称和模块名称）

#### Step 1: 验证参数

1. 验证页面名称格式（PascalCase）
2. 验证模块名称格式（camelCase，必须以 `Module` 结尾）
3. 检查页面是否已存在

#### Step 2: 检查模块是否存在

读取 `src/modulePagesConfig.ts` 文件，检查模块配置：

- 检查是否存在 `{moduleName}Name` 常量
- 检查是否存在 `{moduleName}Pages` 数组

#### Step 3a: 模块不存在 - 创建新模块

如果模块不存在，执行以下步骤：

1. **创建环境配置文件**：

   - `.env.development_blended_{moduleName}`
   - `.env.production_blended_{moduleName}`

   内容示例：

   ```env
   # 开发环境
   TARO_APP_OUTPUT={moduleName}

   # 生产环境
   TARO_APP_OUTPUT={moduleName}
   ```

2. **更新 modulePagesConfig.ts**：
   添加模块配置：

   ```typescript
   // {模块描述}分包名
   export const {moduleName}Name = '{moduleName}'

   // {模块描述}分包相关页面
   export const {moduleName}Pages = [
     'pages/{PageName}/index'
   ]
   ```

3. **更新 app.config.ts**：
   添加模块导入和配置：

   ```typescript
   import {
     {moduleName}Name,
     {moduleName}Pages,
     // ... 其他导入
   } from './modulePagesConfig'
   ```

4. **更新 package.json**：
   添加 npm scripts：
   ```json
   {
     "dev_blended:{moduleName}": "...",
     "build_blended:{moduleName}": "..."
   }
   ```

#### Step 3b: 模块存在 - 更新模块配置

如果模块已存在，只需要在 `{moduleName}Pages` 数组中添加新页面路径。

#### Step 4: 创建页面文件

与场景 1 相同，创建页面文件、类型定义和样式文件。

#### Step 5: 反馈结果

告知用户：

- 模块状态（新创建 / 已存在）
- 页面文件已创建
- 模块配置已更新
- 环境配置已创建（如果是新模块）
- 提供开发命令

---

## 页面模板

### 页面主文件（index.tsx）

⚠️ **组件化原则**：

- 页面主文件应保持简洁，主要负责数据获取、状态管理和整体布局
- 将独立的功能模块拆分为子组件，放在 `components/` 目录下
- 子组件命名使用 PascalCase，例如 `HeaderSection.tsx`、`ContentCard.tsx`

```typescript
import { FC, useState } from 'react'
import { View, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'
import SafeArea from '@/components/SafeArea'
import usePageLog from '@/hooks/useLog'
import { useParams } from '@/hooks/useParams'
import type { {PageName}Params } from '@/types/pages/{PageName}'
// ⭐ 引入页面级子组件
import HeaderSection from './components/HeaderSection'
import ContentCard from './components/ContentCard'
import BottomBar from './components/BottomBar'
import styles from './index.module.scss'

const {PageName}: FC = () => {
  // 1. 状态定义
  const params = useParams() as {PageName}Params
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState([])

  // 埋点 Hook（页面级初始化，action 埋点待开发者按需补充）
  usePageLog('{PageName}', {
    type: 'page',
    external_source: Taro.getApp()?.globalData?.external_source
  })

  // 3. 数据加载函数
  const loadData = async () => {
    setLoading(true)
    try {
      // TODO: 加载数据
      // const result = await fetchData()
      // setData(result)
    } catch (error) {
      console.error('加载数据失败:', error)
      Taro.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  // 4. ⭐ 首次加载（必须放在 useMount）
  useMount(() => {
    loadData()
  })

  // 5. 事件处理函数
  const handleAction = () => {
    // TODO: 处理事件
  }

  // 6. 渲染（使用子组件保持页面结构清晰）
  return (
    <View className="flex h-screen flex-col bg-white">
      {/* ⭐ NavHeader 必须放在最顶部 */}
      <NavHeader
        title="{页面标题}"
        customNavStyle={{ backgroundColor: '#fff' }}
        customBackIconStyle={{ color: '#212121' }}
        customTitleStyle={{ color: '#212121' }}
      />

      {/* ⭐ ScrollView 配合 CSS 隐藏滚动条 */}
      <ScrollView scrollY className={`flex-1 ${styles.pageScroll}`}>
        {/* ⭐ 使用页面级子组件组织页面结构 */}
        <HeaderSection onAction={handleAction} />

        {data.map(item => (
          <ContentCard key={item.id} data={item} />
        ))}
      </ScrollView>

      {/* ⭐ 底部操作栏也可以抽取为组件 */}
      <BottomBar onSubmit={handleAction} />

      {/* 底部安全区域 */}
      <SafeArea position="bottom" />
    </View>
  )
}

// ⭐ 导出（所有页面都必须用 DetailLoginHOC 包裹）
export default DetailLoginHOC({PageName})
```

### 页面级子组件示例（components/HeaderSection.tsx）

```typescript
import { FC } from 'react'
import { View } from '@tarojs/components'

interface HeaderSectionProps {
  onAction: () => void
}

const HeaderSection: FC<HeaderSectionProps> = ({ onAction }) => {
  return (
    <View className="mb-[30px] px-[30px] pt-[20px]">
      <View className="text-[38px] font-semibold text-[#212121]">
        标题内容
      </View>
      <View className="mt-[12px] text-[26px] text-[#999]">
        描述信息
      </View>
      <View
        className="mt-[20px] rounded-[16px] bg-[#01c176] px-[30px] py-[16px] text-center text-[28px] text-white"
        onClick={onAction}
      >
        操作按钮
      </View>
    </View>
  )
}

export default HeaderSection
```

### 页面级子组件示例（components/ContentCard.tsx）

```typescript
import { FC } from 'react'
import { View } from '@tarojs/components'

interface ContentCardProps {
  data: {
    id: string
    title: string
    description: string
  }
}

const ContentCard: FC<ContentCardProps> = ({ data }) => {
  return (
    <View className="mx-[30px] mb-[20px] rounded-[16px] bg-[#f7f7f7] p-[20px]">
      <View className="text-[30px] font-medium text-[#212121]">
        {data.title}
      </View>
      <View className="mt-[8px] text-[26px] text-[#646464]">
        {data.description}
      </View>
    </View>
  )
}

export default ContentCard
```

### 页面配置文件（index.config.ts）

```typescript
export default definePageConfig({
  navigationStyle: 'custom',
  disableScroll: true
})
```

**说明**：

- ⚠️ **`definePageConfig` 是全局变量，不需要手动导入**（不要写 `import { definePageConfig } from '@tarojs/taro'`）
- `navigationStyle: 'custom'` - 使用自定义导航栏（项目中所有页面都使用 NavHeader 组件）
- `disableScroll: true` - 禁用页面滚动（由页面内部的 ScrollView 或 View 控制滚动）

### 类型定义文件（src/types/pages/{PageName}.ts）

```typescript
/**
 * {PageName} 页面类型定义
 */

/**
 * 页面路由参数
 */
export interface {PageName}Params {
  id?: string
  // TODO: 添加其他参数
}

/**
 * 数据项类型
 */
export interface DataItem {
  id: string
  name: string
  // TODO: 添加其他字段
}
```

### 样式文件（index.module.scss）

```scss
// ⭐ 禁止页面滚动（所有 Taro 页面必须）
:global(.taro_page) {
  overflow: hidden;
}

// ⭐ 移动端隐藏滚动条（所有 Taro 页面必须）
.pageScroll {
  &::-webkit-scrollbar {
    display: none;
  }
}

// 其他复杂样式（渐变、动画等）
.customStyle {
  // 复杂样式定义
}
```

### 说明文档（README.md）

```markdown
# {PageName}

## 页面概述

TODO: 页面功能描述

## 技术栈

- **框架**: Taro 3.6.20 + React 18 + TypeScript
- **样式**: TailwindCSS 3.4.17 + CSS Modules
- **状态管理**: React Hooks (useState)
- **导航**: navigateToEnhance
- **埋点**: usePageLog Hook

## 路由参数

| 参数 | 类型   | 说明 |
| ---- | ------ | ---- |
| id   | string | TODO |

## 功能特性

- TODO: 列出主要功能

## 项目规范遵循

✅ 使用标准 React FC（函数组件）  
✅ 必须使用 NavHeader 组件  
✅ 必须使用 DetailLoginHOC 包裹  
✅ **首次加载逻辑在 useMount**（ahooks）  
✅ useDidShow 可选  
✅ **类型定义放在 `src/types/pages/` 下**  
✅ **不使用 enum，改用字面量联合类型**  
✅ **优先使用 TailwindCSS utility classes**  
✅ 复杂样式使用 CSS Modules  
✅ **图标优先使用 iconfont**，无对应图标时用 `ic_help` 占位

## 更新日志

### {当前日期}

- 初始创建
```

---

## 重要规范

创建页面时必须遵循以下项目规范：

### 1. 组件化规范

**⭐ 页面组件化原则**（必须遵守）:

- ✅ **页面主文件保持简洁**：主要负责数据获取、状态管理和整体布局
- ✅ **功能模块组件化**：将独立的功能模块拆分为子组件
- ✅ **组件存放位置**：页面级子组件放在 `src/pages/{PageName}/components/` 目录下
- ✅ **组件命名规范**：使用 PascalCase，例如 `HeaderSection.tsx`、`ContentCard.tsx`、`BottomBar.tsx`
- ✅ **组件职责单一**：每个子组件只负责一个功能模块，便于维护和复用
- ✅ **Props 类型定义**：所有子组件都必须有完整的 TypeScript 类型定义

**组件化拆分建议**：

| 页面区域   | 建议组件化 | 组件名示例          |
| ---------- | ---------- | ------------------- |
| 顶部标题栏 | ✅ 是      | `HeaderSection.tsx` |
| 搜索栏     | ✅ 是      | `SearchBar.tsx`     |
| 筛选器     | ✅ 是      | `FilterBar.tsx`     |
| 内容卡片   | ✅ 是      | `ContentCard.tsx`   |
| 列表项     | ✅ 是      | `ListItem.tsx`      |
| 操作面板   | ✅ 是      | `ActionPanel.tsx`   |
| 底部操作栏 | ✅ 是      | `BottomBar.tsx`     |
| 弹窗内容   | ✅ 是      | `ModalContent.tsx`  |

**页面级组件 vs 全局组件**：

- **页面级组件**（`pages/{PageName}/components/`）: 仅在当前页面使用的组件
- **全局组件**（`src/components/` 或 `src/components-pro/`）: 可在多个页面复用的组件

**组件化示例**：

```typescript
// ❌ 不推荐：所有逻辑都在页面主文件
const Page = () => {
  return (
    <View>
      <View>{/* 200 行标题部分代码 */}</View>
      <View>{/* 300 行内容部分代码 */}</View>
      <View>{/* 150 行底部操作栏代码 */}</View>
    </View>
  )
}

// ✅ 推荐：拆分为子组件
const Page = () => {
  return (
    <View>
      <HeaderSection {...props} />
      <ContentSection {...props} />
      <BottomBar {...props} />
    </View>
  )
}
```

### 2. 生命周期

- ✅ 使用 `useMount`（来自 ahooks）进行首次加载
- ✅ `useDidShow` 是可选的，默认不提供
- ✅ 所有页面必须使用 `DetailLoginHOC` 包裹
- ✅ 所有页面必须使用 `NavHeader` 组件

### 3. 样式规范

- ✅ 优先使用 TailwindCSS utility classes
- ✅ CSS Modules 仅用于复杂样式（渐变、伪元素、背景图）
- ✅ 设计稿基于 750px 宽度（1px = 2rpx）
- ⚠️ **Border 样式必须明确指定 border-style**（默认不显示）

**Border 使用规范**：

Tailwind CSS 的 border 相关类名（如 `border`, `border-[2px]`）只设置 border-width 和 border-color，不会自动设置 border-style，导致边框不显示。

**四边边框**：使用 `border-solid`

```typescript
// ❌ 错误：边框不会显示
<View className="border-[2px] border-[#eaf5f1]">内容</View>

// ✅ 正确：必须添加 border-solid
<View className="border-[2px] border-solid border-[#eaf5f1]">内容</View>

// ✅ 正确：使用 border 默认值（1px）
<View className="border border-solid border-[#e5e5e5]">内容</View>
```

**单边边框**：使用 CSS Modules（⚠️ Tailwind 不支持单边 border-style）

```typescript
// ❌ 错误：border-solid 会影响所有边框
<View className="border-t-[2px] border-solid border-t-[#f0f0f0]">内容</View>

// ✅ 正确：使用 CSS Modules（尺寸需 x2）
// index.tsx
<View className={styles.topBorder}>内容</View>

// index.module.scss
.topBorder {
  border-top: 2px solid #f0f0f0;
}
```

**常见单边边框样式**（尺寸均为设计稿 x2）：

```scss
// 顶部边框
.topBorder {
  border-top: 2px solid #f0f0f0;
}

// 底部边框
.bottomBorder {
  border-bottom: 2px solid #e5e5e5;
}

// 左侧边框
.leftBorder {
  border-left: 4px solid #01c176;
}

// 右侧边框
.rightBorder {
  border-right: 2px solid #ddd;
}
```

### 4. 图标规范

- ⭐ **优先使用项目现有的 iconfont**
- ✅ 图标通过 CSS 类名引用：`<View className="icon {图标类名} text-[尺寸] text-[颜色]" />`
- ✅ 如果没有对应的图标，使用 `ic_help` 作为占位符
- ✅ 常用图标示例：
  - 添加：`ic_add`
  - 删除：`ic_delete_tool`
  - 编辑：`bianji`
  - 搜索：`ic_search`
  - 返回：`ic_back`
  - 帮助：`ic_help`
  - 设置：`ic_setting`
  - 下拉：`xiala`
  - 选中：`ic_selected`
  - 未选中：`ic_select_normal`
- ✅ iconfont 已在 app.tsx 全局引入，无需单独导入
- ✅ 完整图标列表见：`src/assets/iconfont/iconfont.json`（169 个图标）

**使用示例**：

```typescript
// 添加按钮
<View className="icon ic_add text-[32px] text-[#01c176]" />

// 编辑按钮
<View className="icon bianji text-[28px] text-[#212121]" />

// 占位符（暂无合适图标时）
<View className="icon ic_help text-[24px] text-[#999]" />
```

### 5. 类型定义

- ✅ 类型定义必须放在 `src/types/pages/` 目录下
- ✅ 不使用 `enum`，改用字面量联合类型（`type X = 'a' | 'b'`）
- ✅ 使用 `import type` 导入类型

### 6. 代码规范

- ✅ 使用 navigateToEnhance 进行导航
- ✅ 添加完整埋点（usePageLog）
- ✅ 所有函数和变量都有完整类型定义
- ✅ 禁止使用 `any`

### 7. 文件命名

- ✅ 页面组件：PascalCase（如 `UserProfilePage`）
- ✅ 目录名：与组件同名
- ✅ 类型文件：与页面同名

---

## 执行检查清单

在创建页面完成后，验证以下内容：

**文件结构**:

- [ ] 页面文件已创建（index.tsx、index.config.ts、index.module.scss、README.md）
- [ ] ⭐ components/ 目录已创建（用于存放页面级子组件）
- [ ] ⭐ index.config.ts 包含正确配置（navigationStyle: 'custom', disableScroll: true）
- [ ] 类型定义文件已创建（src/types/pages/{PageName}.ts）
- [ ] 路由已配置（app.config.ts 或 modulePagesConfig.ts）
- [ ] 模块环境配置已创建（如果是新模块）
- [ ] 所有文件使用正确的命名规范

**组件化**:

- [ ] ⭐ 页面主文件保持简洁（主要负责数据获取、状态管理、整体布局）
- [ ] ⭐ 独立功能模块已拆分为子组件
- [ ] ⭐ 子组件放在 components/ 目录下
- [ ] ⭐ 子组件命名使用 PascalCase
- [ ] ⭐ 子组件有完整的 TypeScript 类型定义

**基础规范**:

- [ ] 页面组件使用 DetailLoginHOC 包裹
- [ ] 页面包含 NavHeader 组件
- [ ] 使用 useMount 进行首次加载
- [ ] 类型定义使用字面量联合类型（不使用 enum）
- [ ] 样式优先使用 TailwindCSS
- [ ] ⭐ 图标使用 iconfont（格式：`<View className="icon {图标类名} text-[尺寸] text-[颜色]" />`）
- [ ] ⭐ 无对应图标时使用 ic_help 占位

---

## 常见问题

### Q: 如何知道应该创建模块页面还是普通页面？

A:

- **模块页面**：属于 blended 模式的独立分包，会嵌入到原生微信小程序中
- **普通页面**：项目的主包页面，不属于任何模块

如果页面是新业务模块的一部分，建议创建为模块页面。

### Q: 模块名称有什么命名规范？

A:

- 使用 camelCase
- 必须以 `Module` 结尾
- 例如：`wordMemoryModule`、`growthRecordModule`

### Q: 如何验证页面创建成功？

A: 检查以下内容：

1. 文件已创建在正确位置
2. 路由配置已更新
3. 没有 TypeScript 类型错误
4. 可以通过路由访问页面

### Q: 创建的页面可以直接运行吗？

A: 可以，但需要：

1. 运行 `pnpm install`（如果修改了 package.json）
2. 普通页面：运行 `pnpm run dev:h5` 或 `pnpm run dev:weapp`
3. 模块页面：运行 `pnpm run dev_blended:{moduleName}`

### Q: 什么时候应该拆分子组件？

A: 遵循以下原则：

1. **功能独立**：当某个区块有独立的功能逻辑时
2. **代码行数**：单个区块超过 50 行时建议拆分
3. **复用可能**：可能在页面内多次使用的模块
4. **职责单一**：每个组件只负责一个功能

示例：

- 搜索栏（独立交互逻辑）→ 拆分为 `SearchBar.tsx`
- 内容卡片（重复渲染）→ 拆分为 `ContentCard.tsx`
- 底部操作栏（独立布局区域）→ 拆分为 `BottomBar.tsx`

### Q: 页面级子组件和全局组件有什么区别？

A:

**页面级子组件**（`src/pages/{PageName}/components/`）:

- 仅在当前页面使用
- 与页面业务逻辑强相关
- 不需要考虑复用性
- 示例：特定页面的标题栏、内容卡片

**全局组件**（`src/components/` 或 `src/components-pro/`）:

- 可在多个页面复用
- 通用性强，业务逻辑解耦
- 需要考虑 API 设计和扩展性
- 示例：NavHeader、BlockButton、CustomModal

建议：优先创建页面级组件，当发现多个页面需要使用时，再考虑提升为全局组件。

---

## 示例场景

### 示例 1：创建用户资料页面

```bash
/createNewPage UserProfilePage
```

**结果**：

- 创建 `src/pages/UserProfilePage/` 目录及文件
- 创建 `src/types/pages/UserProfilePage.ts`
- 更新 `src/app.config.ts`
- 页面可通过 `/pages/UserProfilePage/index` 访问

### 示例 2：为单词记忆模块创建新页面

```bash
/createNewPage WordTestPage wordMemoryModule
```

**结果**：

- 创建 `src/pages/WordTestPage/` 目录及文件
- 创建 `src/types/pages/WordTestPage.ts`
- 更新 `src/modulePagesConfig.ts`，添加到 `wordMemoryModulePages`
- 页面可通过 `pnpm run dev_blended:wordMemoryModule` 开发

### 示例 3：创建新模块及首页

```bash
/createNewPage ExamCenterPage examCenterModule
```

**结果**：

- 创建模块环境配置：`.env.development_blended_examCenterModule`
- 创建模块环境配置：`.env.production_blended_examCenterModule`
- 更新 `src/modulePagesConfig.ts`，添加新模块配置
- 更新 `src/app.config.ts`，导入新模块
- 更新 `package.json`，添加开发脚本
- 创建页面文件和类型定义
- 提供开发命令：`pnpm run dev_blended:examCenterModule`

---

## 后续步骤

页面创建完成后，开发者需要：

1. **完善页面功能**：

   - 实现数据加载逻辑
   - 添加交互功能
   - 完善 UI 样式

2. **更新类型定义**：

   - 根据实际需求添加类型
   - 定义数据模型

3. **添加埋点**：

   - 为关键操作添加埋点事件

4. **编写文档**：

   - 更新 README.md
   - 添加功能说明

5. **测试验证**：
   - 功能测试
   - 类型检查
   - 样式验证
