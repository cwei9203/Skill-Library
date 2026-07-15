---
name: addPageApis
description: 为 react-taro-teacher 页面添加 API 层代码。根据用户提供的接口信息，生成 TypeScript 类型定义、API 函数和可选的 Zustand Store，并更新页面组件引用。支持从 Apifox MCP 自动获取接口详情。用法：/addPageApis <页面名称> [模块名称]
---

# addPageApis — 为页面添加 API 层

根据用户提供的接口信息，为 react-taro-teacher 页面生成完整的 API 层代码，包括 TypeScript 类型定义、API 函数封装和可选的 Zustand Store。

## 使用场景

**触发时机**：
- 用户执行 `/addPageApis` 命令
- `figmaCreatePage` 流程中用户选择提供 API 定义

**命令格式**：`/addPageApis <页面名称> [模块名称]`

**示例**：
```bash
/addPageApis UserProfilePage
/addPageApis TaskDetailPage wordMemoryModule
```

---

## 工作流程

### Step 1：收集接口路径

**向用户提问**：

```
请提供需要接入的接口路径（可提供多个，每行一条）：

例如：
/api/bffhs/v2/dictation/contents
/api/bffhs/teacher/user/info
```

用户只需提供**接口路径**，其余信息（请求方法、参数、响应结构、字段说明）全部通过 Apifox MCP 自动获取。

---

### Step 2：通过 Apifox MCP 获取接口详情

对用户提供的每一条接口路径，执行以下步骤：

#### Step 2.1：查找项目列表

```
使用工具：mcp__apifox-new-mcp__listAccessibleProjects
  - 获取所有可访问的 Apifox 项目
  - 根据项目名称或上下文确定目标项目（通常为蜜蜂家校相关项目）
```

#### Step 2.2：在项目中搜索接口

```
使用工具：mcp__apifox-new-mcp__listOpenApiEndpoints
  - projectId: 从上一步获取
  - 在结果中按 path 匹配用户提供的接口路径
  - 获取对应接口的 apiId
```

#### Step 2.3：获取接口完整定义

```
使用工具：mcp__apifox-new-mcp__getOpenApiDetails
  - projectId: 上一步获取
  - apiId: 上一步匹配到的接口 ID

从返回数据中提取：
  - 请求方法（GET / POST）
  - 请求参数（query params 或 request body 字段及类型）
  - 响应数据结构（字段名、类型、是否必填、说明）
  - 接口描述（用于生成注释）
```

#### Step 2.4：获取引用的数据模型（如有）

如果响应结构中包含 `$ref` 引用（如 `$ref: '#/components/schemas/ContentItem'`）：

```
使用工具：mcp__apifox-new-mcp__getStructureInfo
  - 获取引用的 Schema 定义
  - 递归解析所有嵌套的 $ref
```

#### Step 2.5：接口未找到时的处理

如果在 Apifox 中未找到对应路径的接口：

```
告知用户：未在 Apifox 中找到接口 {path}，请确认路径是否正确。
可选操作：
  1. 提供正确的接口路径重试
  2. 提供 Apifox 接口链接直接定位
  3. 跳过此接口
```

---

### Step 3：生成 TypeScript 类型定义

#### 文件路径规则

- 优先追加到已存在的模块类型文件：`src/types/api/{module}-api.ts`
- 若不存在则新建
- 模块名从页面名或模块参数推断（如 `TaskDetailPage` + `wordMemoryModule` → `word-memory-api.ts`）

#### 生成规范

```typescript
// src/types/api/{module}-api.ts

/** 获取用户详情 - 请求参数 */
export interface GetUserInfoParams {
  /** 用户 ID */
  user_id: string
}

/** 获取用户详情 - 响应数据 */
export interface GetUserInfoResponse {
  /** 用户名 */
  name: string
  /** 头像 URL */
  avatar: string
  // TODO: 从 Apifox 补充其他字段
}
```

**类型命名规范**：
- 请求参数：`{动词}{资源名}Params` 或 `{动词}{资源名}Request`
- 响应数据：`{动词}{资源名}Response` 或 `{动词}{资源名}Data`
- 列表响应：包含 `list`、`total`、`page`、`page_size` 等标准分页字段
- **禁止使用 `enum`**，使用字面量联合类型：`type Status = 'active' | 'inactive'`

---

### Step 4：生成 API 函数

#### 文件路径规则

- 优先追加到已存在的模块 API 文件：`src/api/{module}-api.ts`
- 若不存在则新建
- 文件命名用 kebab-case：`word-memory-api.ts`、`user-profile-api.ts`

#### 生成规范

```typescript
// src/api/{module}-api.ts

import { requestWithNewUrl } from '@/server/request2'
import type { GetUserInfoParams, GetUserInfoResponse } from '@/types/api/{module}-api'

/**
 * 获取用户详情
 * @doc {Apifox链接（如有）}
 */
export function getUserInfo(params: GetUserInfoParams): Promise<GetUserInfoResponse> {
  return requestWithNewUrl({
    url: '/api/bffhs/teacher/user/info',
    method: 'GET',
    data: params
  })
}
```

**函数命名规范**：
- GET 查询：`get{资源名}`、`fetch{资源名}List`
- POST 创建：`create{资源名}`
- POST 更新：`update{资源名}`
- POST 删除：`delete{资源名}`
- POST 提交：`submit{资源名}`

