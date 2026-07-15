---
name: figmaCreatePage
description: 从 Figma 设计一步到位创建符合项目规范的页面。自动应用尺寸转换（x2），并创建完整文件结构。用法：/figmaCreatePage <Figma URL> <页面名称> [模块名称]
---

# figmaCreatePage — 从 Figma 一键创建页面

从 Figma 设计稿一步到位创建符合 react-taro-teacher 项目规范的完整页面，自动整合 figma-mcp、figmaToTaroPage 和 createNewPage 三个流程。

## 使用场景

**触发时机**：用户提供 Figma URL 并希望创建新页面

**命令格式**：`/figmaCreatePage <Figma URL> <页面名称> [模块名称]`

**作用**：

1. 从 Figma 获取设计并生成代码
2. 自动应用项目规则（尺寸 x2）
3. 创建完整文件结构和配置

## Skill 参数

- **Figma URL**（必需）：Figma 设计链接，格式如 `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
- **页面名称**（必需）：页面组件名称，使用 PascalCase，例如 `UserProfilePage`、`TaskDetailPage`
- **模块名称**（可选）：blended 模块名称，例如 `wordMemoryModule`、`growthRecordModule`

### 使用示例

```bash
# 创建普通页面
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 UserProfilePage

# 创建模块页面
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 TaskDetailPage wordMemoryModule

# 创建新模块的页面
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 HomePage examModule
```

## 工作流程

### Step 1: 参数验证

1. 验证 Figma URL 格式
2. 提取 fileKey 和 nodeId
3. 验证页面名称（PascalCase）
4. 如果提供模块名称，验证格式（camelCase，以 `Module` 结尾）
5. 检查页面是否已存在

### Step 2: 从 Figma 获取设计

使用 `figma-implement-design` 获取设计并生成初始代码：

```typescript
// 自动执行
figma-implement-design
  - 输入：fileKey, nodeId
  - 输出：初始 React 组件代码（使用 Figma 原始尺寸）
