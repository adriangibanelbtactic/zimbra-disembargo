# Ubuntu 24.04 source extractor walkthrough: zm-ajax 10.1.20

This verifies the deterministic `zm-ajax` source extractor in a fresh checkout.
It downloads the required package builds, compares their payloads, locates each
`Ajax_all.js` hunk's before-side text in the public baseline source tree, and
prints one reconstructed upstream-ready Git diff. No `10.1.20` upstream tag,
package catalogue, interactive selection, or package-artifact path is required.

The downloaded packages and results stay under ignored `var/`; do not add them
to Git.

## Run the extraction

Docker Engine must be available to the invoking user. The two named package
releases must still be available in the configured Zimbra APT repositories.

From a new clone, stop a stale fixed-name analysis container if needed:

```sh
if scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis status >/dev/null 2>&1; then
  scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis stop
fi
```

Build and start the environment:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis build
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis start
```

Run the extractor with its name and after release:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis source-extract \
  zm-ajax 10.1.20
```

The command refreshes the package catalogue, selects the newest catalogued
`zimbra-mbox-webclient-war` build for each release, and writes the upstream
diff path to standard output. In a fresh checkout the path is:

```text
var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/
source-extractions/zm-ajax/10.1.17__to__10.1.20/upstream.diff
```

`10.1.18` and `10.1.19` do not exist as `zm-ajax` tags. The extractor therefore
automatically selects `10.1.17` as the public baseline for target package
release `10.1.20`. It does not read an upstream `10.1.20` tag, even if one is
available later. To choose the baseline explicitly, use
`source-extract zm-ajax 10.1.17 10.1.20` instead.

## Verify the diff

Review the output directly from an upstream `zm-ajax` checkout, or inspect it:

```sh
result=var/ubuntu24-debian-non-patch-packages-pseudo-code-analysis/results/source-extractions/zm-ajax/10.1.17__to__10.1.20
less "$result/upstream.diff"
```

It must contain the change in
`WebRoot/js/ajax/dwt/widgets/DwtListView.js`:

```diff
- body +='<td>' + cell.innerText + '</td>';
+ body +='<td>' + AjxStringUtil.htmlEncode(cell.innerText) + '</td>';
```

The associated `manifest.json` records the exact package builds, public
baseline tag commit, target package release, and output locations.
`matched-artifact-hunks.json` shows the deterministic before-side mapping from
the changed `Ajax_all.js` hunk to
`DwtListView.js`; `unmatched-artifact-hunks.json` preserves text hunks that did
not have one unique source match.

Stop the disposable container when finished:

```sh
scripts/ubuntu24-debian-non-patch-packages-pseudo-code-analysis stop
```
