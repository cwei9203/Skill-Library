# Bee-static 目录规则

将此文件作为已确认仓库约定的精简、可编辑记录。依赖任何规则前，都要先根据当前仓库验证该规则。

## 已从需求确认的规则

- 将下载的 iconfont 构建产物存放在仓库根目录下的 `hashIconfontDir/<hash>/...`。
- 检查 `hashIconfontDir` 是否存在。只有它是真实目录时才复用；不存在时在确认后创建；同名路径是文件或符号链接时停止。
- 下载的 iconfont 目录通常采用 `font_<项目ID>_<hash>` 结构，例如 `/Users/chen_wei/Downloads/font_4071061_semole6prt`。
- 只提取最后一个下划线后的部分（`semole6prt`）作为目标 hash 文件夹。将所选目录的内容直接放到 `hashIconfontDir/semole6prt/` 下。
- 仓库目标目录中不得包含 `font_<项目ID>_` 前缀。
- 如果所选目录不符合已确认的命名模式，不得根据修改时间或文件内容猜测 hash；应询问用户。

## 目标目录推断

证据按强弱顺序排列：

1. 用户明确提供的准确目标目录。
2. 从符合 `font_<项目ID>_<hash>` 规则的源目录提取最后一段 hash，并放到固定的 `hashIconfontDir` 根目录下。
3. manifest、样式表、生成的 iconfont 文件或源码 CDN 引用中嵌入的匹配路径。
4. 同一项目、资源类型和构建产物标识对应的已有目录。
5. 近期 Git 历史显示同一文件系列被放置在某个目录结构中。
6. 仅凭文件名或视觉内容相似度得出的判断。

选择 hash 目录时要求存在多个证据信号。不得仅因为某个 hash 在字典序上最大或修改时间最新，就将其选为目标。除非仓库或构建流水线中存在已确认的确定性生成规则，否则不得推导新的 hash。

如果多个已有 hash 都有可能，展示候选及其证据，并在最终上传确认前让用户选择。

## 公开 URL 约定

使用已确认的测试 CDN 前缀：

`https://static-cdn-test.mifengjiaoyu.com/`

将经过 URL 编码的仓库相对文件路径直接追加到该前缀后。例如：

`hashIconfontDir/deadbeef/iconfont.woff2`

会转换为：

`https://static-cdn-test.mifengjiaoyu.com/hashIconfontDir/deadbeef/iconfont.woff2`

确认前检查最终 URL。将 2xx/3xx 视为重名和明确的覆盖风险，将 404/410 视为可用，其他所有结果均视为未知并阻止后续操作。
