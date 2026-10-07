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

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

[foss-releases]: https://wiki.zimbra.com/wiki/Zimbra_Foss_Source_Code_Only_Releases
[zimbra-foss-discussion]: https://github.com/maldua/zimbra-foss/discussions/20#discussioncomment-13879644
[zimbra-github]: https://github.com/Zimbra

[^zimbra-foss]: See the linked discussion for a maintainer's explanation of
    embargoed and missing commits, and their impact on FOSS builds.
