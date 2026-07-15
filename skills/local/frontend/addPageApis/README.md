# addPageApis

为 react-taro-teacher 页面添加完整的 API 层代码。

## 功能

- 根据接口路径/Apifox 链接生成 TypeScript 类型定义
- 生成符合项目规范的 API 函数封装
- 可选生成 Zustand Store
- 自动更新页面组件的 `loadData` 函数

## 用法

```bash
/addPageApis <页面名称> [模块名称]
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `src/types/api/{module}-api.ts` | TypeScript 类型定义 |
| `src/api/{module}-api.ts` | API 函数封装 |
| `src/store/use{PageName}Store.ts` | Zustand Store（可选） |
| `src/pages/{PageName}/index.tsx` | 页面组件（更新 loadData） |

## 与 figmaCreatePage 集成

在 `figmaCreatePage` 流程中，Step 4（createNewPage）完成后会询问是否添加 API 定义，选择"是"时自动触发此 skill。

## 详细文档

见 [SKILL.md](./SKILL.md)
