# createNewPage Skill - 快速开始

> 5 分钟快速上手 createNewPage skill

## 🎯 核心用法

### 最简单的用法

```bash
/createNewPage MyPage
```

就这么简单！这会创建一个完全符合项目规范的页面。

## 📝 三种使用场景

### 1️⃣ 创建普通页面

**命令**：

```bash
/createNewPage UserProfilePage
```

**结果**：

- ✅ 创建页面文件
- ✅ 创建类型定义
- ✅ 配置路由

**访问路径**：`/pages/UserProfilePage/index`

---

### 2️⃣ 为现有模块添加页面

**命令**：

```bash
/createNewPage TestPage wordMemoryModule
```

**结果**：

- ✅ 创建页面文件
- ✅ 创建类型定义
- ✅ 更新模块配置

**开发命令**：

```bash
pnpm run dev_blended:wordMemoryModule
```

---

### 3️⃣ 创建新模块及首页

**命令**：

```bash
/createNewPage HomePage examModule
```

**结果**：

- ✅ 创建模块配置
- ✅ 创建环境配置
- ✅ 创建页面文件
- ✅ 创建类型定义
- ✅ 更新路由和脚本

**开发命令**：

```bash
pnpm run dev_blended:examModule
```

## 🎨 生成的页面包含什么？

### 页面文件（index.tsx）

```typescript
✅ React FC 组件
✅ NavHeader 导航栏
✅ DetailLoginHOC 包裹
✅ useMount 首次加载
✅ usePageLog 埋点
✅ TailwindCSS 样式
✅ 完整 TypeScript 类型
```

### 类型定义（types/pages/{PageName}.ts）

```typescript
✅ 路由参数类型
✅ 数据模型类型
✅ 字面量联合类型（不使用 enum）
```

### 样式文件（index.module.scss）

```scss
✅ CSS Modules 配置
✅ 导入项目变量
✅ 注释说明用法
```

### 文档文件（README.md）

```markdown
✅ 页面概述
✅ 技术栈说明
✅ 功能特性列表
✅ 项目规范遵循清单
```

## 📋 命名规范速查

### ✅ 正确的命名

#### 页面名称（PascalCase）

```
UserProfilePage ✅
OrderDetailPage ✅
ProductListPage ✅
SettingsPage ✅
```

#### 模块名称（camelCase + Module 后缀）

```
wordMemoryModule ✅
examCenterModule ✅
userManagementModule ✅
```

### ❌ 错误的命名

#### 页面名称

```
userProfile ❌ (应该用 PascalCase)
User-Profile ❌ (不要用连字符)
user_profile_page ❌ (不要用下划线)
```

#### 模块名称

```
wordMemory ❌ (必须以 Module 结尾)
WordMemoryModule ❌ (应该用 camelCase)
word-memory-module ❌ (不要用连字符)
```

## 🚀 创建后的下一步

### 1. 开发页面

```bash
# 普通页面
pnpm run dev:h5

# 模块页面
pnpm run dev_blended:moduleName
```

### 2. 完善功能

- 实现数据加载逻辑
- 添加交互功能
- 完善 UI 样式

### 3. 更新类型

编辑 `src/types/pages/{PageName}.ts`：

```typescript
// 添加业务类型
export type Status = 'active' | 'inactive'

export interface DataItem {
  id: string
  name: string
  status: Status
}
```

### 4. 添加埋点

```typescript
const handleClick = () => {
  Log?.action('button_click', {
    button_name: 'submit'
  })
  // 处理逻辑
}
```

### 5. 完善样式

```typescript
// TailwindCSS（优先）
<View className="flex items-center gap-[20px] rounded-[16px] bg-white px-[30px]">
  ...
</View>

// CSS Modules（复杂样式）
<View className={styles.complexAnimation}>
  ...
</View>
```

## 💡 常用模式

### 带参数的页面

```typescript
// 类型定义
export interface DetailPageParams {
  id: string
  type?: 'edit' | 'view'
}

// 页面组件
const DetailPage: FC = () => {
  const params = useParams() as DetailPageParams

  useMount(() => {
    loadData(params.id)
  })
}
```

### 列表页面

```typescript
const [list, setList] = useState<DataItem[]>([])
const [loading, setLoading] = useState(false)

const loadList = async () => {
  setLoading(true)
  try {
    const data = await fetchList()
    setList(data)
  } finally {
    setLoading(false)
  }
}

useMount(() => {
  loadList()
})
```

### 表单页面

```typescript
const [formData, setFormData] = useState({
  name: '',
  email: ''
})

const handleSubmit = async () => {
  // TODO: action 埋点待开发者按需补充
  // Log?.uploadWeEvent('form_submit')
  try {
    await submitForm(formData)
    Taro.showToast({ title: '提交成功', icon: 'success' })
    navigateBackEnhance({ delta: 1 })
  } catch (error) {
    Taro.showToast({ title: '提交失败', icon: 'none' })
  }
}
```

## 🔍 快速检查清单

创建页面后，快速检查：

```bash
✅ 文件已创建在 src/pages/{PageName}/
✅ 类型文件已创建在 src/types/pages/{PageName}.ts
✅ 路由已配置（app.config.ts 或 modulePagesConfig.ts）
✅ 无 TypeScript 错误
✅ 无 ESLint 错误
✅ 可以访问页面
```

## 📞 需要帮助？

### 查看完整文档

- **[SKILL.md](./SKILL.md)** - 完整规范和工作流程
- **[EXAMPLES.md](./EXAMPLES.md)** - 详细示例和最佳实践
- **[README.md](./README.md)** - skill 概览和功能介绍

### 常见问题

**Q: 如何知道应该创建普通页面还是模块页面？**

A:

- 主包业务 → 普通页面
- 独立模块业务 → 模块页面
- 新业务模块 → 创建新模块

**Q: 页面创建后可以直接运行吗？**

A: 可以，但需要运行相应的开发命令：

- 普通页面：`pnpm run dev:h5`
- 模块页面：`pnpm run dev_blended:moduleName`

**Q: 如何修改生成的页面？**

A: 直接编辑生成的文件即可：

- 页面逻辑：`src/pages/{PageName}/index.tsx`
- 类型定义：`src/types/pages/{PageName}.ts`
- 样式：`src/pages/{PageName}/index.module.scss`

## 🎉 开始使用

现在你已经了解了基础用法，开始创建你的第一个页面吧！

```bash
/createNewPage MyFirstPage
```

Happy coding! 🚀
