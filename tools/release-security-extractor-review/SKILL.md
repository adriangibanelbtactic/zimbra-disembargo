# Security source-extractor release review

Use this playbook to investigate a Zimbra release's announced security fixes and
add deterministic source extractors. It is intended to be handed directly to an
investigating agent with the target and previous release labels.

## Inputs

Use all three sources and retain their boundaries in the final review:

1. The output of `ubuntu24-debian-non-patch-packages-pseudo-code-analysis` for
   the target package comparison. It establishes the installed package artifact
   that actually changed.
2. The release announcement's **Security Fixes** table. Make one result row for
   every entry, including entries without a CVE.
3. The public Zimbra upstream repositories selected by `zm-build` at the target
   release tag and the preceding release tag.

## Upstream survey

Run the bundled survey with explicit release labels:

```sh
tools/release-security-extractor-review/survey-zimbra-upstream-tags \
  <previous-release> <target-release>
```

It invokes `zm-build-print-repos.pl` from `maldua/zimbra-tag-helper` at each
corresponding `zm-build` tag. Read `tag-status.tsv` before interpreting an
absent source diff: a repository without one of the tags cannot prove that a
fix was absent.

For repositories with both tags, review `changes/*/log.tsv` and
`changes/*/names.tsv`, then inspect only changes that plausibly correspond to
the announced security-fix description.

## Package comparison

Start or refresh the Ubuntu 24 environment only when it is safe to use its
fixed-name container, then refresh the catalogue and run the candidate
extractor:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis catalog
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract \
  <extractor-name> <previous-release> <target-release>
```

If package builds are no longer in APT metadata, record that fact. Do not claim
that an extractor ran successfully merely because the public upstream diff
exists.

## Decision rule

Create an extractor only when all of the following hold:

- one non-patch Debian package contains the changed artifact;
- that artifact is text, not a JAR/class/binary payload;
- its upstream repository and candidate source scope are explicit; and
- the extractor's exact before-side hunk matching can locate one source path.

Do not create an extractor based only on a CVE description or a plausible
upstream commit. Compiled Java in JARs, patch-package-only changes, unavailable
package builds, missing public tags, and ambiguous matches are valid **not
created** results. Preserve those reasons rather than guessing source paths.

## Deliverables

1. Add each supported JSON definition under `source-extractors/`. There must
   be exactly one definition for each upstream GitHub repository; extend its
   artifact scope and mappings for subsequent release candidates.
2. Add or update a release review document with a row for every announced
   security fix: CVE (or `TBD`), announcement focus, created/not created, and
   the evidence or boundary.
3. Validate all definitions:

   ```sh
   python3 tests/test-source-extractor-definitions.py
   python3 tests/test-ubuntu24-source-extract.py
   python3 tests/test-ubuntu24-source-extract-wrapper.py
   ```

4. When historical packages are unavailable, synthetically validate a new
   definition from the before/after upstream text only as a definition test.
   Label it clearly as synthetic; it is not an NE package extraction.

Never commit Network Edition packages, extracted payloads, or cached upstream
repositories. `cache/` and `var/` are intentionally ignored.
