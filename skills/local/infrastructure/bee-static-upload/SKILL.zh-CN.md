---
name: bee-static-upload
description: 规划上传、检查 CDN 重名、审阅、复制、提交并推送图片或文件夹到 bee-static CDN 仓库中的正确目录。适用于用户要求向 bee-static 上传或发布静态资源、根据自然语言或仓库约定推断 CDN 目标目录、将下载的 iconfont 资源放入 hashIconfontDir 下对应的 hash 子目录、上传前校验 static-cdn-test URL，或在用户一次明确确认后安全地提交并推送所选 CDN 文件的场景。
---

# Bee Static 上传

通过一个可审阅的两阶段工作流上传所选文件。将复制、覆盖、提交和推送视为一次统一确认的操作；确认前不得修改工作树、暂存区或提交历史。

## 解析输入

1. 接受文件、文件夹，或两者同时输入。相对路径以用户的工作目录为基准解析。
2. 按以下顺序定位仓库：用户明确提供的路径、`BEE_STATIC_REPO`、名称为 `bee-static` 的当前 Git 仓库，最后在用户常用项目根目录中进行限定范围的文件系统搜索。
3. 要求解析出的仓库必须是具有 `origin` 远端的 Git 工作树。除非用户明确要求，否则不得克隆仓库。
4. 检查 `git status --short`、当前分支、`origin` 和 `HEAD`。保留无关修改。如果计划中的目标文件已经存在无关的未提交修改，立即停止。
5. 执行 `git fetch origin`，并在当前分支落后或发生分叉时报告。不得自动执行 merge、rebase、reset、切换分支或 pull。

## 推断目标目录

阅读 [references/directory-rules.zh-CN.md](references/directory-rules.zh-CN.md)。结合用户描述与仓库证据进行判断；仓库证据优先于基于命名的猜测。

只检查相关证据：

- 已有的项目目录和资源类型目录。
- 同级文件名与目录树结构。
- 使用 `git log --name-status -- <candidate-path>` 查看近期文件放置模式。
- 当用户提供附近的源码项目时，查找与文件名或 CDN 路径匹配的引用。
- 类似 hash 的目录约定，以及生成该 hash 的构建产物元数据。

存在歧义时，最多给出三个候选目录。为每个候选标注高、中或低置信度并说明依据。如果没有任何候选达到高置信度，在创建最终计划前询问用户目标目录。绝不得编造 hash 值。

如果 iconfont 下载目录的基本名称匹配 `font_<项目ID>_<hash>`，确定性地只使用最后一个下划线后的 hash 作为目标文件夹。例如，`/Users/chen_wei/Downloads/font_4071061_semole6prt` 映射到 `hashIconfontDir/semole6prt`；仓库中不得保留 `font_4071061_` 前缀。检查 bee-static 仓库根目录是否存在 `hashIconfontDir`：如果它是真实目录则复用；如果不存在，则计划在用户确认后创建；如果同名路径是文件或符号链接，则停止。将源目录内的内容直接复制到 hash 文件夹。如果基本名称不符合此模式，停止并询问用户，不得猜测 hash。

## 创建不可变计划

将 `SKILL_DIR` 设置为包含此 `SKILL.md` 的目录。使用技能附带的脚本，并把计划文件保存在仓库之外：

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" plan \
  --repo "$BEE_STATIC_REPO" \
  --source "/absolute/path/to/file-or-folder" \
  --destination "project/asset-family/hash" \
  --output "/tmp/bee-static-upload-plan.json"
```

存在多个输入时，重复使用 `--source`。选择文件夹时，将其内容递归放到目标目录下。脚本会拒绝符号链接、路径穿越、重复目标，以及普通文件或目录之外的源文件。脚本会记录 SHA-256 哈希，并将目标分类为 `new`、`identical` 或 `conflict`。

对于符合命名规则的 iconfont 下载目录，优先使用确定性的 hash 提取方式，不要手工拼接完整目标目录：

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" plan \
  --repo "$BEE_STATIC_REPO" \
  --source "/Users/chen_wei/Downloads/font_4071061_semole6prt" \
  --iconfont \
  --output "/tmp/bee-static-upload-plan.json"
```

