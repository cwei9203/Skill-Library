# figmaCreatePage Skill - 快速开始

> 从 Figma 设计一步到位创建页面

## 🎯 核心用法

```bash
/figmaCreatePage <Figma URL> <页面名称> [模块名称]
```

就这么简单！一个命令完成从 Figma 设计到项目页面的完整创建。

## 📝 三种使用场景

### 1️⃣ 创建普通页面

```bash
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 UserProfilePage
```

**自动完成**：

- ✅ 从 Figma 获取设计
- ✅ 尺寸 x2 转换
- ✅ 创建页面文件
- ✅ 创建类型定义
- ✅ 配置路由

**访问路径**：`/pages/UserProfilePage/index`

---

### 2️⃣ 创建模块页面

```bash
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 TaskDetailPage wordMemoryModule
```

**自动完成**：

- ✅ 从 Figma 获取设计
- ✅ 尺寸 x2 转换
- ✅ 创建页面文件
- ✅ 更新模块配置

**开发命令**：`pnpm run dev_blended:wordMemoryModule`

---

### 3️⃣ 创建新模块

```bash
/figmaCreatePage https://figma.com/design/xxx/MyDesign?node-id=42-15 HomePage examModule
```

**自动完成**：

- ✅ 从 Figma 获取设计
- ✅ 创建模块环境配置
- ✅ 创建页面文件
- ✅ 配置模块路由
- ✅ 更新 package.json 脚本

**开发命令**：`pnpm run dev_blended:examModule`

---

## 🔍 工作流程

```
Figma 设计
   ↓
figma-implement-design（获取设计）
   ↓
figmaToTaroPage（应用规则）
   - 尺寸 x2
   - 主题色适配
   - 组件映射
   ↓
createNewPage（创建文件）
   - 页面文件
   - 类型定义
   - 路由配置
   ↓
完整页面代码
```

## 📋 自动应用的规则

### 尺寸转换（x2）

| Figma | 自动转换      |
| ----- | ------------- |
| 8px   | `[16px]`      |
| 15px  | `[30px]`      |
| 12px  | `text-[24px]` |
| 14px  | `text-[28px]` |

### 必备组件

- ✅ `<NavHeader>` - 导航栏
- ✅ `DetailLoginHOC` - 登录验证
- ✅ 项目组件（如 `<BlockButton>`）

## 💡 实际示例

### 示例：创建按钮页面

**Figma 设计**：

- 按钮宽度：343px
- 按钮高度：44px
- 按钮圆角：8px
- 按钮背景：#21b874
- 文字大小：16px

**命令**：

```bash
/figmaCreatePage https://figma.com/design/xxx/ButtonPage?node-id=1-2 ConfirmPage
```

**生成的代码**：

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
      {/* ⭐ 自动添加导航栏 */}
      <NavHeader title="确认页面" />

      {/* ✅ 自动使用项目组件 BlockButton */}
      {/* ✅ 按钮自动应用主题色 */}
      <View className="flex-1 px-[30px] py-[30px]">
        <BlockButton onClick={handleConfirm} >确认</BlockButton>
      </View>
    </View>
  )
}

// ⭐ 自动添加登录验证 HOC
export default DetailLoginHOC(ConfirmPage)
```

**转换说明**：

- 343px → 使用 `<BlockButton>` 组件（自动处理）
- 44px → 使用 `<BlockButton>` 组件（自动处理）
- 8px → 组件内部处理
- #21b874 → `bg-primary`（组件内部）
- 16px → 组件内部处理
- 内边距 15px → 30px (**x2**)

---

## ✅ 快速验证

生成后检查：

```bash
✅ 所有尺寸是 Figma 的 2 倍
✅ 主题色使用了 primary 类名
✅ 页面包含 <NavHeader> 组件
✅ 页面使用 DetailLoginHOC 包裹
✅ 类型文件在 src/types/pages/
✅ 路由已配置
✅ 无 TypeScript 错误
```

## 🚨 常见错误

### 错误 1：忘记提供 Figma URL

```bash
❌ /figmaCreatePage UserProfilePage
✅ /figmaCreatePage https://figma.com/design/xxx/... UserProfilePage
```

### 错误 2：页面名称格式错误

```bash
❌ /figmaCreatePage https://... userProfilePage  # 小驼峰
❌ /figmaCreatePage https://... user-profile-page  # 短横线
✅ /figmaCreatePage https://... UserProfilePage  # 大驼峰（PascalCase）
```

### 错误 3：模块名称格式错误

```bash
❌ /figmaCreatePage https://... Page WordMemory  # 没有 Module 后缀
❌ /figmaCreatePage https://... Page word-memory-module  # 短横线
✅ /figmaCreatePage https://... Page wordMemoryModule  # 小驼峰 + Module 后缀
```

## 📞 常见问题

**Q: 这个 skill 和 figma-implement-design 有什么区别？**

A: `figma-implement-design` 只生成代码，不会自动应用项目规则。`figmaCreatePage` 整合了获取设计、应用规则、创建文件三个流程，一步到位。

**Q: 生成后可以修改吗？**

A: 可以。直接编辑 `src/pages/{PageName}/index.tsx` 文件即可。

**Q: 尺寸为什么要 x2？**

A: 项目设计稿基于 750px 宽度，编译时 Taro 自动 2:1 转换（1px = 2rpx）。

**Q: 主题色为什么要用 primary？**

A: 项目支持多端，微信用绿色（#21b874），H5 用蓝色（#1890ff）。只有这 4 个颜色值（#1890ff、#21b874、#e6f7f0、#edf6ff）使用 `primary` 类名，其他颜色保持固定色值。

**Q: 可以为同一模块创建多个页面吗？**

A: 可以。多次运行命令，指定相同模块名称即可。

**Q: 如何删除创建的页面？**

A: 手动删除文件并更新路由配置即可。

## 🎉 开始使用

现在你已经了解了基础用法，开始从 Figma 创建你的第一个页面吧！

```bash
/figmaCreatePage <你的Figma链接> MyFirstPage
```

Happy coding! 🚀

---

**查看完整文档**：

- [SKILL.md](./SKILL.md) - 完整规范
- [README.md](./README.md) - 功能概览

**版本**: 1.0.0  
**最后更新**: 2026-04-01
