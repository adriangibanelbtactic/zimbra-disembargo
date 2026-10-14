# Ubuntu 24.04 patch packages pseudo-code analysis: TUI walkthrough

This walkthrough uses the Ubuntu 24.04 Network Edition (NE) package-inspection
environment to compare one changed, source-like file from two versions of one
patch package. It is a manual review aid: a file selected from
`/opt/zimbra/lib/patches` is **not** thereby established to be complete,
authoritative, or official source code.

The package payloads are extracted into the Git-ignored local directory
`var/ubuntu24-patch-packages-pseudo-code-analysis` and are never installed.
Do not add their contents, the downloaded `.deb` files, or generated diffs to
Git.

## Start the local analysis environment

Run these commands from the repository root in an interactive terminal. The
analysis container has a fixed name. If it already exists, remove it first so
the current image and fixed local `var/` mounts are used. This leaves existing
results intact:

```sh
if scripts/ubuntu24-patch-packages-pseudo-code-analysis status >/dev/null 2>&1; then
  scripts/ubuntu24-patch-packages-pseudo-code-analysis stop
fi
```

Build the current image, then start a container with local results mounted:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis build
scripts/ubuntu24-patch-packages-pseudo-code-analysis start
```

## Select the package, versions, and source-like file

Open the selector:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis deb-inspect --interactive
```

It has three screens:

1. Select the package to review, for example `zimbra-patch`.
2. Select the older **BEFORE** package version, then a later **AFTER** version.
3. After the exact packages are downloaded and extracted, select a changed file
   from `/opt/zimbra/lib/patches`.

The final screen contains only regular files present at the same installed path
in both versions whose MD5 values differ. Its entries show the installed path
and the BEFORE and AFTER MD5 values. Type to filter for a source-like extension
or known filename, for example `.py`, `.pl`, `.sh`, `.xml`, or `zmcontrol`.
Use arrow keys (or `j`/`k`) to move, Enter to select, and `q` to cancel.

When you select a file, the tool writes a diff under a path such as:

```text
var/ubuntu24-patch-packages-pseudo-code-analysis/results/deb-package-inspections/zimbra-patch/
  <before-version>__to__<after-version>/artifact-diffs/
  opt/zimbra/lib/patches/commands.py.diff
```

For text that Git recognizes as textual, this is a normal readable unified
diff. For opaque or binary material, it is a Git binary patch instead; treat
that as an artifact change lead rather than a pseudo-code comparison.

## Review the result and provenance

The command prints the exact result directory. To locate the selected artifact
diff and its record after the TUI exits:

```sh
find var/ubuntu24-patch-packages-pseudo-code-analysis/results/deb-package-inspections/zimbra-patch \
  -path '*/artifact-diffs/*.diff' -type f -print

jq . var/ubuntu24-patch-packages-pseudo-code-analysis/results/deb-package-inspections/zimbra-patch/*/manifest.json

selected_diff="$(find var/ubuntu24-patch-packages-pseudo-code-analysis/results/deb-package-inspections/zimbra-patch \
  -path '*/artifact-diffs/*.diff' -type f -print -quit)"
less "$selected_diff"
```

`manifest.json` records the selected package versions, repository origin,
downloaded package SHA-256 values, patch inventory counts, selected path, MD5
values, and relative diff path. `before/patch-artifacts.json` and
`after/patch-artifacts.json` are the full MD5 inventories below the patch root.
The extracted originals remain in `before/payload` and `after/payload` for
local follow-up only.

The current selector does not offer files added or removed between versions,
nor does it compare two unrelated installed paths. It intentionally selects a
single changed path common to both package versions. Stop the disposable
container when finished:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis stop
```
