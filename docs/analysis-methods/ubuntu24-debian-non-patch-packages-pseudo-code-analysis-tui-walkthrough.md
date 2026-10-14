# Ubuntu 24.04 Debian non-patch packages pseudo-code analysis: TUI walkthrough

This walkthrough manually compares one changed, potentially source-like file
from two versions of one non-patch Zimbra Network Edition (NE) Debian package.
It is a review aid only: a selected file is not thereby established to be
complete, authoritative, or official source code.

Downloaded packages, extracted payloads, and generated diffs remain in the
Git-ignored local directory
`var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis`. They are never
installed. Do not add them to Git.

## Start with a local analysis environment

Run the commands from the root of a fresh checkout or other directory in which
you want this workflow's separate `var/` directory. The analysis container has
a fixed name. Remove an existing one first, if present, so the current image
and checkout-local mounts are used; this does not remove the NE cache or prior
results:

```sh
if scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis status >/dev/null 2>&1; then
  scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis stop
fi
```

Cache the verified installer input if needed, build the image, start the
container, and create the reusable non-patch package catalogue:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis cache
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis build
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis start
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis catalog
```

The catalogue takes its package names and versions from every configured
`https://repo.zimbra.com/apt/` binary package index. Package names ending in
`-patch` are omitted, so they cannot appear in this selector. Reuse the
catalogue for later manual comparisons. To deliberately use a newer APT index,
run `catalog` again after `start` refreshes APT metadata.

## Select the package, versions, and file

Open the interactive selector in an interactive terminal:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect --interactive
```

It presents three screens:

1. Select the non-patch package to review, for example `zimbra-common-core`.
2. Select the older **BEFORE** version, then a later **AFTER** version.
3. After the exact packages are downloaded and extracted, select one changed
   regular file from the complete package payload.

The final screen lists only regular files that are present at the same installed
path in both versions and whose MD5 values differ. It searches the entire
payload, rather than a patch-specific directory. Each entry shows the installed
path followed by the BEFORE and AFTER MD5 values. Type to filter for a likely
source-like extension or filename, for example `.py`, `.pl`, `.sh`, `.xml`,
`.java`, or `zmcontrol`; use arrow keys (or `j`/`k`) to move, Enter to select,
and `q` to cancel.

Selecting a file writes a Git diff under a path like:

```text
var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/
  deb-package-inspections/zimbra-common-core/
  <before-version>__to__<after-version>/artifact-diffs/
  opt/zimbra/lib/example.py.diff
```

For text that Git recognizes as text, this is a readable unified diff. For
opaque or binary material, it is a Git binary patch; treat that only as an
artifact-change lead, not as a pseudo-source comparison.

## Review the selected comparison and provenance

The command prints its exact result directory. To find and review the selected
diff afterwards, substitute the package name selected in the TUI:

```sh
results=var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/deb-package-inspections/zimbra-common-core
find "$results" -path '*/artifact-diffs/*.diff' -type f -print

jq . "$results"/*/manifest.json

selected_diff="$(find "$results" -path '*/artifact-diffs/*.diff' -type f -print -quit)"
less "$selected_diff"
```

`manifest.json` records the selected package versions, APT-index origins,
downloaded package SHA-256 values, complete-payload inventory counts, selected
path, MD5 values, and relative diff path. `before/package-artifacts.json` and
`after/package-artifacts.json` inventory every regular file in each payload.
The extracted originals remain under `before/payload` and `after/payload` for
local follow-up only.

The selector does not offer files added or removed between versions, and does
not compare different installed paths. It intentionally compares one changed
path common to both package versions. When finished, remove the disposable
container while retaining the local results:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis stop
```
