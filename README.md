# Zimbra Disembargo

Zimbra Disembargo helps identify changes that appear in Zimbra's public source
repositories after a Zimbra Network Edition (NE) release. Its primary purpose
is to make it faster to find and review delayed changes, especially security
fixes.

## Why this exists

Zimbra's FOSS source does not always become available at the same time as its
corresponding NE release. The community-maintained [Zimbra FOSS Source Code
Only Releases][foss-releases] page records releases whose source was delayed,
and describes embargoes that usually last 60 days. The maintainers of
`zimbra-foss` have also documented cases where delayed or missing commits make
FOSS releases difficult to build.[^zimbra-foss]

This project compares publicly available source history so that newly published
changes can be found and assessed promptly. It does **not** provide access to
NE source code, private repositories, or embargoed changes.

## What it does

The tool is intended to:

- watch the public Zimbra source repositories and release tags;
- detect changes that become public after an NE release;
- highlight changes that may be relevant to security review; and
- provide enough context for maintainers and downstream builders to investigate
  those changes.

Finding a change is not a security advisory, a determination of exploitability,
or a substitute for reviewing upstream advisories and applying appropriate
updates.

## What open source means here

This project works with Zimbra Collaboration FOSS Edition source code and other
components that their respective copyright holders have made publicly available
under their own licenses. Open source availability applies only to the material
actually published under those licenses; it does not grant access to Zimbra NE
components or to source that has not yet been made public.

We use only lawfully obtained, public material. Nothing in this project is
intended to bypass a license, access restriction, or technical protection
measure, or to obtain non-public source code. Where analysis of a publicly
available binary or interface is lawful, it must remain within the applicable
law and the rights granted by the relevant licence. This README is an
explanation of the project's scope, not legal advice.

Zimbra and Zimbra Collaboration are trademarks of their respective owners.
This is an independent community project and is not affiliated with, endorsed
by, or supported by Zimbra or Synacor.

## References

- [Zimbra FOSS Source Code Only Releases][foss-releases]
- [Zimbra FOSS discussion: “How frequently will we receive patch updates for
  ZCS FOSS?”][zimbra-foss-discussion]
- [Zimbra's public GitHub organisation][zimbra-github]

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

[foss-releases]: https://wiki.zimbra.com/wiki/Zimbra_Foss_Source_Code_Only_Releases
[zimbra-foss-discussion]: https://github.com/maldua/zimbra-foss/discussions/20#discussioncomment-13879644
[zimbra-github]: https://github.com/Zimbra

[^zimbra-foss]: See the linked discussion for a maintainer's explanation of
    embargoed and missing commits, and their impact on FOSS builds.
