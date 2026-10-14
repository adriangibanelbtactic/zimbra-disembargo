# RHEL 9 source-package analysis environment

This is the development environment for the RHEL source-package method. It
provides a repeatable, disposable Rocky Linux 9 console for identifying the
corresponding public source-package inputs.

## Repository definitions and mounts

The image uses the shared RHEL repository definitions in
[`Dockerfiles/repositories/yum.repos.d`](../../Dockerfiles/repositories/yum.repos.d).
They were generated once from the NE installer at
`https://files.zimbra.com/downloads/10.1.0_GA/zcs-NETWORK-10.1.0_GA_4688.RHEL9_64.20240911074203.tgz`.
The installer is not downloaded, mounted, or used at runtime. See the shared
[repository-definition provenance](../../Dockerfiles/repositories/README.md)
for both RHEL and Ubuntu inputs.

The running container sees the repository at `/project` read-only. Its writable
`/work` and `/results` directories are ignored host directories, defaulting to
`var/rhel9-source-analysis` in this checkout.

## Start an iterative console

From the repository root:

```sh
scripts/rhel9-source-analysis start
scripts/rhel9-source-analysis shell
```

The `start` command builds `zimbra-disembargo-rhel9-source-analysis` from
Rocky Linux 9 if necessary and leaves the identically named container running.
Re-enter it at any time with `scripts/rhel9-source-analysis shell`. Check it
with `scripts/rhel9-source-analysis status`; remove only the container with
`scripts/rhel9-source-analysis stop`. Neither command removes the analysis work
directory.

The console runs as the invoking host UID/GID rather than root. The default
`disembargo` user has passwordless `sudo` for exploratory package installation
or system inspection. It has RPM, `rpmbuild`, the `dnf download` plugin, `file`,
`jq`, archive tools, and standard comparison tools. Network access is
intentionally enabled during this exploratory phase so public SRPM locations can
be investigated. No source package is downloaded by this environment
automatically.

## Package repositories and SRPM access

The image copies the shared generated RHEL 9 repository definitions into
`/etc/yum.repos.d`, imports Zimbra's RHEL 9 SHA-256 package-signing key,
verifies its installed RPM key ID
`gpg-pubkey-7c66bd84-6583eafa`, and then runs `dnf --assumeyes update` while
building the image. (`dnf` is the EL 9 implementation of the familiar `yum`
command.) Thus the update refreshes metadata from the configured Zimbra and
Rocky repositories and updates packages already present in the base image;
package signatures remain checked by each repository's `gpgcheck=1` setting.

`dnf-plugins-core` supplies `dnf download`. SRPMs are not enabled by a special
DNF switch: an RPM repository publishes them as ordinary packages with the
`src` architecture. The public `zimbra-1010-oss` repository is enabled in the
image and its metadata contains such records, so `dnf download --source` can
select and fetch them. Network Edition repositories, including
`zimbra-1000-network` and `zimbra-1010-network` (whose URLs contain `1000-ne`
and `1010-ne`) are configured for their binary packages but are not considered
SRPM sources.

For example, download a source RPM to the writable analysis directory and list
its contents:

```sh
mkdir -p /work/srpms
dnf download --source --repo=zimbra-1010-oss --downloaddir=/work/srpms \
  zimbra-altermime
rpm -qpl /work/srpms/zimbra-altermime-*.src.rpm
```

Always name the public repository explicitly when retrieving an SRPM. This
keeps binary-only Network Edition repositories out of source-package selection
and makes the source origin evident in command history and later evidence.

### Source comparison

Start the container, then supply a package name from the host. This is the
normal non-interactive workflow: it compares the latest public SRPM with the
immediately preceding public SRPM for that package.

```sh
scripts/rhel9-source-analysis start
scripts/rhel9-source-analysis srpm-diff zimbra-apache-components
```

To compare a particular public version with its immediate predecessor, name its
exact EVR (epoch, version, and release) with `--after`:

