# ML Clean Workflow
> Removes experiment state from .ml/ directory and optionally cleans git branches/tags.
> Called by /gsd:ml-clean skill. Do not run directly.

---

## Pre-flight Check

Verify `.ml/` directory exists:

```bash
test -d .ml/ && echo "OK" || echo "NO_ML_DIR"
```

If `.ml/` does not exist, print:
> No experiment directory found. Nothing to clean.

Then STOP. Do not proceed.

---

## Step 1: Preview

Show what will be removed.

### 1a: Directory Size and File Count

```bash
du -sh .ml/
find .ml/ -type f | wc -l
```

Print:

```
Experiment directory: .ml/
Size: {size}
Files: {count}
```

### 1b: Git Branches and Tags (--branches flag only)

If the user passed `--branches`, also show:

```bash
git branch --list 'ml/run-*'
git tag --list 'ml-best-*'
```

Print the branch and tag lists. If none exist, print "No ml/ branches or tags found."

---

## Step 2: Artifact Preservation

Check if `.ml/artifacts/` exists and contains files:

```bash
test -d .ml/artifacts/ && find .ml/artifacts/ -type f | head -5
```

If artifacts exist, ask the user:

```
Best model artifacts found in .ml/artifacts/. Copy to ./model/ before cleaning? (y/n)
```

If the user confirms (y), copy artifacts:

```bash
mkdir -p model && cp -r .ml/artifacts/* model/
```

Print: "Artifacts copied to ./model/"

If the user declines (n) or no artifacts exist, skip this step.

---

## Step 3: Confirm

Unless the `--force` flag was passed, ask the user for confirmation:

```
Remove all experiment state? This will delete .ml/ and cannot be undone. (y/n)
```

Wait for the user's response. If they decline (n), print "Clean cancelled." and STOP.

If `--force` was passed, skip confirmation and proceed directly.

---

## Step 4: Delete

### 4a: Remove Experiment Directory

```bash
rm -rf .ml/
```

### 4b: Remove Git Branches and Tags (--branches flag only)

If `--branches` was passed, delete each branch and tag:

```bash
# Delete branches
for branch in $(git branch --list 'ml/run-*' | tr -d ' *'); do
    git branch -D "$branch" 2>/dev/null && echo "Deleted branch: $branch"
done

# Delete tags
for tag in $(git tag --list 'ml-best-*'); do
    git tag -d "$tag" 2>/dev/null && echo "Deleted tag: $tag"
done
```

### 4c: Summary

Print what was removed:

```
Cleaned:
  - Removed .ml/ directory ({size}, {count} files)
  - Deleted {n} branches, {m} tags  (if --branches)
```

---

## Notes

- This is a destructive operation. Always preview first, always confirm (unless --force).
- Artifact preservation is offered before any deletion.
- Branch/tag deletion only happens with explicit --branches flag.
