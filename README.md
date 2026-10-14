# Zimbra Disembargo

Zimbra Disembargo tries to identify changes in Zimbra Network Edition (NE)
software between releases. Its primary purpose is to make it faster to find and
review delayed changes, especially security fixes.

## Why this exists

Zimbra's FOSS source does not always become available at the same time as its
corresponding NE release. The community-maintained [Zimbra FOSS Source Code
Only Releases][foss-releases] page records releases whose source was delayed,
and describes embargoes that usually last 60 days. The maintainers of
`zimbra-foss` have also documented cases where delayed or missing commits make
FOSS releases difficult to build.[^zimbra-foss]

This project exists because the corresponding FOSS source is not always
available when an NE release is made. Comparing NE binaries and the
pseudo-source code found in NE packages can provide clues about changes before
the corresponding FOSS source is published. The results are indications for
further investigation, not a guarantee that every change will be found or
correctly identified.

## What it does

The tool is intended to:

- compare NE binaries from different releases;
- compare pseudo-source code included in NE packages;
- identify differences that may correspond to functional or security changes;
  and
- provide context that helps maintainers and downstream builders investigate
  those differences and correlate them with later FOSS source releases.

Finding a change is not a security advisory, a determination of exploitability,
or a substitute for reviewing upstream advisories and applying appropriate
updates.

## Containerized analysis environment

This project will use Docker for its analysis environment. The host only needs
Docker and the repository checkout; distribution-specific packages, utilities,
and temporary files belong in a container. This keeps the host system clean and
makes the same workflow usable for every supported target distribution.

The approach is adapted from [Zimbra FOSS Builder][zimbra-foss-builder]: each
target distribution has its own Dockerfile, and the container's unprivileged
working user is created with the invoking user's UID and GID. Files written to
a bind-mounted output directory therefore remain owned by the user on the host,
not by `root`.

### Prerequisites

- Docker Engine (not merely a Docker-compatible command supplied by another
  container runtime);
- a regular, non-root user that can run Docker; and
- sufficient local disk space for images, package caches, extracted packages,
  and analysis results.

Install Docker Engine using the [official instructions for your
distribution][docker-install]. On RHEL-family systems, verify that the
installed service is Docker Engine: `podman` and `buildah` are not drop-in
replacements for all Docker build and volume behaviours used by this project.

Give the build user access to Docker once, then start a new login session (or
run `newgrp docker`):

```sh
sudo usermod -aG docker "$USER"
newgrp docker
docker run --rm hello-world
```

Membership in the `docker` group is effectively privileged access to the host.
Use a dedicated build account where that is not acceptable, and do not run the
workflow as `root`.

### Design and file handling

When the container support is added, Dockerfiles will be organised by target
distribution. Each image will install only the tools and libraries needed for
that target; package-manager changes stay inside the image rather than changing
the host OS.

Images will accept the host identity at build time, following the pattern used
by Zimbra FOSS Builder:

```sh
docker build \
  --build-arg ZIMBRA_DISEMBARGOER_UID="$(id -u)" \
  --build-arg ZIMBRA_DISEMBARGOER_GID="$(id -g)" \
  --tag zimbra-disembargo-<distro> \
  -f Dockerfiles/<distro>/Dockerfile .
```

Analysis inputs and results will be passed through explicit bind mounts. The
repository and input directories should be mounted read-only where possible;
only the results directory should be writable. Do not mount the Docker socket,
your home directory, or SSH credentials into an analysis container unless a
specific documented operation requires them. In particular, Network Edition
materials should remain local and must not be baked into images or committed to
this repository.

### RHEL 9 source-package comparisons

The RHEL 9 analysis container can download and compare public Zimbra source
RPMs. Its shared, checked-in repository definitions were generated from an NE
installer once; the workflow never downloads that installer. For the normal
package-name workflow and a manual TUI walkthrough in a fresh work directory,
see [RHEL 9 source-package analysis environment](docs/analysis-methods/rhel-source-package-environment.md).

### Ubuntu 24.04 patch packages pseudo-code analysis