```sh
scripts/rhel9-source-analysis srpm-diff zimbra-apache-components \
  --after 2.0.12-1zimbra8.8b1.el9
```

`--after` also accepts a version alone when that version is unique. It rejects
ambiguous values rather than choosing a release silently.

The terminal UI is retained for manual investigation, such as choosing a
non-adjacent pair of versions:

```sh
scripts/rhel9-source-analysis srpm-diff --interactive
```

Its first screen lists public source package names with at least two available
SRPM versions; package versions do not appear until after a name is selected.
The following screens select the older (BEFORE) version and a later (AFTER)
version. Type to filter, use the arrow keys (or `j` and `k`) to move, press
Enter to select, and press `q` to cancel.

#### Manual TUI walkthrough in a new work directory

Run this from the repository checkout in an interactive terminal. It creates a
new host directory for this comparison session, rather than using the default
`var/rhel9-source-analysis` directory:

```sh
export ZIMBRA_ANALYSIS_WORK="$PWD/rhel9-srpm-review"
mkdir -p "$ZIMBRA_ANALYSIS_WORK"
```

The analysis container has a fixed name and its bind mounts are chosen when it
is created. If it already exists, remove that container first so the new work
directory is mounted. This does not remove any host work directory or previous
results:

```sh
if scripts/rhel9-source-analysis status >/dev/null 2>&1; then
  scripts/rhel9-source-analysis stop
fi
```

Build the current image, start a container with the new mount, and open the
manual selector:

```sh
scripts/rhel9-source-analysis build
scripts/rhel9-source-analysis start
scripts/rhel9-source-analysis srpm-diff --interactive
```

On the first screen, type enough of the package name to filter it, select the
package, then select its BEFORE and AFTER source-package versions. The AFTER
screen deliberately contains only versions newer than the selected BEFORE
version. Press `q` at any selection screen to cancel without downloading an
SRPM.

When the comparison completes, inspect the result path printed by the tool.
For the work directory above, results are below
`rhel9-srpm-review/results/srpm-diffs`. For example:

```sh
find "$ZIMBRA_ANALYSIS_WORK/results/srpm-diffs" -name manifest.json -printf '%h\n'
less "$ZIMBRA_ANALYSIS_WORK/results/srpm-diffs"/*/*/changes.diff
jq . "$ZIMBRA_ANALYSIS_WORK/results/srpm-diffs"/*/*/manifest.json
```

`changes.diff` is the readable source comparison. `manifest.json` records the
selected versions, repository, timestamp, SRPM SHA-256 values, and any source
archive expansion warnings. The same result directory retains the downloaded
SRPMs and the direct and expanded extraction trees for follow-up inspection.

Stop the disposable container when finished; the new host work directory and
its results remain available:

```sh
scripts/rhel9-source-analysis stop
```

The UI queries only `zimbra-1010-oss`, downloads the exact selected source RPMs
with `dnf download --source`, validates their RPM signatures, and writes a new
comparison directory below `/results/srpm-diffs` (the host's
`var/rhel9-source-analysis/results/srpm-diffs` by default). It retains the
downloaded RPMs and their direct extraction, expands common source archives to
make the comparison readable, and writes:

- `changes.diff`: a no-index Git diff of the extracted source views;
- `manifest.json`: selected versions, SRPM SHA-256 values, source repository,
  timestamp, and any archive-expansion warnings; and
- `before-*` and `after-*` directories containing the raw SRPM extraction and
  the readable comparison views.

Existing results are never overwritten: a repeated selection receives a numeric
suffix. The UI does not query `1000-ne` or `1010-ne` for source packages.

## Current boundary and next evidence to record

The current source-package inputs are the public repositories represented by the
shared generated definitions. The next step is to establish, without inferring
URLs, which installed package metadata or vendor-published index identifies
public SRPMs. For every discovered SRPM, record its package name,
epoch/version/release, architecture (`src`), source URL, download timestamp, and
SHA-256.

Expected failures are an unavailable public package download, insufficient host
disk space, or Docker being inaccessible.