`--iconfont` 只允许一个源目录。它始终以 `hashIconfontDir/<提取出的hash>` 为目标，并记录根目录是已经存在，还是将在确认后创建。

请求用户确认前，检查每一个最终 URL。以下命令会使用固定前缀 `https://static-cdn-test.mifengjiaoyu.com/` 检查 CDN，并把结果写回计划：

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" check-cdn \
  --plan "/tmp/bee-static-upload-plan.json"
```

保守解释 CDN 检查结果：

- `available`：HTTP 404 或 410；当前未使用该名称。
- `exists`：HTTP 2xx 或 3xx；上传这个相对路径可能覆盖已有 CDN 对象。
- `unknown`：鉴权、限流、超时、网络故障或其他响应。停止并解决检查失败；绝不得将其视为可用。

确认前展示一份简洁的计划，其中包含：

- 仓库路径、分支、远端和 `HEAD`。
- 源文件到目标文件的映射，以及各状态的数量。
- 仓库根目录的 `hashIconfontDir` 将被复用还是创建。
- 明确列出每一个仓库冲突和状态为 `exists` 的 CDN URL。将每一个 CDN 冲突标记为 **CDN 已存在，将覆盖**；默认不允许覆盖。
- 确切的 commit message 和 push ref。
- 使用固定前缀拼接出的每一个最终 CDN URL。
- 将保持未暂存状态的无关脏文件。

只询问一次明确的是/否确认；确认范围包括复制、所有列出的仓库/CDN 覆盖、按精确路径暂存、提交和推送。接受含义明确的肯定答复。目标目录、文件清单、hash、CDN 状态、覆盖集合、分支、远端、commit message 或 push ref 中任何一项发生变化，都会使确认失效，必须重新生成计划并再次确认。

## 应用、提交和推送

只能在用户确认后执行：

1. 重新检查仓库路径、分支、远端和 `HEAD` 是否与计划一致。
2. 应用前立即再次运行 `check-cdn`，将每个 URL 的状态与已确认计划进行比较。如果任何状态发生变化，停止并请求重新确认。超过 10 分钟的 CDN 检查结果无效。
3. 应用计划。只有当每一个仓库冲突都已列入确认计划时，才能添加 `--overwrite-conflicts`。只有当每一个状态为 `exists` 的 CDN URL 都已在确认计划中明确列为覆盖项时，才能添加 `--allow-cdn-overwrite`：

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" apply --plan "/tmp/bee-static-upload-plan.json"
```

4. 使用 `git diff -- <exact-targets>` 检查差异。确认其中不包含意外文件、凭据、私钥、source map 或环境文件。
5. 使用 `git add -- <paths>` 只暂存计划中的精确目标路径。绝不得使用 `git add .` 或 `git add -A`。
6. 执行 `git diff --cached --check`，并将 `git diff --cached --name-only` 与计划中所有非 `identical` 目标进行比较。发现任何不一致时停止。
7. 使用已确认的 commit message 提交。不得 amend 已有提交。
8. 使用 `git push origin HEAD:<confirmed-branch>` 进行非强制推送。

任何步骤失败时都要停止。不得 reset、丢弃文件、force push 或临时改用其他目标目录。如果提交成功但推送失败，保留本地提交并报告恢复命令，不得进行破坏性重试。

## 报告结果

返回 commit hash、已推送分支、上传和跳过的数量、仓库相对路径，以及能够推导出的 CDN URL。说明所有被保留的无关修改。成功后删除临时计划；失败时保留计划用于诊断。

## 维护规则

当真实 bee-static 仓库表明存在稳定的项目、hash 或公开 URL 约定时，更新 [references/directory-rules.zh-CN.md](references/directory-rules.zh-CN.md)。将推断观察与已确认规则分开记录。

正式英文文件 `SKILL.md` 或 `references/directory-rules.md` 发生实质变化时，同步更新对应的中文参考文件。本文件仅供阅读；技能执行仍以英文正式文件为准。
