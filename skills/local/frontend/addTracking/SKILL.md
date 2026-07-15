---
name: addTracking
description: 从埋点平台（ids.intsig.net/trackManage/develop）自动读取待开发埋点，解析 pageId/actionId/参数，然后自动在对应页面代码中写入 usePageLog 和 Log.action 埋点代码。遇到无法确定的插入位置或参数来源时暂停询问用户。触发时机：用户说"添加埋点"、"加埋点"、"实现埋点"、"做埋点"、"把埋点做了"、"处理埋点"，或执行 /addTracking。
---

# addTracking — 从埋点平台读取并自动实现埋点代码

读取埋点管理平台的待开发列表，解析出每条埋点的 pageId、actionId、参数，然后直接在项目代码中写入对应的埋点调用。遇到不确定的地方会暂停问你。

## 工作流程

### Step 1：打开埋点平台并获取数据

```
mcp__playwright__browser_navigate → https://ids.intsig.net/trackManage/develop
```

如果页面 URL 包含 `web-sso.intsig.net/login`，说明需要登录：
- 告诉用户"需要先登录 SSO，登录完告诉我"
- 用户确认后重新 navigate

页面加载成功后（title 包含"埋点开发"），用 `mcp__playwright__browser_snapshot` 读取表格。

### Step 2：解析表格数据

表格快照的结构是嵌套的 row/cell。每条**主记录**的 row 包含完整字段：

```
row 格式（主记录）:
- cell: 序号 + container 图标
- cell: 平台（"小程序 小程序" = 上传平台 + 开发平台）
- cell: 描述 + 截图
- cell: 需求ID
- cell: 埋点类型（pageview / actionlog）
- cell: PageID + 中文名（pageId 在 generic[ref] 中，pageIdZh 在下一个 generic 中）
- cell: ActionID + 中文名（同上模式，actionId + actionIdZh）
- cell: 附加参数 key + 中文名
- cell: 参数类型（枚举值 / 任意值）
- cell: 参数 value + 中文名
- cell: 版本号
- cell: 状态（待开发 / 已发布）
- cell: 开发者
- cell: 测试者
```

**container 展开行**（只有部分 cell 有内容）属于上一条主记录的参数枚举值。识别方式：
- 没有"平台"、"描述"、"需求ID"、"埋点类型"、"PageID" 等字段
- 只有 value + valueZh 或 key + keyZh
- 合并到前一条主记录的参数列表中

**解析产出**：每条埋点记录包含：
```
{
  type: 'pageview' | 'actionlog',
  pageId: string,
  pageIdZh: string,
  actionId: string | null,
  actionIdZh: string | null,
  description: string,        // 触发条件描述
  requirement: string,        // 需求名
  params: Array<{
    key: string,
    keyZh: string,
    valueType: '枚举值' | '任意值',
    enumValues: Array<{value: string, valueZh: string}>  // 枚举值列表
  }>
}
```

### Step 3：展示解析结果（必须等用户确认才继续）

**在写任何代码之前，必须先把解析结果展示给用户看，等用户明确说"确认"/"可以"/"没问题"后才进入 Step 4。** 这一步不能跳过。

按需求分组展示：

```
📊 解析结果 — {需求名}（共 N 条）

【页面曝光 pageview】
| # | PageID | 中文 | 描述 |
|---|--------|------|------|
| 1 | ... | ... | ... |

【行为埋点 actionlog】
| # | PageID | ActionID | 中文 | 描述 | 参数 |
|---|--------|----------|------|------|------|
| 2 | ... | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... | ... |

以上解析是否正确？要处理哪些？（全部 / 指定序号 / 有修正）
```

等用户确认后才进入 Step 4。如果用户指出解析有误，先修正再重新展示。

### Step 4：定位页面文件

对每个 pageId，在项目中找到对应页面：

```bash
grep -rn "pageId值" src/pages --include="*.tsx" --include="*.ts"
```

- **找到了**：该文件就是目标页面
- **没找到**：根据 pageIdZh 搜索相关文件名，如果还是不确定，**暂停询问用户**：
  ```
  ⚠️ 找不到 PageID "DictationSelectTypePage" 对应的页面文件。
  pageId 中文名是"听写批改-选择类型页"，你知道对应哪个文件吗？
  ```

### Step 5：写入代码

#### 5.1 页面曝光 (pageview)

