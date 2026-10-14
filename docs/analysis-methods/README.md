# Zimbra NE analysis methods

Zimbra Disembargo will obtain evidence about Zimbra Network Edition (NE)
changes through three distinct methods. They are intentionally kept separate:
each has different inputs, extraction work, comparison techniques, confidence
limits, and licensing considerations.

This directory records the initial design boundary for those methods. It does
not define a claim that a detected difference is a vulnerability or that an
absence of differences proves releases are equivalent.

## Methods

| Method | Primary material | Initial development role | Intended steady-state owner |
| --- | --- | --- | --- |
| Distribution source packages | RHEL source packages; Ubuntu source packages may later be supported | `source-package-analysis-developer` | Scripts or an operational source-package role |
| Binary package binaries | Executables, libraries, and other binary artifacts from NE packages | `binary-package-analysis-developer` | Scripts or an operational binary-analysis role |
| Pseudo-source in binary packages | Human-readable or source-like material carried inside NE binary packages | `pseudo-source-analysis-developer` | Scripts or an operational pseudo-source role |

The three methods can corroborate one another, but their outputs must retain
their method, release, package, artifact, tool version, and input hashes so
that a finding can be reproduced and its provenance reviewed.

## Common operating principles

- Analyse only materials obtained and used lawfully; do not bypass access
  controls, authentication, licence checks, or technical protections.
- Keep NE materials out of Git. Store references, hashes, manifests, and
  derived reports in the project as appropriate, but do not commit proprietary
  package contents or pseudo-source.
- Compare like with like: record the distribution, architecture, package name,
  package version, build/release metadata, and extraction settings for both
  sides of a comparison.
- Prefer deterministic, scriptable extraction and normalization steps. Preserve
  originals and generate analysis output in explicit working/output locations.
- Treat results as leads for investigation. Clearly distinguish observed
  differences, inferred relationships, and confirmed upstream information.

## Lifecycle

Each method begins with an OpenCode role focused on building a repeatable
implementation: defining inputs and manifests, choosing safe extraction and
normalization steps, producing structured reports, and adding fixtures or tests
that do not contain NE material.

Once a method is stable, its routine work should move to either:

1. scripts that run the established workflow; or
2. a separate OpenCode operational role that executes and reviews that workflow
   without redesigning it.

The initial development roles are therefore not the final day-to-day operators.
They should document their interface and leave behind automation that an
operational role can use.

## Method boundaries

### 1. Distribution source packages

This method analyses source packages supplied by a distribution. RHEL source
packages are the initial target. Ubuntu source packages are a possible future
extension, not an assumed supported input.

Initial development should establish how to acquire or accept source-package
inputs, verify their identity, unpack them reproducibly, identify relevant
Zimbra components, normalize generated or distribution-specific noise, and
report meaningful source-level differences. The implementation must keep the
distribution-specific handling explicit so that Ubuntu support can be added
without silently treating it as RHEL-compatible.

### 2. Binary package binaries

This method compares binary artifacts from NE binary packages across releases.
It covers executables, shared libraries, archives, and other compiled or
opaque artifacts for which a binary-oriented comparison is appropriate.

Initial development should define package extraction, artifact inventorying,
architecture checks, stable fingerprints, comparison-tool adapters, and a
report format that maps each result back to its package and artifact. It should
separate packaging churn from a change in the binary artifact itself wherever
the available evidence permits.

### 3. Pseudo-source inside binary packages

This method extracts and compares source-like material embedded in NE binary
packages. Such material may be useful for review but is not assumed to be
complete, authoritative build source, or legally redistributable.

Initial development should identify and classify eligible embedded material,
extract it without committing it, normalize safe non-semantic variation, and
produce file-level comparison reports with provenance. It must not conflate
pseudo-source findings with either official source-package evidence or direct
binary analysis.

The Ubuntu 24.04 Debian-package acquisition and inspection environment
discovers and caches every package in the configured Zimbra APT repositories
before inventorying uninstalled payloads. It is documented in [Ubuntu 24.04
pseudo-source package environment](ubuntu24-pseudo-source-package-environment.md).

## Cross-method reporting

Reports should identify the evidence method first, then describe the release
pair, inputs, transformations, tools, and findings. When the same apparent
change is found through more than one method, reports may link the findings but
must retain the independent evidence records rather than merging them into a
single unsupported conclusion.
