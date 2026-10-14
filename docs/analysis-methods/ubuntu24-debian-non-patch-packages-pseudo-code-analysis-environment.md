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
