# createNewPage Skill

为 react-taro-teacher 项目创建标准化新页面的 Claude Code skill。

## 📋 功能概述

此 skill 提供自动化的页面创建流程，确保所有新页面都符合项目规范，包括：

- ✅ 自动生成标准页面文件（React 组件、样式、文档）
- ✅ 自动创建 TypeScript 类型定义
- ✅ 自动配置路由
- ✅ 支持 blended 模块模式
- ✅ 自动创建模块环境配置（如果是新模块）
- ✅ 遵循项目最新规范（TailwindCSS、useMount、类型定义等）

## 🚀 快速开始

### 创建普通页面

```bash
/createNewPage UserProfilePage
```

这将创建：

- `src/pages/UserProfilePage/index.tsx` - 页面组件
- `src/pages/UserProfilePage/index.module.scss` - 样式文件
- `src/pages/UserProfilePage/README.md` - 文档
- `src/types/pages/UserProfilePage.ts` - 类型定义
- 更新 `src/app.config.ts` - 路由配置

### 创建模块页面

```bash
/createNewPage TaskDetailPage wordMemoryModule
```

这将额外：

- 更新 `src/modulePagesConfig.ts` - 模块配置
- 如果是新模块，创建环境配置文件
- 配置模块路由

## 📖 使用方法

### 语法

```bash
/createNewPage <页面名称> [模块名称]
```

### 参数说明

- **页面名称**（必需）

  - 格式：PascalCase
  - 示例：`UserProfilePage`、`OrderDetailPage`
  - 说明：页面组件的名称

- **模块名称**（可选）
  - 格式：camelCase，必须以 `Module` 结尾
  - 示例：`wordMemoryModule`、`examCenterModule`
  - 说明：blended 模块的名称

### 使用场景

| 场景               | 命令                                       | 说明                        |
| ------------------ | ------------------------------------------ | --------------------------- |
| 创建主包页面       | `/createNewPage ProfilePage`               | 在 pages 目录下创建普通页面 |
| 为现有模块添加页面 | `/createNewPage TestPage wordMemoryModule` | 添加到已存在的模块          |
| 创建新模块及首页   | `/createNewPage HomePage examModule`       | 创建新模块配置和首个页面    |

## 📁 生成的文件结构

### 普通页面

```
src/
├── pages/
│   └── UserProfilePage/
│       ├── index.tsx              # 页面组件
│       ├── index.module.scss      # 样式文件
│       └── README.md              # 文档
└── types/
    └── pages/
        └── UserProfilePage.ts     # 类型定义
```

### 新模块页面

```
.env.development_blended_examModule    # 开发环境配置
.env.production_blended_examModule     # 生产环境配置

src/
├── pages/
│   └── HomePage/
│       ├── index.tsx
│       ├── index.module.scss
│       └── README.md
├── types/
│   └── pages/
│       └── HomePage.ts
├── modulePagesConfig.ts               # 更新：添加模块配置
└── app.config.ts                      # 更新：导入模块
```

## 🎯 项目规范遵循

此 skill 生成的页面完全遵循项目最新规范：

### 1. 生命周期规范

```typescript
import { useMount } from 'ahooks'

const PageName: FC = () => {
  useMount(() => {
    // ⭐ 首次加载逻辑（不使用 useLoad）
  })

  // ❌ useDidShow 可选，默认不提供
}
```

### 2. HOC 使用规范

```typescript
import DetailLoginHOC from '@/components/DetailLoginHOC'
import { NavHeader } from '@/components/NavHeader'

const PageName: FC = () => {
  return (
    <View>
      {/* ⭐ NavHeader 必须在最顶部 */}
      <NavHeader title="页面标题" />
      {/* 页面内容 */}
    </View>
  )
}

// ⭐ 必须用 DetailLoginHOC 包裹
export default DetailLoginHOC(PageName)
```

### 3. 样式规范

