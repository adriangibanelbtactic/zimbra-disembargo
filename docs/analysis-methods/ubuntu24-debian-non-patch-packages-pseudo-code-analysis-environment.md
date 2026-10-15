# Ubuntu 24.04 Debian non-patch packages pseudo-code analysis environment

This sibling workflow acquires and inspects the non-patch Debian packages made
available by the configured Ubuntu 24.04 Zimbra APT repositories. It uses a
separate image, container, working directory, catalogue, and result tree from
the patch-package workflow.

Packages are never installed. Each selected `.deb` is downloaded through APT,
recorded with package and hash metadata, and extracted only to inventory every
regular file in its payload. The workflow does not yet classify a file as
pseudo-code or make a semantic assessment of a change.

## Input and lifecycle

The shared generated APT `.list` files are the same as those used by the
patch-package environment; see its [repository-definition
provenance](ubuntu24-patch-packages-pseudo-code-analysis-environment.md#repository-definitions-and-mounts).
The non-patch workflow has its own host path:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis build
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis start
```

Its writable working and results directory is
`var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis`; it is
Git-ignored. The checkout is a read-only container mount. `stop` removes only
this workflow's named container.

### Ubuntu repository series

Ubuntu 24.04 (`noble`) remains the default repository series.  The Ubuntu 24
analysis image can also query the Zimbra `bionic`, `focal`, and `jammy`
repositories without building a second image.  Pass `--ubuntu-series` to
`start`, `shell`, `catalog`, `deb-inspect`, or `source-extract`:

```sh
# Select only Zimbra's Ubuntu 18.04 (bionic) package indexes.
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis \
  catalog --ubuntu-series 18

# Inspect using the resulting Ubuntu 18 catalogue.
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis \
  deb-inspect zimbra-common-core-jar --ubuntu-series 18
```

The launcher removes the active Zimbra APT lists, copies exactly one checked-in
series profile, removes old Zimbra package-index files, and then runs
`apt-get update`.  Thus `--ubuntu-series 18` never combines `bionic` package
indexes with `focal`, `jammy`, or `noble` indexes.  Ubuntu base-image indexes
may still be present, but the catalogue accepts only `repo.zimbra.com/apt/`
indexes.

Non-default results are isolated under `results/ubuntu18/`,
`results/ubuntu20/`, or `results/ubuntu22/`; default Ubuntu 24 results retain
their existing paths.  Do not run two commands using different series against
the same named container at the same time.

### Original installer package repositories

APT metadata may eventually drop a package build that was shipped in an
original NE installer.  The checked-in manifests in
[`manifests/ne-releases`](../../manifests/ne-releases) record the public URLs,
checksum URLs, and expected MD5 values for the 10.1.0 Ubuntu 18, 20, 22, and
24 Network Edition installers.  The archives themselves and their extracted
package contents remain under ignored `cache/ne/`; they are never committed.

Use `--local-release` with the matching Ubuntu series to download, verify, and
safely extract only the installer `packages/` directory on the host.  The
launcher bind-mounts `cache/ne/` read-only at `/ne-cache` and configures that
one extracted directory as a local APT source in addition to the selected
series' Zimbra repositories:

```sh
# The local-release option requires a container created with the /ne-cache mount.
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis stop
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis \
  start --ubuntu-series 18 --local-release 10.1.0

scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis \
  source-extract --ubuntu-series 18 --local-release 10.1.0 \
  zm-web-client 10.1.0 10.1.1
```

The host helper verifies the archive against both the checked-in MD5 and the
published `.md5` file before extraction.  It accepts only regular files and
directories beneath the archive's single `packages/` directory, rejecting
links and other member types.  This preserves the original package pair while
never executing an installer or installing a package.

## Package catalogue

Build the package catalogue once after `start`:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis catalog
```

The command reads the downloaded binary `Packages` indexes for **every** APT
source whose URI begins `https://repo.zimbra.com/apt/`. It stores the package
names, all indexed versions, architectures, source-index URIs, and index
SHA-256 values at:

```text
var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/
zimbra-non-patch-debian-package-catalogue.json
```

Any package whose name ends in `-patch` is excluded while creating the
catalogue. Consequently, patch packages are not candidates for selection or
default inspection. The persisted catalogue is reused by later inspections, so
package discovery is not repeated. Refresh it deliberately after refreshing
APT metadata when a new published index should be considered:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis catalog
# or rebuild it immediately before an inspection
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect --refresh-catalog
```

To catalogue every supported series and write one LLM-readable version/source
map, use:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis catalog-availability
```

It writes `results/ubuntu-repository-version-map.json`.  Each entry records a
package name, exact Debian version, architecture, Ubuntu series, and the exact
Zimbra APT `Packages` index URI(s) that supplied it.  The per-series catalogues
used to produce the map are retained alongside it.

## Debian package inspection

With a catalogue present, the default command compares the latest catalogued
version and immediate predecessor for every non-patch package that has at least
two versions:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect
```

To inspect one package or select a non-adjacent version pair:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect zimbra-common-core
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect zimbra-common-core \
  --after 10.1.21.1789536217-1.u24
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis deb-inspect --interactive
```

The TUI filters the catalogued package list, then selects a before and later
after version. It can write a Git binary diff for one changed regular file.

Each comparison creates a unique directory under
`results/deb-package-inspections/<package>/<before>__to__<after>/`. It includes
the exact `.deb` files, their SHA-256 values, `dpkg-deb --info` and
`--contents` output, extracted payload trees, full-payload
`package-artifacts.json` MD5 inventories, and `manifest.json`. A selected
artifact diff is stored under `artifact-diffs/` with the installed path.

APT verifies signed repository metadata and package hashes during download; the
script also verifies the selected package name, version, and architecture.
Inventories exclude symlinks and identify byte changes only. They neither
classify material as pseudo-code nor establish a semantic change.

## Deterministic source extractors

A source extractor correlates an existing package inspection with explicitly
mapped paths in one public upstream Git repository. It does not reconstruct a
package artifact and does not infer source paths with an LLM. It uses the
nearest lower existing public upstream tag as a baseline, then reconstructs an
upstream diff from uniquely mapped before/after package hunks. It never requires
or reads an upstream tag for the target package release.

The first definition is [`zm-ajax`](../../source-extractors/zm-ajax.json). It
maps the `Ajax_all.js` artifact in `zimbra-mbox-webclient-war` to `.js`
candidates under `WebRoot/js/ajax` in the public `Zimbra/zm-ajax` baseline; it
does **not** predeclare `DwtListView.js`. Each changed artifact hunk's
before-side text is located in every candidate baseline source file. A source
path is reconstructed only when there is one unique exact match. Its derivation
records that `Ajax_all.js` is an Ajx package bundle whose dependency manifest is
`WebRoot/js/ajax/package/Ajax.js`.

For the normal workflow, provide the extractor and after release. The command
finds the nearest lower existing upstream tag, refreshes the package catalogue,
downloads the newest matching build of the extractor's package for each
release, runs the package inspection, and prints one upstream-ready
`upstream.diff` path:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract \
  zm-ajax 10.1.20
```

The command caches public upstream repositories under `/work` and writes a new
result beneath `results/source-extractions/zm-ajax/<before-tag>__to__<after-tag>/`.
For this example it selects `10.1.17`: tags `10.1.18` and `10.1.19` do not
exist in `Zimbra/zm-ajax`. Pass both tags, for example
`source-extract zm-ajax 10.1.17 10.1.20`, to override automatic selection.

The result contains:

- `upstream.diff`: one reconstructed Git diff that can be applied from the
  public baseline repository root;
- `upstream-diffs/`: the same reconstructed changes as path-specific Git
  diff(s);
- `matched-artifact-hunks.json`: changed package hunks with one exact mapped
  baseline source location; and
- `unmatched-artifact-hunks.json`: changed text hunks from every common package
  artifact that passes the extractor filters but has no mapped source-hunk
  match. This also records ambiguous matches instead of choosing a source file
  arbitrarily.

Extractor definitions can use `artifact-positive` to scope an extractor to
specific installed artifact paths. An empty list accepts every changed common
artifact. Within that scope, suffix filters apply: `filter-positive` is an
allow-list and `filter-negative` is a deny-list. The default negative suffixes
are `.jar`, `.class`, `.java`, `ZaMsg*properties`, `ZsMsg*properties`, and
`.zgz`. The `ZaMsg*properties` and `ZsMsg*properties` filename globs exclude
translated Admin Console and mailbox message resources without excluding other
properties files. New extractor definitions must retain both exclusions when
they specify `filter-negative`; omitting that field inherits the default list.
The `zm-ajax` definition deliberately has an empty positive filter. Binary
changes and changed files added or removed between package versions have no
unified text hunk and are not entries in the unmatched-hunk report.

Use exactly **one extractor definition per upstream GitHub repository**. When
another release exposes a new textual package artifact for an already covered
repository, add its installed artifact to that definition's
`artifact-positive` list and add a mapping with its own package, source roots,
suffixes, and optional bundle derivation. Do not create a second definition for
the same upstream repository merely to isolate a release or feature.

For a directory of directly installed source files, a mapping can instead use
`artifact-root` and `source-root`. Each changed artifact below the installed
root is considered only when its relative path exists below the source root at
the baseline tag. For example, `opt/zimbra/bin/zmlicensectl` maps directly to
`src/bin/zmlicensectl`. This scopes the extractor to that directory without
having to enumerate each script.

`source-extract-manual` retains the lower-level interface for an already
created inspection directory. It accepts the former `--tag` and
`--inspection-directory` arguments and is intended for investigating package
selection or mapping behaviour rather than routine extraction.
