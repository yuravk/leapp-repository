---
name: create-vendors-patch
description: >-
  Generate the AlmaLinux ELevate / Vendors patch for the leapp-repository RPM
  package. Use when the user asks to create a vendors patch, create an ELevate
  patch, generate the elevate patch, or update the vendors patch.
---

# Create Vendors / ELevate Patch

Generate the ELevate patch from the current leapp-repository fork, update the
RPM spec file, and commit the result in the RPM package repository.

## Configurable Inputs

Ask the user to confirm or provide these values before starting:

| Variable | Description | Current default |
|----------|-------------|-----------------|
| `<git_ref>` | Git tag/ref in the current repo against which `git diff` is run. Encodes the upstream package version and release. | `v0.24.0-1` |
| `<rpm_leapp_repository>` | Path (relative to this project root) to the RPM package repo containing the `.spec` and `SOURCES/`. | `../rpms/leapp-repository` |

### Derived variables

Parse `<git_ref>` to extract:

- `<package_version>` — version portion, e.g. `0.24.0` from `v0.24.0-1`
- `<package_release>` — release number, e.g. `1` from `v0.24.0-1`

## Workflow

### Step 0 — Detect patch mode

Determine whether the patch is for an **upstream sync** or for **local-only
changes**. This controls the changelog entry and commit message in later steps.

#### 0a — Find the last cherry-picked upstream hash

```bash
git log --grep="cherry picked from commit" --format="%B" -1 \
  | grep "cherry picked from commit" \
  | sed 's/.*(cherry picked from commit \([a-f0-9]*\)).*/\1/'
```

This gives `<last_cherry_picked_hash>`.

#### 0b — Check whether the RPM repo already has this hash patched

```bash
cd <rpm_leapp_repository>
git log --oneline --grep="<last_cherry_picked_hash>" | head -1
```

If a commit is found whose message matches
`Update AlmaLinux ELevate and Vendors patch to upstream <last_cherry_picked_hash>`,
then the upstream sync is **already patched**.

#### 0c — Check for newer local-only commits

Back in the leapp-repository project, find the cherry-pick commit itself and
list any commits made **after** it that are NOT cherry-picks:

```bash
cherry_pick_sha=$(git log --grep="cherry picked from commit" --format="%H" -1)
git log --no-merges --format="%H %s" "${cherry_pick_sha}..HEAD" | grep -v "cherry picked from commit"
```

#### 0d — Determine mode

- If 0b found a match **and** 0c found local-only commits →
  **`mode = local`**.  Save the list of those commit subjects as
  `<local_commit_summaries>`.
- Otherwise → **`mode = upstream`**.

### Step 1 — Validate RPM repository branch

```bash
cd <rpm_leapp_repository>
git branch --show-current
git status --porcelain
```

- The branch name must be `a8-elevate-XYZW` where `XYZW` is the dotless
  `<package_version>` (e.g. `0.24.0` → `0240`, so branch = `a8-elevate-0240`).
- There must be no uncommitted changes.

**If either check fails:** stop and ask the user whether to continue.

### Step 2 — Generate the patch

From the **leapp-repository** project root, run:

```bash
git diff <git_ref> > <rpm_leapp_repository>/SOURCES/leapp-repository-<package_version>-elevate.patch
```

### Step 3 — Update the spec file

Open `<rpm_leapp_repository>/SPECS/leapp-repository.spec`.

#### 3a — Validate Version

The `Version:` field must equal `<package_version>`. If it does not, **stop**
and report the mismatch.

#### 3b — Update Release

The `Release:` field format is:

```
<rpm_package_release>%{?dist}.elevate.<elevate_release>
```

Read the current `<rpm_package_release>` and `<elevate_release>` from the spec.

- If `<rpm_package_release>` equals `<package_release>` → increment
  `<elevate_release>` by 1.
- If `<rpm_package_release>` is less than `<package_release>` → set
  `<rpm_package_release>` to `<package_release>` and reset
  `<elevate_release>` to `1`.

#### 3c — Add changelog entry

Date format for all entries: `Mon Apr 14 2026` — three-letter day-of-week,
three-letter month, zero-padded two-digit day, four-digit year. Use the
current date.

**If `mode = upstream`:**

```
* <DAY_NAME> <MONTH_NAME> <DD> <YYYY> Yuriy Kohut <ykohut@almalinux.org> - <package_version>-<package_release>.elevate.<elevate_release>
- ELevate vendors support for upstream <package_version>-<package_release> version (<last_cherry_picked_hash>)
```

**If `mode = local`:**

```
* <DAY_NAME> <MONTH_NAME> <DD> <YYYY> Yuriy Kohut <ykohut@almalinux.org> - <package_version>-<package_release>.elevate.<elevate_release>
- <brief summary of the local-only commits>
```

Write a concise summary derived from `<local_commit_summaries>`. Each distinct
change should be a separate `- ...` line in the changelog if there are
multiple unrelated changes, or a single line if they are closely related.

### Step 4 — Review

Present the spec file changes to the user and wait for approval before
proceeding.

### Step 5 — Commit

Commit **both** the patch file and the spec changes in `<rpm_leapp_repository>`.

**If `mode = upstream`:**

```bash
cd <rpm_leapp_repository>
git add SOURCES/leapp-repository-<package_version>-elevate.patch SPECS/leapp-repository.spec
git commit -m "$(cat <<'EOF'
Update AlmaLinux ELevate and Vendors patch to upstream <last_cherry_picked_hash> (<package_version>-<package_release>)

The package version <package_version>-<package_release>.elevate.<elevate_release>
EOF
)"
```

**If `mode = local`:**

```bash
cd <rpm_leapp_repository>
git add SOURCES/leapp-repository-<package_version>-elevate.patch SPECS/leapp-repository.spec
git commit -m "$(cat <<'EOF'
<brief summary of the local-only commits>

The package version <package_version>-<package_release>.elevate.<elevate_release>
EOF
)"
```

Use the same brief summary as in the changelog entry for the commit subject.