```

### Step 3: 应用 figmaToTaroPage 规则

自动应用以下转换规则（参考 `figmaToTaroPage` skill）：

**1. 尺寸转换（x2）**

- 所有宽度、高度、padding、margin、gap、font-size、border-radius 等数值 × 2
- 示例：`w-[200px]` → `w-[400px]`，`text-[14px]` → `text-[28px]`

**2. 组件映射**

- 底部固定按钮 → `<BlockButton>`
- 弹窗 → `<CustomModal>`
- 列表 → `<List>`

**3. 必备组件**

- 添加 `<NavHeader>` 导航栏（放在最顶部）
- 使用 `DetailLoginHOC` 包裹页面
- 添加 `<SafeArea>` 底部安全区域（可选）

**4. 代码规范**

- 使用 `useMount` 进行首次加载
- 类型定义使用 `import type`
- 优先使用 TailwindCSS，复杂样式使用 CSS Modules
- ⚠️ **Border 样式规范**：

  - **四边边框**：使用 `border-solid`
    - 错误：`border-[2px] border-[#eaf5f1]`
    - 正确：`border-[2px] border-solid border-[#eaf5f1]`
  - **单边边框**：使用 CSS Modules（Tailwind 不支持单边 border-style）

    - ❌ 错误：`border-t-[2px] border-solid border-t-[#f0f0f0]`（`border-solid` 会影响所有边框）
    - ✅ 正确：在 `index.module.scss` 中定义样式（尺寸需 x2）

      ```tsx
      // index.tsx
      <View className={styles.topBorder}>内容</View>

      // index.module.scss
      .topBorder {
        border-top: 2px solid #f0f0f0;
      }
      ```

**5. 图标规范**

- ⭐ **优先使用项目现有的 iconfont**（169 个图标可用）
- 格式：`<View className="icon {图标类名} text-[尺寸] text-[颜色]" />`
- 如果没有对应的图标，使用 `ic_help` 作为占位符
- 常用图标：`ic_add`（添加）、`bianji`（编辑）、`ic_search`（搜索）、`ic_selected`（选中）、`xiala`（下拉）
- iconfont 已全局引入，无需单独导入

**6. 组件化规范**

- ⭐ **页面主文件保持简洁**：主要负责数据获取、状态管理和整体布局
- ⭐ **功能模块组件化**：将独立的功能模块拆分为子组件，放在 `components/` 目录下
- ⭐ **组件命名**：使用 PascalCase（如 `HeaderSection.tsx`、`ContentCard.tsx`）
- ⭐ **职责单一**：每个子组件只负责一个功能模块
- 建议拆分的模块：标题栏、搜索栏、筛选器、内容卡片、列表项、操作面板、底部操作栏

**7. 文字渲染规范**

- ⭐ **优先使用 View 组件渲染文字**，而不是 Text 组件（多端兼容性更好）
- ⭐ **防止文字换行**：所有 View 渲染的文字都必须添加防换行处理
  - **单行文字**：添加 `whitespace-nowrap` 类名
    ```tsx
    <View className="whitespace-nowrap text-[30px] text-[#212121]">标题文字</View>
    ```
  - **多行文字容器**：使用 `flex` 布局组合多个 View
    ```tsx
    <View className="flex items-center">
      <View>预计学习</View>
      <View className="mx-[4px]">{minutes}</View>
      <View>分钟</View>
    </View>
    ```
  - **长文本允许换行**：不添加 `whitespace-nowrap`，让内容自然换行
    ```tsx
    <View className="text-[30px] leading-[48px]">这是一段很长的文字内容...</View>
    ```
  - **特殊情况**：如果 View 无法满足样式需求，仍然可以使用 Text 组件

**8. 底部固定元素识别和实现规范**

- ⭐ **正确识别和实现 Figma 中的底部固定元素**
- **问题描述**：
  - Figma 中使用 `absolute` 定位的底部元素，在代码中容易被误放入 `ScrollView` 内
  - 导致这些本应固定的元素随内容滚动，不符合设计意图
- **智能识别规则**（综合判断，不是单一标准）：

  **1. 语义判断（权重最高）**

  - 检查元素的 `data-name` 属性，包含以下关键词的通常需要固定：
    - `导航`、`nav`、`navigation`
    - `底部`、`bottom`、`footer`
    - `按钮`、`button`、`操作`、`action`
    - `提示`、`tip`、`hint`
    - `悬浮`、`float`、`fixed`
  - 常见固定元素名称示例：
    - `底部导航`、`底部按钮`、`底部操作栏`
    - `预计学习时间`、`内容有误？去反馈`
    - `Home Indicator`（iOS 底部指示器）

  **2. 位置判断**

  - 检查元素是否在页面底部 25% 区域内（更宽松的判断）
  - 计算方式：`(页面高度 - 元素top值) / 页面高度 < 0.25`
  - 或者：元素的 `bottom` 值 ≤ 页面高度的 20%

  **3. 定位方式判断**

  - 使用 `absolute` 定位且相对于页面根元素定位（不是相对于父容器）
  - 检查父元素：如果父元素已经是滚动容器，则子元素不应该固定

  **4. 上下文判断**

  - 检查是否有 group 包含多个底部元素
  - 该 group 的位置是否在页面底部
  - group 名称是否包含"底部"、"固定"等关键词

  **5. 功能判断（根据元素类型）**

  - **应该固定**：
    - 按钮栏、操作栏、工具栏
    - 提示文字、状态栏
    - 导航栏（TabBar）
    - 悬浮按钮
  - **不应该固定**：
    - 列表项、卡片
    - 内容区域
    - 普通文本段落

  **决策流程**：

  ```
  1. 语义判断：名称包含固定关键词？
     ├─ 是 → 固定
     └─ 否 → 继续判断

  2. 位置判断：在底部 25% 区域内？
     ├─ 否 → 不固定
     └─ 是 → 继续判断

  3. 上下文判断：属于底部 group？
     ├─ 是 → 固定
     └─ 否 → 继续判断

  4. 功能判断：是按钮/操作栏/提示？
     ├─ 是 → 固定
     └─ 否 → 不固定（放在 ScrollView 内）
  ```

- **实际案例分析**：

  以 CustomContentSelectPage 为例，Figma 返回的结构：

  ```html
  <!-- group: 底部区域 (node-id: 12438:30645, top: 662px, 页面高度: 1624px) -->
  <div className="absolute contents left-0 top-[662px]">
    <!-- 1. 反馈按钮 (data-name="历史记录", top: 662px) -->
    <div className="absolute ... top-[662px]" data-name="历史记录"> 内容有误？去反馈 </div>

    <!-- 2. 底部导航 (data-name="底部导航", bottom: 0, height: 94px) -->
    <div className="absolute bottom-0 h-[94px]" data-name="底部导航"> 批量选择 + 去布置 </div>

    <!-- 3. 预计时间 (top: 696px) -->
    <div className="absolute ... top-[696px]"> 预计学习 5 分钟 </div>
  </div>
  ```

  **判断过程**：

  1. ✅ 语义判断：
     - "底部导航" → 包含"底部"关键词 → 应该固定
     - "历史记录"（反馈按钮） → 功能是反馈 → 应该固定
     - "预计学习时间" → 位于底部区域，与其他固定元素在同一 group → 应该固定
  2. ✅ 位置判断：
     - 所有元素 top 值 ≥ 662px，页面高度 1624px
     - (1624 - 662) / 1624 = 59% → 在底部区域
  3. ✅ 上下文判断：
     - 三个元素都在同一个 group 内
     - 该 group 使用 `absolute` 定位在页面底部

  **结论**：这三个元素都应该固定

- **实现规范**：

  ```tsx
  // ❌ 错误：将底部固定元素放在 ScrollView 内
  <ScrollView scrollY>
    <View>内容</View>
    <View>预计学习时间</View> {/* 会随内容滚动 */}
  </ScrollView>
  <View className={styles.bottomBar}>底部按钮</View>

  // ✅ 正确：将底部固定元素移出 ScrollView
  <ScrollView scrollY className="pb-[280px]">
    {/* pb-[280px] 确保内容不被底部固定区域遮挡 */}
    <View>内容</View>
  </ScrollView>

  {/* 底部固定区域 1：提示信息 */}
  <View className={styles.bottomFixedArea}>
    <View>内容有误？去反馈</View>
    <View>预计学习 5 分钟</View>
  </View>

  {/* 底部固定区域 2：操作按钮 */}
  <View className={styles.bottomBar}>
    <View>批量选择</View>
    <View>去布置</View>
  </View>
  ```

- **样式配置**：

  ```scss
  // 底部固定区域（提示信息）
  .bottomFixedArea {
    position: fixed;
    bottom: 154px; // 计算方式：底部按钮高度 + padding + safe-area
    left: 0;
    right: 0;
    z-index: 10;
  }

  // 底部操作栏
  .bottomBar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 20; // 确保在 bottomFixedArea 之上
    padding-bottom: constant(safe-area-inset-bottom);
    padding-bottom: env(safe-area-inset-bottom);
  }
  ```

- **层级关系**：

  - 使用 `z-index` 控制多个固定层的层级关系
  - 越靠底部的元素，`z-index` 值越大
  - ScrollView 内容：z-index 默认（0）
  - 中间固定层：z-index: 10
  - 底部操作栏：z-index: 20

- **特殊情况处理**：

  **情况 1：悬浮按钮（Floating Action Button）**

  - 通常在右下角或右上角
  - 使用 `position: fixed` + 具体的 `right`/`bottom` 值
  - 不需要完整的横向宽度

  ```tsx
  <View className={styles.fabButton}>
    <View className="icon ic_add" />
  </View>

  // SCSS
  .fabButton {
    position: fixed;
    right: 30px;
    bottom: 200px;
    z-index: 30;
  }
  ```

  **情况 2：多个滚动容器共存**

  - 如果页面有多个独立的滚动区域，每个区域可能有自己的固定元素
  - 固定元素应该相对于其所属的滚动容器定位
  - 使用 `position: sticky` 代替 `fixed`（如果适用）

  **情况 3：内容较少时**

  - 当内容不足一屏时，底部固定元素仍然应该固定在底部
  - 不要因为内容少就改为相对定位
  - ScrollView 的 `min-height` 确保至少占满一屏

  **情况 4：横屏模式**

  - 底部固定元素的高度和位置可能需要调整
  - 考虑使用 CSS 媒体查询或动态计算

- **常见误判情况**：

  **误判为固定（实际应该放在 ScrollView 内）**：

  - ❌ 列表项底部的"查看更多"按钮（应该在列表末尾）
  - ❌ 卡片内部的操作按钮
  - ❌ 分组标题下方的说明文字

  **误判为非固定（实际应该固定）**：

  - ❌ 使用 `relative` 定位但位于底部的操作栏
  - ❌ 嵌套在多层容器内的底部按钮
  - ❌ 动态显示/隐藏的底部提示

**9. 代码质量检查和修复**

- ⭐ **创建完成后必须修复所有 TypeScript 和 ESLint 错误**
- 常见问题及修复方案：
  - **未使用的变量**：
    - 如果变量确实不需要，移除声明或使用 `const` 代替 `useState`
    - 埋点相关的 `Log` 变量可以注释掉，待开发者补充
  - **函数声明顺序**：
    - 被 `useMount` 等 Hook 调用的函数必须在 Hook 之前声明
    - 工具函数应该放在组件顶部（状态声明之后）
  - **未使用的函数参数**：
    - 回调函数如果不需要参数，直接移除参数
    - 如果参数在未来会用到，添加注释说明
  - **async 函数没有 await**：
    - 如果函数内部没有异步操作，移除 `async` 关键字
  - **catch 块未使用的 error**：
    - 使用空 `catch (e) {}` 或 `catch (e) { /* ignore */ }`
  - **Image 组件的 src 类型问题**：
    - 使用 `??` 操作符处理可能的 undefined：`src={iconMap[type] ?? defaultIcon ?? ''}`
  - **map 的 key 使用 index**：
    - 优先使用数据的唯一标识（如 `id`、`type`）作为 key
    - 示例：`key={item.id}` 或 `key={setting.type}`

### Step 4: 应用 createNewPage 流程

根据是否提供模块名称，执行不同流程：

#### 场景 A：创建普通页面（无模块名称）

1. **创建页面文件**：`src/pages/{PageName}/index.tsx`
2. **创建页面配置**：`src/pages/{PageName}/index.config.ts`
3. **创建类型定义**：`src/types/pages/{PageName}.ts`
4. **创建样式文件**：`src/pages/{PageName}/index.module.scss`（如有复杂样式）
5. **创建组件目录**：`src/pages/{PageName}/components/`（用于存放页面级子组件）
6. **配置路由**：更新 `src/app.config.ts`，添加页面路径

#### 场景 B：创建模块页面（有模块名称）

**B1：模块已存在**

1. 创建页面文件、页面配置、类型定义、样式文件、组件目录
2. 更新 `src/modulePagesConfig.ts`，在对应模块的 pages 数组中添加页面路径

**B2：模块不存在（新建模块）**

1. 创建环境配置文件：

   - `.env.development_blended_{moduleName}`
   - `.env.production_blended_{moduleName}`

2. 更新 `src/modulePagesConfig.ts`，添加模块配置：

   ```typescript
   export const {moduleName}Name = '{moduleName}'
   export const {moduleName}Pages = ['pages/{PageName}/index']
   ```

3. 更新 `package.json`，添加开发和构建脚本

4. 创建页面文件、页面配置、类型定义、样式文件

### Step 4.5: （可选）添加 API 定义

**在 Step 4 完成后，必须向用户提问**：

```
✅ 页面文件结构已创建完成。

是否需要为此页面添加 API 定义？
- 回复「是」或提供接口信息（路径/Apifox链接），将自动生成 API 函数和类型定义
- 回复「否」或直接回车跳过，后续可单独执行 /addPageApis {PageName}
```

**如果用户回复「是」或直接提供了接口信息**：

按照 `addPageApis` skill 的完整流程执行（参见 [addPageApis/SKILL.md](../addPageApis/SKILL.md)）：

1. 收集所有接口信息（路径、方法、说明、Apifox 链接）
2. 调用 Apifox MCP 获取接口详情（如提供了链接）
3. 生成 `src/types/api/{module}-api.ts`
4. 生成 `src/api/{module}-api.ts`
5. 询问是否生成 Zustand Store
6. 在 Step 5 的页面代码中直接引用生成的 API 函数（替换 `// TODO: 加载数据`）

**如果用户回复「否」或跳过**：

继续执行 Step 5，页面中保留 `// TODO: 加载数据` 注释，并在反馈结果中提示：

```
⚠️ 未添加 API 定义，loadData 函数保留 TODO 注释。
   后续可执行：/addPageApis {PageName} 补充 API 层代码。
```

---

### Step 5: 生成最终代码

生成的页面代码结构：

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

const {PageName}: FC = () => {
  // 埋点 Hook（页面级初始化，action 埋点待开发者按需补充）
  usePageLog('{PageName}', {
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
      // TODO: 处理逻辑
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
        {/* ✅ 使用项目组件 */}
      </ScrollView>

      <SafeArea position="bottom" />
    </View>
  )
}

// ⭐ 必须：登录验证 HOC
export default DetailLoginHOC({PageName})
```

页面配置文件（`src/pages/{PageName}/index.config.ts`）：

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

样式文件（`src/pages/{PageName}/index.module.scss`）：

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
```

类型定义文件（`src/types/pages/{PageName}.ts`）：

```typescript
// 页面参数类型
export interface {PageName}Params {
  id?: string
}

// 其他页面相关类型定义
export interface DataItem {
  id: string
  title: string
}

// 使用字面量联合类型，不使用 enum
export type Status = 'pending' | 'active' | 'completed'
```

### Step 6: 代码质量检查和修复

**创建文件后，必须执行以下检查和修复步骤**：

1. **修复所有未使用的变量**

   - 检查并移除或注释未使用的导入（如 `usePageLog`）
   - 调整函数声明顺序（被 Hook 调用的函数必须在 Hook 之前）
   - 移除未使用的 `loading`、`setLoading` 等状态（如果确实不需要）
   - 注释掉未使用的埋点 `Log` 变量，待开发者补充

2. **修复 TypeScript 类型错误**

   - 使用 `??` 操作符处理可能的 undefined 值
   - 确保 Image 组件的 src 有正确的类型：`src={value ?? defaultValue ?? ''}`

3. **修复 ESLint 错误**

   - 移除 `async` 关键字（如果函数内没有 await）
   - 使用数据唯一标识作为 map 的 key（不使用 index）
   - 使用空 catch 块或添加注释：`catch { /* ignore */ }`

4. **添加文字防换行处理**

   - 检查所有 View 渲染的文字
   - 单行文字添加 `whitespace-nowrap`
   - 多段文字使用 flex 布局拆分

5. **验证代码质量**
   ```bash
   # 检查 ESLint（可选）
   pnpm exec eslint src/pages/{PageName}/**/*.tsx --format=compact
   ```

### Step 7: 反馈结果

告知用户：

1. **创建的文件列表**：

   - ✅ `src/pages/{PageName}/index.tsx`
   - ✅ `src/pages/{PageName}/index.config.ts`
   - ✅ `src/types/pages/{PageName}.ts`
   - ✅ `src/pages/{PageName}/index.module.scss`（如有）
   - ✅ `src/pages/{PageName}/components/`（子组件目录）

2. **配置更新**：

   - ✅ 路由已配置（`app.config.ts` 或 `modulePagesConfig.ts`）
   - ✅ 模块配置已更新（如为新模块）
   - ✅ package.json 脚本已添加（如为新模块）

3. **代码质量**：

   - ✅ 所有 TypeScript 错误已修复
   - ✅ 所有 ESLint 错误已修复
   - ✅ 文字渲染已添加防换行处理

4. **开发命令**：

   - 普通页面：页面路径为 `/pages/{PageName}/index`
   - 模块页面：运行 `pnpm run dev_blended:{moduleName}` 开发

5. **注意事项**：
   - ⚠️ 已应用尺寸 x2 规则
   - ⚠️ 已添加必备组件（NavHeader, DetailLoginHOC）
   - ⚠️ 已拆分子组件（功能模块化）

## 完整示例

### 示例 1：创建普通用户资料页面

**命令**：

```bash
/figmaCreatePage https://figma.com/design/abc123/UserProfile?node-id=10-5 UserProfilePage
```

**执行流程**：

1. ✅ 验证参数
2. ✅ 从 Figma 获取设计（头像、姓名、简介、编辑按钮）
3. ✅ 应用转换规则：
   - 头像大小：60px → 120px
   - 姓名字号：18px → 36px
   - 简介字号：14px → 28px
   - 按钮高度：44px → 88px
4. ✅ 创建文件：
   - `src/pages/UserProfilePage/index.tsx`
   - `src/types/pages/UserProfilePage.ts`
5. ✅ 配置路由：`app.config.ts` 添加 `pages/UserProfilePage/index`

**结果反馈**：

```
✅ 页面创建成功！

创建的文件：
  - src/pages/UserProfilePage/index.tsx
  - src/types/pages/UserProfilePage.ts

路由配置：
  - 路径：/pages/UserProfilePage/index

已应用的规则：
  ✅ 所有尺寸 x2
  ✅ 添加 NavHeader 和 DetailLoginHOC
  ✅ 使用项目组件（BlockButton）
```

---

### 示例 2：为现有模块创建任务详情页面

**命令**：

```bash
/figmaCreatePage https://figma.com/design/def456/TaskDetail?node-id=20-10 TaskDetailPage wordMemoryModule
```

**执行流程**：

1. ✅ 验证参数
2. ✅ 检查 wordMemoryModule 存在
3. ✅ 从 Figma 获取设计
4. ✅ 应用转换规则
5. ✅ 创建文件
6. ✅ 更新模块配置：`modulePagesConfig.ts` 中的 `wordMemoryModulePages` 数组

**结果反馈**：

```
✅ 模块页面创建成功！

创建的文件：
  - src/pages/TaskDetailPage/index.tsx
  - src/types/pages/TaskDetailPage.ts
  - src/pages/TaskDetailPage/index.module.scss

模块配置：
  - 模块：wordMemoryModule
  - 已更新：src/modulePagesConfig.ts

开发命令：
  pnpm run dev_blended:wordMemoryModule
```

---

### 示例 3：创建新模块和首页

**命令**：

```bash
/figmaCreatePage https://figma.com/design/ghi789/ExamHome?node-id=30-15 ExamHomePage examModule
```

**执行流程**：

1. ✅ 验证参数
2. ✅ 检测到 examModule 不存在，创建新模块
3. ✅ 创建环境配置文件：
   - `.env.development_blended_examModule`
   - `.env.production_blended_examModule`
4. ✅ 从 Figma 获取设计
5. ✅ 应用转换规则
6. ✅ 创建页面文件
7. ✅ 更新 `modulePagesConfig.ts`，添加模块配置
8. ✅ 更新 `package.json`，添加开发和构建脚本

**结果反馈**：

```
✅ 新模块和页面创建成功！

创建的文件：
  - src/pages/ExamHomePage/index.tsx
  - src/types/pages/ExamHomePage.ts
  - .env.development_blended_examModule
  - .env.production_blended_examModule

模块配置：
  - 新模块：examModule
  - 已更新：src/modulePagesConfig.ts
  - 已更新：package.json（添加开发和构建脚本）

开发命令：
  pnpm run dev_blended:examModule
```

## 检查清单

在执行完毕后，自动验证以下内容：

### ✅ 代码质量

- [ ] 所有尺寸数值是 Figma 的 2 倍
- [ ] 页面包含 `<NavHeader>` 组件
- [ ] 页面使用 `DetailLoginHOC` 包裹
- [ ] 使用 `useMount` 进行首次加载
- [ ] 类型定义在 `src/types/pages/` 目录
- [ ] 不使用 enum，使用字面量联合类型
- [ ] 优先使用项目组件

### ✅ 文件结构

- [ ] 页面文件已创建（`src/pages/{PageName}/index.tsx`）
- [ ] 类型定义已创建（`src/types/pages/{PageName}.ts`）
- [ ] 样式文件已创建（如有复杂样式）
- [ ] ⭐ components/ 目录已创建（用于存放页面级子组件）
- [ ] 路由已配置（`app.config.ts` 或 `modulePagesConfig.ts`）

### ✅ 组件化规范

- [ ] ⭐ 页面主文件保持简洁（主要负责数据获取、状态管理、整体布局）
- [ ] ⭐ 独立功能模块已拆分为子组件
- [ ] ⭐ 子组件放在 `components/` 目录下
- [ ] ⭐ 子组件命名使用 PascalCase
- [ ] ⭐ 子组件有完整的 TypeScript 类型定义

### ✅ 模块配置（如适用）

- [ ] 环境配置文件已创建
- [ ] 模块配置已添加到 `modulePagesConfig.ts`
- [ ] package.json 脚本已添加

### ✅ 代码规范

- [ ] 通过 TypeScript 类型检查（无错误）
- [ ] 通过 ESLint 检查（无错误）
- [ ] 通过 Prettier 格式化
- [ ] 无未使用的变量和导入
- [ ] 函数声明顺序正确（被 Hook 调用的函数在 Hook 之前）
- [ ] map 的 key 使用唯一标识（不使用 index）

### ✅ 样式规范

- [ ] ScrollView 添加样式类（`styles.pageScroll`）
- [ ] 样式文件中添加隐藏滚动条（`::-webkit-scrollbar { display: none }`）
- [ ] 所有 View 渲染的单行文字添加 `whitespace-nowrap`
- [ ] 多段文字使用 flex 布局组合

### ✅ 布局规范

- [ ] ⭐ 正确识别 Figma 中的底部固定元素（`absolute` 定位的底部元素）
- [ ] ⭐ 底部固定元素已从 ScrollView 中移出
- [ ] ⭐ 使用 `position: fixed` 实现底部固定布局
- [ ] ⭐ 多个固定层使用 `z-index` 控制层级关系
- [ ] ⭐ ScrollView 有足够的 `padding-bottom`，避免内容被遮挡

### ✅ 交互规范

- [ ] 关键按钮点击使用 `useDebounceFn` 防抖
- [ ] 引入 `usePageLog`，但不自动调用任何埋点方法（`Log?.uploadWeEvent`），待开发者自己实现
- [ ] `useDidShow` 可选，默认不提供（待开发者按需补充）

## 与其他 Skill 的关系

- **figma-implement-design**：用于从 Figma 获取设计并生成初始代码
- **figmaToTaroPage**：提供尺寸转换规则（自动应用）
- **createNewPage**：提供文件创建和路由配置流程（自动应用）
- **addPageApis**：在 Step 4.5 中可选集成，为页面生成 API 层代码（类型定义 + API 函数 + 可选 Store）
- **addPageInteractions**：（规划中）在 API 之后可选集成，补充页面交互逻辑

**优势**：此 skill 整合了多个流程，用户只需一个命令即可完成从 Figma 设计到项目页面的完整创建，并可按需叠加 API 定义和交互逻辑。

## 注意事项

1. **Figma 授权**：首次使用需要授权 Figma 访问权限
2. **尺寸转换**：所有 Figma 尺寸会自动 x2，无需手动调整
3. **组件优先**：会自动使用项目已有组件，避免重复实现
4. **类型安全**：生成的代码包含完整的 TypeScript 类型定义

## 常见问题

### Q: 生成的尺寸不对怎么办？

A: 尺寸应该是 Figma 的 2 倍。如果不对，检查是否正确应用了 x2 规则。

### Q: 如何修改生成的页面？

A: 生成后可以直接编辑 `src/pages/{PageName}/index.tsx` 文件。

### Q: 可以为同一个模块创建多个页面吗？

A: 可以。多次运行命令，指定相同的模块名称即可。

## 相关文档

- [figmaToTaroPage](../figmaToTaroPage/SKILL.md) - Figma 转换规则
- [createNewPage](../createNewPage/SKILL.md) - 页面创建流程
- [项目 AGENTS.md](/Users/youbao_feng/workspace/react-taro-teacher/AGENTS.md) - 项目完整规范
- [迁移规则 MIGRATION_RULES.md](/Users/youbao_feng/workspace/MIGRATION_RULES.md) - 迁移规则

## 更新日志

### 2026-04-01 - v1.2.1

- ✅ 优化底部固定元素识别规则（从单一标准改为综合判断）
- ✅ 新增智能识别算法：语义判断 + 位置判断 + 上下文判断 + 功能判断
- ✅ 添加决策流程图，清晰展示判断逻辑
- ✅ 新增实际案例分析（CustomContentSelectPage）
- ✅ 添加特殊情况处理（悬浮按钮、多滚动容器、内容较少等）
- ✅ 添加常见误判情况说明

### 2026-04-01 - v1.2.0

- ✅ 新增底部固定元素识别和实现规范
- ✅ 添加识别 Figma `absolute` 定位元素的规则
- ✅ 添加正确实现底部固定布局的示例代码
- ✅ 更新检查清单，增加布局规范检查项

### 2026-04-01 - v1.1.0

- ✅ 新增文字渲染规范（View 组件 + whitespace-nowrap）
- ✅ 新增代码质量检查步骤（修复 TypeScript 和 ESLint 错误）
- ✅ 添加常见问题修复方案（未使用变量、函数顺序、类型错误等）
- ✅ 更新检查清单，增加代码质量和文字渲染检查项

### 2026-04-01 - v1.0.0

- ✅ 初始版本发布
- ✅ 整合 figma-implement-design、figmaToTaroPage、createNewPage
- ✅ 支持创建普通页面和模块页面
- ✅ 自动应用尺寸 x2 规则
- ✅ 完整的文件创建和路由配置
