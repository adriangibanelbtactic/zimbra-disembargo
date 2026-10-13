# RHEL 9 source-package analysis environment

This is the development environment for the RHEL source-package method. It is
not yet an SRPM extraction or comparison workflow. Its current purpose is to
preserve a verified NE release input and provide a repeatable, disposable Rocky
Linux 9 console for identifying the corresponding public source-package inputs.

## Inputs and mounts

The initial release input is described by
[`manifests/ne-releases/10.1.0_GA_4688.RHEL9_64.20240911074203.conf`](../../manifests/ne-releases/10.1.0_GA_4688.RHEL9_64.20240911074203.conf).
This version-controlled manifest records the release identity, distribution,
architecture, edition, archive and checksum URLs, and the expected archive MD5.
It contains no NE material. The archive filename and its internal top-level
directory are both derived from the archive URL basename, after removing its
`.tgz` suffix.

`scripts/rhel9-source-analysis cache` downloads each of the archive and its
checksum only when it is absent from the host cache, then runs `md5sum --check`.
It also compares the result with the MD5 recorded in the release manifest.
The default cache is `cache/ne` in this repository. `cache/` is ignored by Git,
so neither the archive nor its checksum can be accidentally added to the
repository; set `ZIMBRA_NE_CACHE` to use a different location. The archive and
checksum are made non-writable by the current user after validation.

The running container sees the repository at `/project` and the cache at
`/inputs/ne`; Docker mounts both read-only. Its writable `/work` and `/results`
directories are also ignored host directories, defaulting to
`var/rhel9-source-analysis` in this checkout.

## Start an iterative console

From the repository root:

```sh
scripts/rhel9-source-analysis cache
scripts/rhel9-source-analysis start
scripts/rhel9-source-analysis shell
```

The `start` command builds `zimbra-disembargo-rhel9-source-analysis` from
Rocky Linux 9 if necessary and leaves the identically named container running.
Re-enter it at any time with `scripts/rhel9-source-analysis shell`. Check it
with `scripts/rhel9-source-analysis status`; remove only the container with
`scripts/rhel9-source-analysis stop`. Neither command removes the cache or
analysis work directory.

The console runs as the invoking host UID/GID rather than root. The default
`disembargo` user has passwordless `sudo` for exploratory package installation
or system inspection. It has RPM, `rpmbuild`, the `dnf download` plugin, `file`,
`jq`, archive tools, and standard comparison tools. Network access is
intentionally enabled during this exploratory phase so public SRPM locations can
be investigated. No source package is downloaded by this environment
automatically.

## Package repositories and SRPM access

The image copies the RHEL 9 repository definitions statically rendered from the
verified installer into `/etc/yum.repos.d`, imports Zimbra's RHEL 9 SHA-256
package-signing key, verifies its installed RPM key ID
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

## Current boundary and next evidence to record

The supported input boundary is one verified RHEL 9 NE tarball. The next step
is to establish, without inferring URLs, which installed package metadata or
vendor-published index identifies public SRPMs. For every discovered SRPM, the
future input manifest must at least record its package name, epoch/version/
release, architecture (`src`), source URL, download timestamp, SHA-256, and the
NE archive SHA-256 and path from which its relationship was observed.

Expected failures are an unavailable download, a malformed checksum, a checksum
mismatch, insufficient host disk space, or Docker being inaccessible. The
launcher exits on each of these rather than using an unverified input.

### Safely deriving repository URLs

`util/utilfunc.sh` in the installer contains `configurePackageServer`, which
selects and writes yum repository definitions. Do **not** source and invoke that
function to inspect it: it can import a GPG key, overwrite `/etc/yum.repos.d`,
and run `yum`.

Pass the verified installer archive directly to the static parser instead:

```sh
cd /work
/project/scripts/extract-rhel-yum-repositories \
  /inputs/ne/10.1.0_GA/zcs-NETWORK-10.1.0_GA_4688.RHEL9_64.20240911074203.tgz \
  --report repository-extraction.json
```

The parser reads `BASEDIR/util/utilfunc.sh` directly from the archive; it neither
extracts it to disk nor sources it. By default it writes the rendered files that
would be placed in `/etc/yum.repos.d` to `/work/yum.repos.d` and emits a JSON
report only when `--report` is supplied. That report contains the archive and
helper SHA-256 values, assumptions, repositories, and output paths. Use
`--output-directory` to choose another writable destination. Use `--platform`,
`--edition`, or `--package-server` to record a different supported assumption.
