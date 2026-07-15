# figmaCreatePage Skill

从 Figma 设计一步到位创建符合项目规范的页面。

## 📋 功能概述

整合 figma-mcp、figmaToTaroPage 和 createNewPage 三个流程，一键创建完整页面。

- ✅ **从 Figma 获取设计** - 自动解析 Figma 设计稿
- ✅ **自动尺寸转换（x2）** - 所有尺寸自动乘以 2
- ✅ **组件智能映射** - 优先使用项目已有组件
- ✅ **完整文件结构** - 创建页面文件、类型定义、样式文件
- ✅ **自动配置路由** - 更新 app.config.ts 或 modulePagesConfig.ts

## 🚀 快速开始

### 基础用法

```bash
# 创建普通页面
/figmaCreatePage <Figma URL> UserProfilePage

# 创建模块页面
/figmaCreatePage <Figma URL> TaskDetailPage wordMemoryModule

# 创建新模块和页面
/figmaCreatePage <Figma URL> HomePage examModule
```

### Figma URL 格式

```
https://figma.com/design/:fileKey/:fileName?node-id=1-2
```

## 🎯 工作流程

```
1. 用户提供 Figma URL 和页面名称
   ↓
2. 从 Figma 获取设计（figma-implement-design）
   ↓
3. 应用转换规则（figmaToTaroPage）
   - 尺寸 x2
   - 组件映射
   ↓
4. 创建文件结构（createNewPage）
   - 页面文件
   - 类型定义
   - 样式文件
   - 路由配置
   ↓
5. 输出完整页面代码
```

## 📁 生成的文件结构

```
src/
├── pages/
│   └── UserProfilePage/
│       ├── index.tsx              # 页面组件
│       └── index.module.scss      # 样式文件（如有）
└── types/
    └── pages/
        └── UserProfilePage.ts     # 类型定义

# 如为模块页面，还会更新：
├── .env.development_blended_examModule   # 模块环境配置（新模块）
├── .env.production_blended_examModule    # 模块环境配置（新模块）
├── src/modulePagesConfig.ts              # 模块配置
└── package.json                          # 开发脚本（新模块）
```

## 📖 使用文档

- **[SKILL.md](./SKILL.md)** - 完整的 skill 规范和工作流程
- **[QUICK_START.md](./QUICK_START.md)** - 快速参考指南

## ✅ 自动应用的规则

### 尺寸转换（x2）

| Figma 值 | TailwindCSS | 说明        |
| -------- | ----------- | ----------- |
| 8px      | `[16px]`    | 小间距 x2   |
| 15px     | `[30px]`    | 标准间距 x2 |
| 12px     | `[24px]`    | 小字号 x2   |
| 14px     | `[28px]`    | 正文字号 x2 |

### 必备组件

- ✅ `<NavHeader>` - 导航栏
- ✅ `DetailLoginHOC` - 登录验证
- ✅ `<SafeArea>` - 底部安全区域

## 🔍 使用示例

### 示例 1：创建普通页面

**命令**：

```bash
/figmaCreatePage https://figma.com/design/xxx/UserProfile?node-id=10-5 UserProfilePage
```

**结果**：

```
✅ 页面创建成功！

创建的文件：
  - src/pages/UserProfilePage/index.tsx
  - src/types/pages/UserProfilePage.ts

路由配置：
  - 路径：/pages/UserProfilePage/index

已应用规则：
  ✅ 所有尺寸 x2
  ✅ 主题色适配
  ✅ 添加必备组件
```

### 示例 2：创建模块页面

**命令**：

```bash
/figmaCreatePage https://figma.com/design/xxx/TaskDetail?node-id=20-10 TaskDetailPage wordMemoryModule
```

**结果**：

```
✅ 模块页面创建成功！

创建的文件：
  - src/pages/TaskDetailPage/index.tsx
  - src/types/pages/TaskDetailPage.ts

模块配置：
  - 模块：wordMemoryModule
  - 已更新：src/modulePagesConfig.ts

开发命令：
  pnpm run dev_blended:wordMemoryModule
```

### 示例 3：创建新模块

**命令**：

```bash
/figmaCreatePage https://figma.com/design/xxx/ExamHome?node-id=30-15 ExamHomePage examModule
```

**结果**：

```
✅ 新模块和页面创建成功！

创建的文件：
  - src/pages/ExamHomePage/index.tsx
  - src/types/pages/ExamHomePage.ts
  - .env.development_blended_examModule
  - .env.production_blended_examModule

模块配置：
  - 新模块：examModule
  - 已更新配置文件

开发命令：
  pnpm run dev_blended:examModule
```

## 🐛 常见问题

### Q: 尺寸不对？

A: 应该是 Figma 的 2 倍。检查是否正确应用了 x2 规则。

### Q: 如何修改生成的页面？

A: 直接编辑 `src/pages/{PageName}/index.tsx` 文件。

### Q: 可以为同一模块创建多个页面吗？

A: 可以。多次运行命令，指定相同模块名称即可。

## 🔗 与其他 Skill 的关系

此 skill 整合了以下流程：

- **figma-implement-design** - 从 Figma 获取设计
- **figmaToTaroPage** - 应用转换规则
- **createNewPage** - 创建文件和配置

**优势**：一个命令完成全部流程，无需手动调用多个 skill。

---

**版本**: 1.0.0  
**最后更新**: 2026-04-01
