# addPageApis — 快速上手

## 最简用法

```bash
/addPageApis UserProfilePage
```

执行后，只需提供接口路径：

```
请提供需要接入的接口路径（可提供多个，每行一条）：

/api/bffhs/teacher/user/info
/api/bffhs/teacher/user/update
```

系统会自动通过 **Apifox MCP** 查询接口定义，获取请求参数、响应结构和字段说明，无需手动填写。

## 提供多个接口

```
/api/bffhs/v2/dictation/contents
/api/bffhs/v2/dictation/content/add
/api/bffhs/v2/dictation/content/delete
```

每条路径都会自动从 Apifox 获取完整定义，批量生成类型和 API 函数。

## 配合 figmaCreatePage 使用

在执行 `/figmaCreatePage` 创建页面时，流程会自动询问：

```
✅ 页面文件已创建完成。

是否需要为此页面添加 API 定义？
- 输入接口信息，自动生成 API 函数和类型定义
- 直接回车跳过，后续可单独执行 /addPageApis
```
