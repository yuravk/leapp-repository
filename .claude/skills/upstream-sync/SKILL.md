---
name: upstream-sync
description: >-
  Sync the AlmaLinux fork with the upstream oamg/leapp-repository by
  cherry-picking new commits. Use when the user asks to sync with upstream,
  cherry-pick upstream commits, or update from upstream.
---

# Upstream Sync Workflow

Sync the AlmaLinux fork with [oamg/leapp-repository](https://github.com/oamg/leapp-repository)
by cherry-picking upstream commits one at a time.

## Prerequisites

- Upstream remote: `oamg`
- Upstream repository: `git@github.com:oamg/leapp-repository.git`
- Upstream branch: `main`

## Step 1 — Fetch Recent Upstream Commits

```bash
git fetch oamg main
```

## Step 2 — Find the Latest Cherry-Picked Upstream Commit

Cherry-picked commits contain `(cherry picked from commit <hash>)` in their
message. Extract the hash of the most recent one:

```bash
git log --grep="cherry picked from commit" --format="%B" -1 \
  | grep "cherry picked from commit" \
  | sed 's/.*(cherry picked from commit \([a-f0-9]*\)).*/\1/'
```

This hash is the starting point — all upstream commits after it are missing.

## Step 3 — Cherry-Pick the Next Upstream Commit

Find the next commit after `<hash>` on the upstream branch (oldest first):

```bash
git log --reverse --format="%H" <hash>..oamg/main | head -1
```

Cherry-pick it with `-x` (records the source hash in the message):

```bash
git cherry-pick -x <hash_next>
```

## Step 4 — Resolve Cherry-Pick Conflicts (if any)

If the cherry-pick succeeds cleanly, skip to Step 5.

If there are conflicts:

1. Run `git diff` or `git status` to identify conflicted files.
2. Read the conflicted files, understand both sides (ours = local fork,
   theirs = upstream).
3. Propose resolved code and ask the user to review.
4. Once approved, stage and continue:

```bash
git add <resolved_files>
git cherry-pick --continue
```

5. Repeat until all conflicts are resolved.

## Step 5 — Track Data File Changes

Check whether the commit touches any of these data files. Record the hash for
the post-sync report.

### Device Driver Deprecation Data
- File: `etc/leapp/files/device_driver_deprecation_data.json`
- Report: **"Device Driver Deprecation Data is updated"**

### PES Data (Package Evolution Service)
- Files: `etc/leapp/files/pes-events.json`, `etc/leapp/files/repomap.json`
- Report: **"PES Data is updated"**

### Upgrade Paths (AlmaLinux)
- File: `repos/system_upgrade/common/files/upgrade_paths.json`
- Only report if the `"almalinux"` section changed: **"New upgrade path is
  added for the AlmaLinux"** with the specific entries.

To check:

```bash
git show --stat <hash> | grep -E 'device_driver_deprecation_data\.json|pes-events\.json|repomap\.json|upgrade_paths\.json'
```

To inspect AlmaLinux-specific changes:

```bash
git show <hash> -- repos/system_upgrade/common/files/upgrade_paths.json | grep -A5 -B5 'almalinux'
```

## Step 6 — Repeat Until Fully Synced

Go back to Step 3. Continue until all commits from `oamg/main` have been
cherry-picked.

## Step 7 — Post-Sync Report

After all commits are cherry-picked, report:
- Data file updates (Device Driver, PES, Upgrade Paths) with commit hashes.
- Summary: total commits, clean cherry-picks, conflicts resolved, remaining.