The Ubuntu 24.04 analysis container uses shared, checked-in APT source lists
generated from an NE installer once; it does not download that installer. It
records selected Network Edition Debian patch packages for
Ubuntu 24.04 patch packages pseudo-code analysis. See [Ubuntu 24.04 patch
packages pseudo-code analysis environment](docs/analysis-methods/ubuntu24-patch-packages-pseudo-code-analysis-environment.md).

For a fresh-work-directory, manual TUI workflow that selects and reviews one
changed source-like patch file, see [Ubuntu 24.04 patch packages pseudo-code
analysis: TUI walkthrough](docs/analysis-methods/ubuntu24-patch-packages-pseudo-code-analysis-tui-walkthrough.md).

### Ubuntu 24.04 Debian non-patch packages pseudo-code analysis

The separate Ubuntu 24.04 container inventories every regular file in package
payloads from all configured Zimbra APT repositories, excluding `*-patch`
packages. It persists a reusable package catalogue and has its own working
path. See [Ubuntu 24.04 Debian non-patch packages pseudo-code analysis
environment](docs/analysis-methods/ubuntu24-debian-non-patch-packages-pseudo-code-analysis-environment.md).

For a manual TUI workflow that selects one non-patch package, two versions, and
one changed full-payload file, see [Ubuntu 24.04 Debian non-patch packages
pseudo-code analysis: TUI walkthrough](docs/analysis-methods/ubuntu24-debian-non-patch-packages-pseudo-code-analysis-tui-walkthrough.md).

The same environment can run deterministic [source extractors][source-extractors]
that map selected package artifacts to public upstream Git paths and preserve
unmatched artifact hunks for review.

See [source extractor usage][source-extractor-usage] for automatic previous-tag
selection and its upstream-ready diff output.

For a complete fresh-checkout verification of the first extractor, see the
[`zm-ajax` source extractor walkthrough][zm-ajax-source-extractor-walkthrough].

## What open source means here

The source code in this repository is open source and is licensed under the GNU
GPL v3.0. That license applies to this project; it does **not** apply to Zimbra
Network Edition binaries, packages, pseudo-source code, trademarks, or other
materials that may be examined with it. Those materials remain subject to their
copyrights, licenses, and other applicable rights. This project does not claim
that NE materials are open source or grant permission to redistribute them.

The project is intended to work with NE materials obtained lawfully, such as
software that a user is entitled to possess. Users are responsible for making
sure that their acquisition, use, analysis, and sharing of any such material is
permitted in their jurisdiction and under its applicable license. Laws on
reverse engineering and interoperability differ and may apply only in specific
circumstances. Nothing here authorizes bypassing authentication, access
controls, license checks, technical protection measures, or other restrictions,
or obtaining non-public source code. This README describes the project's scope;
it is not legal advice.

Zimbra and Zimbra Collaboration are trademarks of their respective owners.
This is an independent community project and is not affiliated with, endorsed
by, or supported by Zimbra or Synacor.

## References

- [Zimbra FOSS Source Code Only Releases][foss-releases]
- [Zimbra FOSS discussion: “How frequently will we receive patch updates for
  ZCS FOSS?”][zimbra-foss-discussion]
- [Zimbra's public GitHub organisation][zimbra-github]
- [Zimbra FOSS Builder][zimbra-foss-builder]

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

[foss-releases]: https://wiki.zimbra.com/wiki/Zimbra_Foss_Source_Code_Only_Releases
[zimbra-foss-discussion]: https://github.com/maldua/zimbra-foss/discussions/20#discussioncomment-13879644
[zimbra-github]: https://github.com/Zimbra
[zimbra-foss-builder]: https://github.com/maldua/zimbra-foss-builder
[docker-install]: https://docs.docker.com/engine/install/
[source-extractors]: docs/analysis-methods/ubuntu24-debian-non-patch-packages-pseudo-code-analysis-environment.md#deterministic-source-extractors
[source-extractor-usage]: docs/analysis-methods/ubuntu24-source-extractor-usage.md
[zm-ajax-source-extractor-walkthrough]: docs/analysis-methods/ubuntu24-source-extractor-zm-ajax-walkthrough.md

[^zimbra-foss]: See the linked discussion for a maintainer's explanation of
    embargoed and missing commits, and their impact on FOSS builds.
