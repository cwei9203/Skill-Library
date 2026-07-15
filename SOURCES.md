# 第三方 Skill 来源

第三方内容通过 Git submodule 固定版本，本仓库只保存上游 commit 指针、启用清单和软链接，不复制其历史。

| 分组 | 上游仓库 | 本仓库路径 | 官方/兼容安装命令 |
|---|---|---|---|
| Lark/飞书 | [larksuite/cli](https://github.com/larksuite/cli) | `upstreams/larksuite-cli` | `npx skills add larksuite/cli -y -g` |
| 工程工作流 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `upstreams/addyosmani-agent-skills` | `npx skills add addyosmani/agent-skills -y -g` |
| Skill 发现 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | `upstreams/vercel-labs-skills` | `npx skills add vercel-labs/skills --skill find-skills -y -g` |
| 文件化规划 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | `upstreams/planning-with-files` | `npx skills add OthmanAdi/planning-with-files --skill planning-with-files-zh -y -g` |

当前固定版本可通过以下命令查看：

```bash
git submodule status
```

本仓库的日常使用不执行上表中的逐项安装命令；`scripts/bootstrap.sh` 会统一初始化来源并建立全局链接。安装命令仅用于来源追溯和故障恢复。