**请求方法选择**：
- `requestWithNewUrl` — 新接口（`/api/bffhs/` 路径）【首选】
- `get` / `post` from `@/server/server` — 旧接口（`H5/teacher/` 路径）

---

### Step 5：（可选）生成 Zustand Store

**触发条件**：当接口数量 ≥ 2，或页面有明显的共享状态需求时，询问用户：

```
是否需要生成 Zustand Store 来管理页面状态？
（适用于：多个组件共享数据、复杂的状态联动）
```

若用户同意，生成：

```typescript
// src/store/use{PageName}Store.ts

import { create } from 'zustand'
import type { GetUserInfoResponse } from '@/types/api/{module}-api'

type State = {
  userInfo: GetUserInfoResponse | null
  loading: boolean
}

type Actions = {
  setUserInfo: (info: GetUserInfoResponse | null) => void
  setLoading: (loading: boolean) => void
  reset{PageName}Store: () => void
}

const initialState: State = {
  userInfo: null,
  loading: false
}

const use{PageName}Store = create<State & Actions>()(set => ({
  ...initialState,
  setUserInfo: info => set({ userInfo: info }),
  setLoading: loading => set({ loading }),
  reset{PageName}Store: () => set(initialState)
}))

export default use{PageName}Store
```

---

### Step 6：更新页面组件

在页面 `src/pages/{PageName}/index.tsx` 中：

1. 添加 API 函数导入
2. 添加类型导入
3. 在 `loadData` 函数中调用 API（替换原来的 `// TODO: 加载数据`）
4. 如果生成了 Store，添加 Store 导入和使用

**更新前（createNewPage 生成的默认代码）**：

```typescript
// index.tsx（更新前）
const loadData = async () => {
  setLoading(true)
  try {
    // TODO: 加载数据
  } catch (error) {
    Taro.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    setLoading(false)
  }
}
```

**更新后**：

```typescript
// index.tsx（更新后）
import { getUserInfo } from '@/api/{module}-api'
import type { GetUserInfoResponse } from '@/types/api/{module}-api'

const [userInfo, setUserInfo] = useState<GetUserInfoResponse | null>(null)

const loadData = async () => {
  setLoading(true)
  try {
    const result = await getUserInfo({ user_id: params.userId ?? '' })
    setUserInfo(result)
  } catch {
    Taro.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    setLoading(false)
  }
}
```

---

### Step 7：反馈结果

告知用户以下内容：

**生成/更新的文件**：
- ✅ `src/types/api/{module}-api.ts`（新建 或 追加 N 个类型）
- ✅ `src/api/{module}-api.ts`（新建 或 追加 N 个函数）
- ✅ `src/store/use{PageName}Store.ts`（如生成）
- ✅ `src/pages/{PageName}/index.tsx`（已更新 loadData）

**接口清单**：

| 函数名 | 路径 | 方法 | 说明 |
|--------|------|------|------|
| `getUserInfo` | `/api/bffhs/teacher/user/info` | GET | 获取用户详情 |

**注意事项**：
- ⚠️ 类型字段可能不完整，建议对照 Apifox 文档补充
- ⚠️ 错误处理仅为基础实现，按需完善

---

## 代码规范检查清单

### ✅ 类型定义
- [ ] 所有 interface 字段有 JSDoc 注释
- [ ] 不使用 `enum`，使用字面量联合类型
- [ ] 使用 `import type` 导入类型
- [ ] 响应类型包含正确的嵌套结构

### ✅ API 函数
- [ ] 函数有 JSDoc 注释（包含 `@doc` 链接，如有）
- [ ] 请求参数和返回值都有完整类型定义
- [ ] 使用 `requestWithNewUrl` 还是旧版 `get/post` 选择正确
- [ ] 函数命名符合 `{动词}{资源名}` 规范

### ✅ 页面更新
- [ ] 导入语句使用 `import type` 导入类型
- [ ] `loadData` 中有正确的错误处理
- [ ] 状态变量类型明确（非 `any`）
- [ ] 参数取值有空值保护（`?? ''` 或 `?? undefined`）

---

## 与其他 Skill 的关系

- **figmaCreatePage**：在 Step 4（createNewPage）完成后，可选调用此 skill 为页面添加 API 层
- **addPageInteractions**：（未来）补充页面交互逻辑，两者独立但可组合使用

---

## 常见问题

### Q: 接口路径用 `/api/bffhs/` 还是 `H5/teacher/`？
A: 新接口统一用 `/api/bffhs/` 路径，使用 `requestWithNewUrl`。旧接口如 `H5/teacher/` 使用 `get`/`post`。如不确定，使用 `requestWithNewUrl` 并留注释。

### Q: 从 Apifox 获取了类型但字段不完整怎么办？
A: 生成的类型字段会标注 `// TODO:` 注释，开发者需要对照 Apifox 文档手动补全。

### Q: 已有同名 API 文件，会覆盖吗？
A: 不会覆盖，只会在文件末尾追加新的类型和函数。追加前会检查同名函数是否已存在，避免重复。

### Q: 不需要 Store 但想手动管理状态可以吗？
A: 可以，Step 5 是可选的。不生成 Store 时，状态通过页面级 `useState` 管理（已在 Step 6 中体现）。
