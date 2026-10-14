# Ubuntu 24.04 source extractor usage

`source-extract` creates an upstream-ready Git diff from two Zimbra release
versions. An extractor definition identifies the public upstream repository,
the relevant NE package, and the candidate source scope used to map package
bundle changes back to upstream files.

The routine command needs an extractor and an after release. The before release
is optional:

```text
source-extract <extractor> [<before-release>] <after-release>
```

To let the extractor find the nearest lower existing upstream tag, pass only the
after release. For `zm-ajax`, this finds `10.1.17` before `10.1.20` because the
`10.1.18` and `10.1.19` tags do not exist:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis build
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis start

scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract \
  zm-ajax 10.1.20
```

Pass both releases to select the comparison explicitly:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract \
  zm-ajax 10.1.17 10.1.20
```

The command automatically:

1. rebuilds the local non-patch package catalogue from the current APT metadata;
2. selects the newest catalogued build of the extractor's package whose Debian
   version starts with each release label;
3. downloads and extracts those two packages without installing them;
4. searches the public baseline source tree under the extractor's configured
   source scope for each package hunk's before-side text;
5. reconstructs a source-file change only when that baseline match is unique;
   and
6. writes and prints the path to one `upstream.diff` file.

The command requires the requested package builds to remain available in the
configured Zimbra APT repositories. It currently supports extractors whose
mappings use one Debian package.

## Output

For the example above, a fresh checkout writes:

```text
var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/
source-extractions/zm-ajax/10.1.17__to__10.1.20/upstream.diff
```

`upstream.diff` is a normal Git diff scoped to the source files found by the
extractor. Review or apply it from a checkout of the extractor's upstream
repository at the before tag:

```sh
git checkout 10.1.17
git apply --check /path/to/upstream.diff
git apply /path/to/upstream.diff
```

The adjacent `manifest.json` records the exact Debian builds, their hashes, the
public baseline tag and commit, target package release, and output paths. The
target release's upstream tag is not read. `matched-artifact-hunks.json` records
each before-side hunk-to-source mapping. `unmatched-artifact-hunks.json` retains
changed text hunks for which no unique deterministic baseline-source mapping was
found.

## Manual mode

Use `source-extract-manual` only when you already have a specific package
inspection and need to inspect its mapping behaviour:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract-manual \
  zm-ajax --tag 10.1.20 --inspection-directory /results/deb-package-inspections/<package>/<comparison>
```

The normal `source-extract` command is preferred because it creates the package
inspection and source extraction from the two release inputs in one operation.
