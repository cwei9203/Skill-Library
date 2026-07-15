# 技术方案文档生成器 (tech-doc-generator)

自动根据需求文档和 Figma 设计链接生成符合团队规范的前端技术方案文档。

## 安装

此 skill 已安装在 `~/.claude/skills/tech-doc-generator/`

## 使用方法

### 基本用法

在 Claude Code 中调用：

```
/tech-doc-generator

需求文档：https://intsig-info.feishu.cn/wiki/xxx
Figma：https://www.figma.com/design/xxx
功能名称：课本同步详情页优化
```

### 完整示例

```
/tech-doc-generator

需求文档：https://intsig-info.feishu.cn/wiki/LBDiwiZ6wiwTVgkpsywcfiJQnuh
Figma：https://www.figma.com/design/5kmgtYtmYtsILrvODVBjBB/...?node-id=7075-10645
功能名称：小程序-学期分析优化
前端开发：@张露露
后端开发：@谭浩杰
估时：4天
```

## 生成的文档结构

生成的 Markdown 文档包含以下章节：

1. **相关文档** - 需求、设计、埋点链接和开发人员信息
2. **功能设计**
   - 2.1 总体设计 - 技术架构和设计思路
   - 2.2 实现详情 - 详细的功能点实现表格
   - 2.3 技术方案担忧点 - 风险和注意事项
3. **埋点** - 埋点方案（如需要）
4. **灰度方案** - 灰度发布策略（如需要）

## 文档输出位置

默认保存到：`~/Desktop/[功能名称]-前端技术方案.md`

## 前置要求

### 1. 飞书认证

首次使用需要完成飞书用户认证：

```bash
lark-cli auth login --domain docs,wiki --as user
```

### 2. 权限

需要以下飞书权限：
- `docx:document:readonly` - 读取文档
- `wiki:node:read` - 读取知识库

## 特性

### ✅ 支持的功能

- [x] 从飞书需求文档提取内容
- [x] 自动生成标准格式的技术方案
- [x] 包含功能设计表格
- [x] 支持自定义功能名称和开发人员
- [x] 保存为 Markdown 格式
- [x] 符合 react-taro-teacher 项目规范

### 📋 生成内容

- 文档头部（需求链接、设计链接、人员信息）
- 总体设计章节（技术选型、架构思路）
- 实现详情表格（功能点、页面、详细设计）
- 风险识别
- 埋点和灰度方案占位符

### 🔧 需要手动补充的内容

生成的文档是基础框架，以下内容需要开发人员根据实际情况补充：

- 具体的技术实现细节
- 代码文件路径
- 接口对接信息
- 详细的埋点方案
- 具体的灰度策略
- 时间估算细节

## 示例输出

```markdown
# 小程序-学期分析优化-前端技术方案

## 相关文档

需求相关：[需求管理链接]

需求文档：[飞书需求文档]

设计文档：https://www.figma.com/design/5kmgtYtmYtsILrvODVBjBB/...

前端开发：@张露露

后端开发：@谭浩杰

| 内容 | 人员 | 估时(d) |
|------|------|---------|
| 学情分析优化 | @张露露 | 4 |

## 功能设计

### 2.1 总体设计

**技术选型**：
- 框架：Taro 3.6 + React 18 + TypeScript
- 状态管理：Zustand
- 样式方案：TailwindCSS + CSS Modules

...
```

## 注意事项

1. **隐私安全**：生成的文档可能包含内部链接，注意保密
2. **内容审核**：AI 生成的内容需要人工审核和完善
3. **技术细节**：具体实现需要开发人员根据实际情况填写
4. **版本控制**：建议将文档纳入 Git 管理

## 故障排查

### 问题：无法读取需求文档

**解决方案**：
1. 检查飞书认证状态：`lark-cli auth login --domain docs,wiki --as user`
2. 确认有文档访问权限
3. 检查文档链接格式是否正确

### 问题：生成的文档内容不完整

**原因**：AI 只能提取需求文档中的基础信息，具体技术实现需要手动补充

**建议**：
- 参考已有的技术方案文档格式
- 补充详细的实现细节
- 添加具体的代码路径和接口信息

## 技术要点参考

生成文档时会考虑以下项目规范（基于 react-taro-teacher）：

### 必查项
- [ ] 灰度控制需求
- [ ] 涉及页面路径
- [ ] API 接口设计
- [ ] Store 状态管理
- [ ] 组件化方案
- [ ] 分包体积影响
- [ ] 埋点要求

### 关键文件路径
- 组件：`src/components/` 或 `src/components-pro/`
- 页面：`src/pages/`，需在 `src/modulePagesConfig.ts` 注册
- API：`src/api/`
- Store：`src/store/`
- 类型：`src/types/`

## 更新日志

- **v1.0.0** (2026-05-28)
  - 初始版本发布
  - 支持从飞书需求文档生成技术方案
  - 符合 react-taro-teacher 项目规范
