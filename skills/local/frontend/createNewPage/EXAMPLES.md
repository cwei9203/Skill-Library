# createNewPage Skill 使用示例

本文档提供 createNewPage skill 的详细使用示例和最佳实践。

## 基础用法

### 示例 1：创建简单的用户资料页面

**命令**：

```bash
/createNewPage UserProfilePage
```

**执行流程**：

1. ✅ 验证页面名称（PascalCase）
2. ✅ 检查页面是否存在
3. ✅ 创建页面目录：`src/pages/UserProfilePage/`
4. ✅ 生成文件：
   - `index.tsx` - 页面组件
   - `index.module.scss` - 样式文件
   - `README.md` - 说明文档
5. ✅ 创建类型文件：`src/types/pages/UserProfilePage.ts`
6. ✅ 更新路由配置：`src/app.config.ts`

**结果文件树**：

```
src/
├── pages/
│   └── UserProfilePage/
│       ├── index.tsx
│       ├── index.module.scss
│       └── README.md
└── types/
    └── pages/
        └── UserProfilePage.ts
```

**生成的页面组件片段**：

```typescript
import { FC, useState } from 'react'
import { View } from '@tarojs/components'
import { useMount } from 'ahooks'
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'

const UserProfilePage: FC = () => {
  usePageLog('UserProfilePage')

  useMount(() => {
  })

  return (
    <View className="flex h-screen flex-col bg-white">
      <NavHeader title="用户资料" />
      {/* 页面内容 */}
    </View>
  )
}

export default DetailLoginHOC(UserProfilePage)
```

---

## 模块页面创建

### 示例 2：为现有模块添加新页面

**场景**：为单词记忆模块（wordMemoryModule）添加一个单词测试页面

**命令**：

```bash
/createNewPage WordTestPage wordMemoryModule
```

**执行流程**：

1. ✅ 验证参数
2. ✅ 检查模块是否存在（wordMemoryModule 已存在）
3. ✅ 创建页面文件
4. ✅ 更新 `src/modulePagesConfig.ts`：
   ```typescript
   export const wordMemoryModulePages = [
     'pages/WordSelectPage/index',
     'pages/WordMemoryCreatePage/index',
     'pages/WordTestPage/index' // ← 新增
     // ... 其他页面
   ]
   ```

**开发命令**：

```bash
pnpm run dev_blended:wordMemoryModule
```

---

### 示例 3：创建新模块及首页

**场景**：创建一个全新的考试中心模块

**命令**：

```bash
/createNewPage ExamCenterHomePage examCenterModule
```

**执行流程**：

1. ✅ 验证参数
2. ✅ 检查模块不存在，开始创建新模块
3. ✅ 创建环境配置文件

**文件 1**: `.env.development_blended_examCenterModule`

```env
# 考试中心模块开发环境配置
TARO_APP_OUTPUT=examCenterModule
```

**文件 2**: `.env.production_blended_examCenterModule`

```env
# 考试中心模块生产环境配置
TARO_APP_OUTPUT=examCenterModule
```

4. ✅ 更新 `src/modulePagesConfig.ts`

```typescript
// 考试中心分包名
export const examCenterModuleName = 'examCenterModule'

// 考试中心分包相关页面
export const examCenterModulePages = ['pages/ExamCenterHomePage/index']
```

5. ✅ 更新 `src/app.config.ts`

```typescript
import {
  examCenterModuleName,
  examCenterModulePages
  // ... 其他导入
} from './modulePagesConfig'

// ... 在模块输出判断中添加
if (output === examCenterModuleName) {
  pages = examCenterModulePages
}

// ... 在 subPackages 中添加
subPackages.push({
  root: examCenterModuleName,
  pages: examCenterModulePages.map(path => path.replace(`pages/${examCenterModuleName}/`, ''))
})
```

6. ✅ 更新 `package.json`

```json
{
  "scripts": {
    "dev_blended:examCenterModule": "...",
    "build_blended:examCenterModule": "..."
  }
}
```

7. ✅ 创建页面文件和类型定义

**开发命令**：

```bash
pnpm run dev_blended:examCenterModule
```

---

## 高级场景

### 示例 4：创建带复杂参数的页面

**命令**：

```bash
/createNewPage OrderDetailPage
```

**自定义类型定义**：

创建后，开发者可以在 `src/types/pages/OrderDetailPage.ts` 中添加详细类型：

```typescript
/**
 * 订单状态（字面量联合类型）
 */
export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'completed' | 'cancelled'

/**
 * 订单详情
 */
export interface OrderDetail {
  id: string
  orderNo: string
  status: OrderStatus
  totalAmount: number
  items: OrderItem[]
  createdAt: string
}

/**
 * 订单项
 */
export interface OrderItem {
  id: string
  productName: string
  quantity: number
  price: number
}

/**
 * 页面路由参数
 */
export interface OrderDetailPageParams {
  order_id: string
}
```

**在页面中使用**：

