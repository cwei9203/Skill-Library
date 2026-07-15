---
name: bee-static-upload
description: Plan, check CDN name collisions, review, copy, commit, and push images or folders into the correct bee-static CDN repository directory. Use when a user asks to upload or publish static assets to bee-static, infer a CDN destination from natural language or repository conventions, place downloaded iconfont assets in hash-specific subdirectories beneath hashIconfontDir, verify static-cdn-test URLs before upload, or safely commit and push selected CDN files after one explicit confirmation.
---

# Bee Static Upload

Upload selected files through a reviewable two-phase workflow. Treat copying, overwriting, committing, and pushing as one confirmed operation; never mutate the worktree, index, or history before confirmation.

## Resolve inputs

1. Accept files, folders, or both. Resolve relative paths against the user's working directory.
2. Resolve the repository in this order: an explicit user path, `BEE_STATIC_REPO`, the current Git repository when named `bee-static`, then a narrow filesystem search in the user's normal project roots.
3. Require the resolved repository to be a Git worktree with an `origin` remote. Do not clone unless the user explicitly asks.
4. Inspect `git status --short`, the current branch, `origin`, and `HEAD`. Preserve unrelated changes. Stop if a planned target already has unrelated uncommitted changes.
5. Run `git fetch origin` and report when the branch is behind or diverged. Do not merge, rebase, reset, switch branches, or pull automatically.

## Infer the destination

Read [references/directory-rules.md](references/directory-rules.md). Combine the user's wording with repository evidence; repository evidence wins over naming guesses.

Inspect only relevant evidence:

- Existing project and asset-family directories.
- Sibling filenames and tree shape.
- `git log --name-status -- <candidate-path>` for recent placement patterns.
- References to matching filenames or CDN paths in nearby source projects when the user provides them.
- Hash-like directory conventions and the artifact metadata that produced the hash.

Produce up to three candidates when ambiguous. Assign high, medium, or low confidence and state the evidence. Ask for destination clarification before creating the final plan when no candidate reaches high confidence. Never invent a hash value.

For an iconfont download directory whose basename matches `font_<project-id>_<hash>`, deterministically use only the final underscore-delimited hash as the destination folder. For example, `/Users/chen_wei/Downloads/font_4071061_semole6prt` maps to `hashIconfontDir/semole6prt`; do not preserve `font_4071061_` in the repository. Check for `hashIconfontDir` at the bee-static repository root. Reuse it when it is a real directory; plan to create it after confirmation when absent; stop if the path is a file or symbolic link. Copy the source directory contents directly into the hash folder. If the basename does not match this pattern, stop and ask instead of guessing a hash.

## Build the immutable plan

Set `SKILL_DIR` to the directory containing this `SKILL.md`. Use the bundled script and keep the plan outside the repository:

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" plan \
  --repo "$BEE_STATIC_REPO" \
  --source "/absolute/path/to/file-or-folder" \
  --destination "project/asset-family/hash" \
  --output "/tmp/bee-static-upload-plan.json"
```

Repeat `--source` for multiple inputs. A selected folder contributes its contents recursively beneath the destination. The script rejects symlinks, path traversal, duplicate targets, and sources outside ordinary files/directories. It records SHA-256 hashes and classifies targets as `new`, `identical`, or `conflict`.

For a matching iconfont download folder, prefer deterministic hash extraction over a manually assembled destination:

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" plan \
  --repo "$BEE_STATIC_REPO" \
  --source "/Users/chen_wei/Downloads/font_4071061_semole6prt" \
  --iconfont \
  --output "/tmp/bee-static-upload-plan.json"
```

`--iconfont` requires exactly one source directory. It always targets `hashIconfontDir/<extracted-hash>` and records whether the root directory already exists or will be created after confirmation.

Check every final URL before asking for confirmation. This updates the plan with results from the fixed prefix `https://static-cdn-test.mifengjiaoyu.com/`:

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" check-cdn \
  --plan "/tmp/bee-static-upload-plan.json"
```

Interpret CDN results conservatively:

- `available`: HTTP 404 or 410; the name is currently unused.
- `exists`: HTTP 2xx or 3xx; uploading this relative path can overwrite an existing CDN object.
- `unknown`: authentication, rate limiting, timeout, network failure, or any other response. Stop and resolve the check failure; never treat it as available.

Before confirmation, show one concise plan containing:

- Repository path, branch, remote, and HEAD.
- Source-to-destination mapping and counts by status.
- Whether the repository-root `hashIconfontDir` will be reused or created.
- Every repository conflict and every `exists` CDN URL explicitly. Label each CDN collision as **CDN 已存在，将覆盖**; default to no overwrite.
- Exact commit message and push ref.
- Every final CDN URL using the fixed prefix.
- Any unrelated dirty files that will remain unstaged.

Ask one explicit yes/no confirmation covering copy, all listed repository/CDN overwrites, exact-path staging, commit, and push. Accept an unambiguous affirmative reply. A changed destination, file list, hash, CDN status, overwrite set, branch, remote, commit message, or push ref invalidates the confirmation and requires a new plan and confirmation.

## Apply, commit, and push

After confirmation only:

1. Recheck that repository path, branch, remote, and HEAD match the plan.
2. Run `check-cdn` again immediately before apply and compare every URL status with the confirmed plan. If any status changed, stop and request a new confirmation. CDN checks older than 10 minutes are invalid.
3. Apply the plan. Add `--overwrite-conflicts` only when every repository conflict was listed in the confirmed plan. Add `--allow-cdn-overwrite` only when every `exists` CDN URL was explicitly listed as an overwrite in the confirmed plan:

```bash
python3 "$SKILL_DIR/scripts/asset_upload.py" apply --plan "/tmp/bee-static-upload-plan.json"
```

4. Inspect `git diff -- <exact-targets>`. Verify no unexpected file, credential, private key, source map, or environment file is included.
5. Stage only exact planned target paths with `git add -- <paths>`. Never use `git add .` or `git add -A`.
6. Verify `git diff --cached --check` and compare `git diff --cached --name-only` with the planned non-identical targets. Stop on any mismatch.
7. Commit using the confirmed message. Do not amend an existing commit.
8. Push without force using `git push origin HEAD:<confirmed-branch>`.

If any step fails, stop. Do not reset, discard files, force-push, or improvise a different destination. If commit succeeds but push fails, preserve the local commit and report the recovery command instead of retrying destructively.

## Report the result

Return the commit hash, pushed branch, uploaded/skipped counts, repository-relative paths, and CDN URLs when derivable. Mention any preserved unrelated changes. Delete the temporary plan after success; retain it on failure for diagnosis.

## Maintain the rules

Update [references/directory-rules.md](references/directory-rules.md) when a real bee-static repository reveals stable project, hash, or public URL conventions. Keep inferred observations separate from confirmed rules.

Keep the reading-only Chinese mirrors [SKILL.zh-CN.md](SKILL.zh-CN.md) and [references/directory-rules.zh-CN.md](references/directory-rules.zh-CN.md) synchronized whenever their English source files change materially. Continue to treat the English files as the executable source of truth.