检查页面是否已有 `usePageLog`：
- **已有**：跳过，告知"已存在 usePageLog"
- **没有**：在组件顶部添加 import 和调用：

```typescript
// 添加 import（如果还没有）
import usePageLog from '@/hooks/useLog'

// 在组件函数体中、state 声明之后添加
const Log = usePageLog('PageID值')
```

#### 5.2 行为埋点 (actionlog)

根据埋点描述，找到对应的交互代码位置并插入 `Log.action`：

**能确定位置的情况**（直接写入）：
- 描述中有明确的按钮/点击对象，且代码中有对应的 handler → 在 handler 最前面插入
- 描述是"进入页面时"→ 在 useMount/useEffect 中插入
- 描述是"弹窗展示时"→ 在控制弹窗显示的 state 变化处插入

**无法确定位置的情况**（暂停询问）：
- 描述模糊，代码中找不到明显对应的交互
- 多个 handler 都可能匹配
- 需要新增计算逻辑（如 duration 停留时长）

暂停询问格式：
```
⚠️ 埋点 "textbook_popup_stay"（教材选择弹窗停留时长）：
描述：点击关闭或确定关闭教材选择弹窗时均上报，duration为从弹窗展示到关闭的停留时长（毫秒）

这个需要：
1. 记录弹窗打开时间（useState + 打开时记录时间戳）
2. 关闭时计算 duration = Date.now() - openTime

请告诉我：
- 弹窗的显示/隐藏是由哪个 state 控制的？
- 还是你想让我自己找？
```

#### 5.3 参数写法

```typescript
// 无参数（平台显示 ---）
Log.action('dictation_homework_click')

// 有参数，变量已存在于当前作用域
Log.action('click_textbook_popup_close', { subject })

// 有参数，需要从上下文推断
Log.action('textbook_popup_stay', { duration, subject })
```

参数来源优先级：
1. 当前函数作用域已有同名变量 → 直接用
2. 组件 state/props 中有对应数据 → 引用
3. 路由参数中有 → `params.xxx`
4. 都没有 → **暂停询问用户**这个参数从哪来

### Step 6：完成报告

```
✅ 已实现 {N} 条埋点（需求：{需求名}）

已写入：
- src/pages/XxxPage/index.tsx
  - usePageLog('PageID') ← pageview
  - Log.action('actionId1') ← 在 handleXxx 中
  - Log.action('actionId2') ← 在 handleYyy 中

⚠️ 需要你手动处理：
- textbook_popup_stay: 需要添加计时逻辑（已标记 TODO）
```

---

## 暂停询问的场景汇总

以下情况停下来问用户，不要自己猜：

| 场景 | 问什么 |
|------|--------|
| 找不到 pageId 对应的文件 | 对应哪个页面文件？ |
| 埋点描述的交互在代码中找不到 | 这个操作对应哪个函数/按钮？ |
| 需要新增计算逻辑（如 duration） | 需要的数据从哪来？要我加计时逻辑吗？ |
| 参数在当前上下文中不存在 | 这个参数从哪获取？ |
| 一个 pageId 对应多个可能的文件 | 具体是哪个文件？ |

---

## 翻页处理

如果分页显示"共 N 条"且当前页不够：
1. 读取分页信息（"共 X 条"文本 + 当前页码）
2. 如有下一页，click 下一页按钮
3. 再次 snapshot 读取
4. 合并所有页数据

---

## 项目埋点 API 参考

```typescript
// 核心 hook — 页面级，自动发 PV
import usePageLog from '@/hooks/useLog'
const Log = usePageLog('PageID', { type: 'xxx' })  // type 可选

// 三种埋点方法
Log.page(pageId, data?)     // 手动 PV（通常不需要，usePageLog 自动处理）
Log.action(actionId, data?) // 用户行为
Log.trace(traceId, data?)   // 流程追踪

// 组件内（非页面）获取 Log
import { getLog } from '@/utils/getLog'
const Log = getLog()
```

规则：
- 一个页面只能有一个 `usePageLog`
- `Log.action` 放在事件处理函数最前面
- 子组件直接用 `getLog()` 即可，因为 pageId 是模块级全局变量（`cur_page_id`），`Log.page()` 调用后所有 `Log.action()` 自动继承当前 pageId
- 子组件不需要通过 props 传 Log，也不要在子组件调用 `usePageLog`
