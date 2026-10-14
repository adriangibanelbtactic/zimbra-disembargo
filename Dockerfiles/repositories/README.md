# Generated Zimbra repository definitions

This directory contains the repository definitions used by every analysis-image
build. They are checked-in generated configuration, not Network Edition (NE)
material, so building or starting an analysis environment does not download an
NE installer archive.

The RHEL definitions in [`yum.repos.d`](yum.repos.d) were rendered from
`util/utilfunc.sh` in this installer download:

`https://files.zimbra.com/downloads/10.1.0_GA/zcs-NETWORK-10.1.0_GA_4688.RHEL9_64.20240911074203.tgz`

The Ubuntu 24.04 definitions at the root of
[`debian-repos`](debian-repos) were rendered from `util/utilfunc.sh` in this
installer download:

`https://files.zimbra.com/downloads/10.1.0_GA/zcs-NETWORK-10.1.0_GA_4876.UBUNTU24_64.20260428124223.tgz`

The `ubuntu18`, `ubuntu20`, `ubuntu22`, and `ubuntu24` subdirectories contain
suite-isolated alternatives for the Ubuntu 24 analysis image.  They use the
same Zimbra APT channels with their respective `bionic`, `focal`, `jammy`, and
`noble` suites.  The launcher copies exactly one profile into APT before it
refreshes metadata; it never combines package indexes from Ubuntu series.

The Ubuntu definitions use the one-line APT `.list` format. Their `signed-by`
option refers to the key installed by each Ubuntu image.
