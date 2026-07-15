# Skill Library

个人 AI Code Agent 技能聚合仓库。自定义技能由本仓库直接维护，第三方技能通过 Git submodule 固定版本，所有 agent 从同一份 `enabled/` 软链接目录加载。

## 目录

```text
skills/local/   自定义技能，按领域分类
upstreams/      第三方 Git submodules
enabled/        自动生成的统一技能入口
registry.json   启用清单与来源信息
scripts/        初始化、更新和校验工具
```

## 初始化

```bash
git clone --recurse-submodules https://github.com/cwei9203/Skill-Library.git
cd Skill-Library
./scripts/bootstrap.sh
```

已有全局技能目录时，首次迁移使用：

```bash
./scripts/bootstrap.sh --migrate
```

原目录会移动到仓库内被 Git 忽略的 `.migration-backups/`，确认运行正常后可自行删除。

## 更新

```bash
./scripts/update.sh
```

更新脚本只拉取上游、重建软链接并校验。GitHub Actions 会定期执行同一流程并创建更新 PR，不直接修改 `main`。

macOS 如果启用了系统 HTTPS 代理，脚本会自动读取该代理供 Git 使用，不修改全局 Git 配置。

## 原则

- 第三方仓库按来源聚合，一个仓库可提供多个 skills。
- `registry.json` 明确选择要启用的技能，避免上游新增内容自动进入全局环境。
- `enabled/` 只包含相对软链接，因此仓库可移动、可重新 clone。
- Codex `.system`、Cursor 内置技能等 vendor-managed 内容不纳入聚合。

第三方来源与恢复命令见 [SOURCES.md](SOURCES.md)。