```typescript
import type {
  OrderDetail,
  OrderStatus,
  OrderDetailPageParams
} from '@/types/pages/OrderDetailPage'

const OrderDetailPage: FC = () => {
  const params = useParams() as OrderDetailPageParams
  const [order, setOrder] = useState<OrderDetail | null>(null)

  const loadOrderData = async () => {
    const data = await fetchOrderDetail(params.order_id)
    setOrder(data)
  }

  useMount(() => {
    loadOrderData()
  })

  return (
    <View>
      {order && (
        <View>
          <View>订单号: {order.orderNo}</View>
          <View>状态: {order.status}</View>
        </View>
      )}
    </View>
  )
}
```

---

### 示例 5：创建需要复杂样式的页面

**命令**：

```bash
/createNewPage AnimatedChartPage
```

**CSS Modules 使用**：

虽然优先使用 TailwindCSS，但对于复杂动画和渐变，可以使用 CSS Modules：

```scss
// index.module.scss
@import '@/css/custom-variables-weapp.scss';

.chartContainer {
  background: linear-gradient(135deg, rgba(1, 193, 118, 0.1) 0%, rgba(1, 193, 118, 0.05) 100%);
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pulseAnimation {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

**在组件中使用**：

```typescript
import styles from './index.module.scss'

const AnimatedChartPage: FC = () => {
  return (
    <View className="flex h-screen flex-col">
      <NavHeader title="数据图表" />

      <View className={`flex-1 px-[30px] py-[20px] ${styles.chartContainer}`}>
        <View className={styles.pulseAnimation}>
          {/* 图表内容 */}
        </View>
      </View>
    </View>
  )
}
```

---

## 最佳实践

### 1. 页面命名规范

✅ **推荐**：

- `UserProfilePage`
- `OrderDetailPage`
- `ProductListPage`
- `SettingsPage`

❌ **不推荐**：

- `userProfile` (应该用 PascalCase)
- `order-detail` (不要使用连字符)
- `Page_Product` (不要使用下划线)

### 2. 模块命名规范

✅ **推荐**：

- `wordMemoryModule`
- `examCenterModule`
- `userManagementModule`

❌ **不推荐**：

- `wordMemory` (必须以 Module 结尾)
- `ExamCenterModule` (应该用 camelCase)
- `exam-center-module` (不要使用连字符)

### 3. 类型定义最佳实践

✅ **使用字面量联合类型**：

```typescript
export type TaskStatus = 'pending' | 'in-progress' | 'completed'
```

❌ **避免使用 enum**：

```typescript
enum TaskStatus {
  Pending = 'pending',
  InProgress = 'in-progress',
  Completed = 'completed'
}
```

### 4. 样式书写顺序

1. ✅ 优先使用 TailwindCSS utility classes
2. ✅ 复杂样式使用 CSS Modules
3. ❌ 避免内联样式

```typescript
// ✅ 推荐
<View className="flex items-center gap-[20px] rounded-[16px] bg-white px-[30px] py-[20px]">
  <View className={styles.complexAnimation}>...</View>
</View>

// ❌ 不推荐
<View style={{ display: 'flex', padding: '20px' }}>
  ...
</View>
```

---

## 故障排除

### 问题 1：页面创建后无法访问

**原因**：路由配置可能未生效

**解决方案**：

1. 检查 `src/app.config.ts` 中是否添加了页面路径
2. 重启开发服务器
3. 清除缓存：`rm -rf node_modules/.cache`

### 问题 2：模块页面开发命令不存在

**原因**：package.json 未更新或未安装依赖

**解决方案**：

```bash
# 重新安装依赖
pnpm install

# 验证脚本是否存在
pnpm run dev_blended:examCenterModule
```

### 问题 3：类型导入报错

**原因**：类型文件路径错误或未创建

**解决方案**：

1. 确认类型文件已创建在 `src/types/pages/` 下
2. 检查导入路径是否正确
3. 重启 TypeScript 服务（VSCode: Cmd+Shift+P > Restart TS Server）

### 问题 4：样式不生效

**原因**：TailwindCSS 配置或 CSS Modules 配置问题

**解决方案**：

1. 确认使用正确的类名格式
2. 检查 `tailwind.config.js` 配置
3. CSS Modules 导入方式：`import styles from './index.module.scss'`

---

## 完整工作流示例

### 创建一个完整的任务管理模块

#### Step 1: 创建模块和首页

```bash
/createNewPage TaskHomePage taskManagementModule
```

#### Step 2: 为模块添加更多页面

```bash
/createNewPage TaskListPage taskManagementModule
/createNewPage TaskDetailPage taskManagementModule
/createNewPage TaskCreatePage taskManagementModule
```

#### Step 3: 完善类型定义

编辑 `src/types/pages/TaskDetailPage.ts`：

```typescript
export type TaskStatus = 'todo' | 'in-progress' | 'completed'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  assignee: string
  dueDate: string
  createdAt: string
}

export interface TaskDetailPageParams {
  task_id: string
}
```

#### Step 4: 开发模块

```bash
pnpm run dev_blended:taskManagementModule
```

#### Step 5: 构建模块

```bash
pnpm run build_blended:taskManagementModule
```

---

## 总结

`createNewPage` skill 提供了：

✅ **标准化**：确保所有页面遵循项目规范  
✅ **自动化**：自动生成文件和配置  
✅ **模块化**：支持 blended 模块模式  
✅ **类型安全**：自动创建类型定义  
✅ **文档完善**：自动生成 README 模板

使用此 skill 可以大大提高开发效率，确保代码质量和一致性。
