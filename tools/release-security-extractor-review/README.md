# Release security source-extractor tools

These tools package the repeatable public-upstream part of a security
source-extractor investigation. The accompanying agent playbook is
[`SKILL.md`](SKILL.md).

## List selected upstream repositories

```sh
tools/release-security-extractor-review/print-zimbra-build-repositories 10.1.2
```

The command fetches `maldua/zimbra-tag-helper` and `Zimbra/zm-build` into the
ignored `cache/release-security-extractor-review/` directory. It runs the
helper's `zm-build-print-repos.pl` against the requested `zm-build` tag and
prints the selected Zimbra GitHub URLs.

## Survey two release tags

```sh
tools/release-security-extractor-review/survey-zimbra-upstream-tags 10.1.1 10.1.2
```

The command creates a new ignored report directory under
`cache/release-security-extractor-review/surveys/`. It records the source
repository lists for both release tags, checks both tags in every repository in
their union, and records logs and changed paths where both tags exist. Specify
`--output-directory` to write the report elsewhere. The command refuses to
overwrite an existing report.

This survey is evidence for choosing extractor candidates; it cannot replace a
package comparison. Use the established Ubuntu 24 non-patch workflow to verify
the package artifact and run the resulting extractor.

Some patch releases publish component tags but no identically named `zm-build`
tag.  The repository-listing helper automatically selects the nearest preceding
numeric `zm-build` tag; for example, a 10.1.2 survey uses the 10.1.1 build
repository list while it still compares component tags 10.1.1 and 10.1.2:

```sh
tools/release-security-extractor-review/survey-zimbra-upstream-tags 10.1.1 10.1.2
```