```typescript
// ✅ 优先使用 TailwindCSS utility classes
<View className="flex flex-col gap-[20px] rounded-[16px] bg-white px-[30px] py-[20px]">
  {/* 内容 */}
</View>

// ✅ 复杂样式使用 CSS Modules
import styles from './index.module.scss'
<View className={styles.complexAnimation}>
  {/* 内容 */}
</View>
```

### 4. 类型定义规范

```typescript
// ✅ 类型定义在独立文件中
// src/types/pages/PageName.ts

// ✅ 使用字面量联合类型（不使用 enum）
export type Status = 'pending' | 'active' | 'completed'

// ✅ 使用 import type 导入
import type { Status } from '@/types/pages/PageName'
```

## 📚 相关文档

- **[SKILL.md](./SKILL.md)** - 完整的 skill 规范和工作流程
- **[EXAMPLES.md](./EXAMPLES.md)** - 详细使用示例和最佳实践
- **[项目 CLAUDE.md](/Users/youbao_feng/workspace/react-taro-teacher/CLAUDE.md)** - 项目完整规范

## ✅ 功能特性

### 自动化功能

- ✅ 页面文件生成（React 组件、样式、文档）
- ✅ TypeScript 类型定义生成
- ✅ 路由自动配置
- ✅ 模块配置自动创建/更新
- ✅ 环境配置文件生成（新模块）
- ✅ package.json 脚本更新（新模块）

### 规范检查

- ✅ 页面名称格式验证（PascalCase）
- ✅ 模块名称格式验证（camelCase + Module 后缀）
- ✅ 页面重复性检查
- ✅ 模块存在性检查

### 代码质量

- ✅ 符合项目 ESLint 规范
- ✅ 完整的 TypeScript 类型定义
- ✅ 遵循 Prettier 格式化规则
- ✅ 代码注释和文档

## 🔧 技术实现

### 生成的页面模板

页面模板包含以下核心部分：

1. **导入声明**：必需的依赖和类型
2. **组件定义**：标准 React FC 组件
3. **状态管理**：useState 定义
4. **生命周期**：useMount 首次加载
5. **事件处理**：标准事件处理函数
6. **渲染逻辑**：包含 NavHeader 和 SafeArea
7. **HOC 包裹**：DetailLoginHOC 导出

### 类型定义模板

类型定义包含：

1. **路由参数类型**：`{PageName}Params`
2. **数据模型类型**：业务数据结构
3. **组件 Props 类型**：子组件属性
4. **联合类型**：字面量联合类型（不使用 enum）

### 模块配置模板

模块配置包含：

1. **模块名称常量**：`{moduleName}Name`
2. **页面列表常量**：`{moduleName}Pages`
3. **环境配置**：`.env.development_blended_{moduleName}`
4. **构建脚本**：`dev_blended:{moduleName}`

## 🐛 故障排除

### 常见问题

1. **页面创建后无法访问**

   - 检查路由配置是否更新
   - 重启开发服务器
   - 清除缓存

2. **类型导入报错**

   - 确认类型文件已创建
   - 检查导入路径
   - 重启 TypeScript 服务

3. **模块开发命令不存在**

   - 运行 `pnpm install`
   - 检查 package.json 是否更新

4. **样式不生效**
   - 确认 TailwindCSS 配置
   - 检查 CSS Modules 导入
   - 验证类名格式

详细解决方案请参考 [EXAMPLES.md](./EXAMPLES.md#故障排除)

## 📝 更新日志

### 2026-04-01 - v1.0.0

- ✅ 初始版本发布
- ✅ 支持创建普通页面
- ✅ 支持创建模块页面
- ✅ 自动生成类型定义
- ✅ 自动配置路由
- ✅ 完整的文档和示例

## 🤝 贡献指南

如果需要改进此 skill，请：

1. 确保生成的代码符合最新项目规范
2. 更新相关文档（SKILL.md、EXAMPLES.md）
3. 添加新的使用示例
4. 测试各种使用场景

## 📄 许可证

此 skill 是 react-taro-teacher 项目的一部分，遵循项目许可证。

---

**作者**: Claude Code  
**版本**: 1.0.0  
**最后更新**: 2026-04-01
