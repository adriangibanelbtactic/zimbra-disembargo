# Ubuntu 24.04 patch packages pseudo-code analysis environment

This is the acquisition and inspection foundation for Ubuntu 24.04 patch
packages pseudo-code analysis.
It provides a disposable Ubuntu 24.04 container which uses shared APT source
lists generated from a Network Edition (NE) installer and obtains versioned NE
Debian packages. It does **not** install
the packages or classify any included file as pseudo-code. It extracts
package payloads only to inventory regular files below
`/opt/zimbra/lib/patches`; source-like classification and semantic analysis are
still deliberately deferred.

## Repository definitions and mounts

The shared APT lists are in
[`Dockerfiles/repositories/debian-repos`](../../Dockerfiles/repositories/debian-repos).
They were generated once from the NE installer at
`https://files.zimbra.com/downloads/10.1.0_GA/zcs-NETWORK-10.1.0_GA_4876.UBUNTU24_64.20260428124223.tgz`.
The installer is not downloaded, mounted, or used at runtime. The lists use the
one-line `.list` format and are reused by both Ubuntu workflows. See the shared
[repository-definition provenance](../../Dockerfiles/repositories/README.md).

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis start
scripts/ubuntu24-patch-packages-pseudo-code-analysis shell
```

The running container has a read-only mount of the checkout at `/project`. Its
`/work` and `/results` are writable host directories under
`var/ubuntu24-patch-packages-pseudo-code-analysis` in this checkout. This
location is fixed deliberately; the Ubuntu workflow does not use a work-path
environment override. The container runs as the invoking host UID/GID, not root.

`build`, `status`, and `stop` have the same lifecycle meaning as the RHEL 9
analysis launcher. `stop` removes only the named container and leaves analysis
results intact. `start` refreshes the signed APT metadata
inside the disposable container, so package-version selection uses the current
published index rather than the image-build-time index.

## APT repositories

For `UBUNTU24_64` Network Edition, the generated lists use the `noble` suite
and the public `87`, `1000`, `1010`, `1000-ne`, `1010-ne`, and
`onlyoffice-1010` APT locations at `https://repo.zimbra.com/apt/`. The image
imports the installer-specified
signing key and verifies fingerprint
`254F9170B966D193D6BAD300D5CEF8BF9BE6ED79` before refreshing APT metadata.

The inspection command deliberately selects patch versions only from
`https://repo.zimbra.com/apt/1010-ne`. The separate OnlyOffice source is
configured because the installer configures it, but it is not currently an
input selector. At the time this foundation was established,
`zimbra-onlyoffice-patch` was indexed by `1010-ne`, alongside the other patch
packages.

## Debian package inspection

The default non-interactive command selects the latest version and immediate
predecessor from `1010-ne` for each currently available supported package:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis start
scripts/ubuntu24-patch-packages-pseudo-code-analysis deb-inspect
```

The supported package set is:

- `zimbra-patch`
- `zimbra-proxy-patch`
- `zimbra-mta-patch`
- `zimbra-onlyoffice-patch`

To inspect a selected version against its immediate predecessor, provide the
exact Debian version:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis deb-inspect zimbra-patch \
  --after 10.1.21.1789536217-2.u24
```

For a manual non-adjacent pair, use the terminal UI:

```sh
scripts/ubuntu24-patch-packages-pseudo-code-analysis deb-inspect --interactive
```

The UI first selects one of the supported packages, then a BEFORE version and
a later AFTER version. Type to filter; use arrow keys (or `j`/`k`) to move;
press Enter to confirm; and press `q` to cancel. It queries all versions still
listed by APT for `1010-ne`; it does not infer historical URLs. After both
packages are downloaded and extracted, a final screen lists only regular files
which are present in both payloads below `/opt/zimbra/lib/patches` and whose
MD5 differs. Select one to write its Git binary diff. The selector label shows
the installed path followed by the BEFORE and AFTER MD5 values.

Each selection creates a unique directory below
`results/deb-package-inspections` containing the exact downloaded `.deb` files,
their SHA-256 values, `dpkg-deb --info` output, `dpkg-deb --contents` output,
the extracted `before/payload` and `after/payload` trees, per-side
`patch-artifacts.json` MD5 inventories, and `manifest.json`. A selected
artifact additionally writes a binary patch under
`artifact-diffs/opt/zimbra/lib/patches/<filename>.diff`, preserving its
installed path in the result directory. Existing results are never overwritten.
APT verifies the signed repository metadata and package hashes during download;
the script also checks that the downloaded package name, Debian version, and
architecture are exactly the requested values.

The manifest labels this material as `ubuntu24-patch-packages-pseudo-code-analysis`.
It explicitly records that the packages were not installed and that patch-file
MD5s only identify byte changes; they do not classify a file as pseudo-code
or establish a semantic change. The next phase must define source-like-file
classification, normalization, and file-level comparison while keeping NE
contents out of Git.
