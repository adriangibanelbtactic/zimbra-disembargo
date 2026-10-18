#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-non-patch-release-text-diffs"
loader = importlib.machinery.SourceFileLoader("ubuntu24_non_patch_release_text_diffs", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


package = module.INSPECTOR.DebianPackage
catalogue = {
    "zimbra-example": [
        package("zimbra-example", "10.1.20.1-1.u24", "amd64", ("test",)),
        package("zimbra-example", "10.1.21.1-1.u24", "amd64", ("test",)),
        package("zimbra-example", "10.1.21.2-1.u24", "amd64", ("test",)),
    ],
    "zimbra-no-baseline": [
        package("zimbra-no-baseline", "10.1.21.1-1.u24", "amd64", ("test",)),
    ],
}
comparisons, skipped = module.release_comparisons(catalogue, "10.1.20", "10.1.21")
assert [(before.version, after.version) for before, after in comparisons] == [
    ("10.1.20.1-1.u24", "10.1.21.1-1.u24"),
    ("10.1.20.1-1.u24", "10.1.21.2-1.u24"),
]
assert skipped == [{
    "package": "zimbra-no-baseline",
    "after_versions": ["10.1.21.1-1.u24"],
    "reason": "no retained build for requested before release 10.1.20",
}]
assert module.previous_release(catalogue, "10.1.21") == "10.1.20"
assert module.selected_releases(catalogue, "10.1.21", None) == ("10.1.20", "10.1.21")
assert module.selected_releases(catalogue, "10.1.20", "10.1.21") == ("10.1.20", "10.1.21")
assert module.is_text_mime("text/plain")
assert module.is_text_mime("application/javascript")
assert not module.is_text_mime("application/octet-stream")
template_hunk = module.MANUAL.Hunk(
    "@@ -1 +1 @@",
    ('defaultValue:"20260707-0941"\n',),
    ('defaultValue:"20260916-0520"\n',),
    '@@ -1 +1 @@\n-defaultValue:"20260707-0941"\n+defaultValue:"20260916-0520"\n',
)
assert module.template_hunk_matches(
    template_hunk,
    ('defaultValue:"@buildDateTime@"\n',),
    {"@buildDateTime@": "release-specific build date"},
) == [0]
assert b"--- before/example.js" in module.raw_hunk_patch("example.js", template_hunk)
project_mappings = module.source_extractor_mappings(ROOT / "source-extractors")
for generated_artifact in (
    "opt/zimbra/jetty_base/etc/zimbra.web.xml.in",
    "opt/zimbra/jetty_base/webapps/zimbra/WEB-INF/web.xml",
):
    generated_mapping = module.generated_mapping_for_artifact(
        project_mappings, "zimbra-mbox-webclient-war", generated_artifact
    )
    assert generated_mapping is not None
    assert generated_mapping["derivation"] == {
        "type": "template-substitution",
        "source": "WebRoot/WEB-INF/web.xml",
        "substitutions": {"@jsVersion@": "release-specific JavaScript cache-buster value"},
    }
preferences_mapping = module.bundle_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Preferences_all.js",
)
assert preferences_mapping is not None
assert preferences_mapping["derivation"] == {
    "type": "ajx-package-bundle",
    "manifest": "WebRoot/js/zimbraMail/package/Preferences.js",
    "template-substitution": None,
}
share_mapping = module.bundle_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Share_all.js",
)
assert share_mapping is not None
assert share_mapping["derivation"] == {
    "type": "ajx-package-bundle",
    "manifest": "WebRoot/js/zimbraMail/package/Share.js",
    "template-substitution": None,
}
startup_mapping = module.bundle_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Startup1_2_all.js",
)
assert startup_mapping is not None
assert startup_mapping["derivation"]["manifest"] == "WebRoot/js/zimbraMail/package/Startup1_2.js"
assert startup_mapping["derivation"]["template-substitution"]["source"] == "WebRoot/js/zimbraMail/share/model/ZmSettings.js"
tasks_mapping = module.bundle_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Tasks_all.js",
)
assert tasks_mapping is not None
assert tasks_mapping["derivation"]["manifest"] == "WebRoot/js/zimbraMail/package/Tasks.js"
assert module.upstream_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/mail/model/ZmMailMsg.js",
) == {
    "github_repository": "Zimbra/zm-web-client",
    "repository": "zm-web-client",
    "selection": "exact-artifact",
}
assert module.upstream_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Ajax_all.js",
) == {
    "github_repository": "Zimbra/zm-ajax",
    "repository": "zm-ajax",
    "selection": "exact-artifact",
}
login_mapping = module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/public/login.jsp",
)
assert login_mapping is not None
assert login_mapping["upstream_path"] == "WebRoot/public/login.jsp"
assert module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/Ajax_all.js",
) is None
mail_message_mapping = module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/mail/model/ZmMailMsg.js",
)
assert mail_message_mapping is not None
assert mail_message_mapping["upstream_path"] == "WebRoot/js/zimbraMail/mail/model/ZmMailMsg.js"
compose_mapping = module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/mail/view/ZmComposeView.js",
)
assert compose_mapping is not None
assert compose_mapping["upstream_path"] == "WebRoot/js/zimbraMail/mail/view/ZmComposeView.js"
sharing_page_mapping = module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/prefs/view/ZmSharingPage.js",
)
assert sharing_page_mapping is not None
assert sharing_page_mapping["upstream_path"] == "WebRoot/js/zimbraMail/prefs/view/ZmSharingPage.js"
settings_template_mapping = module.generated_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/share/model/ZmSettings.js",
)
assert settings_template_mapping is not None
assert settings_template_mapping["derivation"]["source"] == "WebRoot/js/zimbraMail/share/model/ZmSettings.js"
accept_share_mapping = module.direct_source_mapping_for_artifact(
    project_mappings,
    "zimbra-mbox-webclient-war",
    "opt/zimbra/jetty_base/webapps/zimbra/js/zimbraMail/share/view/dialog/ZmAcceptShareDialog.js",
)
assert accept_share_mapping is not None
assert accept_share_mapping["upstream_path"] == "WebRoot/js/zimbraMail/share/view/dialog/ZmAcceptShareDialog.js"
sequences = {}
assert module.generated_diff_filename({"github_repository": "Zimbra/zm-web-client", "repository": "zm-web-client"}, "10.1.21", sequences) == "zm-web-client-10.1.21-generated-changes_001.diff"
assert module.generated_diff_filename({"github_repository": "Zimbra/zm-web-client", "repository": "zm-web-client"}, "10.1.21", sequences) == "zm-web-client-10.1.21-generated-changes_002.diff"
assert module.generated_diff_filename({"github_repository": "Zimbra/zm-web-client", "repository": "zm-web-client"}, "10.1.21", sequences, "orphan-changes") == "zm-web-client-10.1.21-orphan-changes_003.diff"


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    before = temporary / "before.txt"
    after = temporary / "after.txt"
    before.write_text("before\n", encoding="utf-8")
    after.write_text("after\n", encoding="utf-8")
    diff = temporary / "changed.diff"
    module.write_unified_diff(diff, "opt/zimbra/example.txt", before, after)
    contents = diff.read_text(encoding="utf-8")
    assert "--- before/opt/zimbra/example.txt" in contents
    assert "+after" in contents

    added = temporary / "added.diff"
    module.write_unified_diff(added, "opt/zimbra/added.txt", None, after)
    assert "--- before/opt/zimbra/added.txt" in added.read_text(encoding="utf-8")

    bundle_upstream = temporary / "bundle-upstream"
    bundle_upstream.mkdir()
    subprocess.run(["git", "init"], cwd=bundle_upstream, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.test"], cwd=bundle_upstream, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=bundle_upstream, check=True)
    source = bundle_upstream / "WebRoot/js/zimbraMail/mail/model/ZmMailMsg.js"
    manifest = bundle_upstream / "WebRoot/js/zimbraMail/package/MailCore.js"
    source.parent.mkdir(parents=True)
    manifest.parent.mkdir(parents=True)
    source.write_text("function attachment() {\n\tuseCL = attach.contentLocation && true;\n}\n", encoding="utf-8")
    manifest.write_text('AjxPackage.require("zimbraMail.mail.model.ZmMailMsg");\n', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=bundle_upstream, check=True)
    subprocess.run(["git", "commit", "-m", "before"], cwd=bundle_upstream, check=True, capture_output=True)
    subprocess.run(["git", "tag", "10.1.20"], cwd=bundle_upstream, check=True)
    bundle_before = temporary / "MailCore_all.before.js"
    bundle_after = temporary / "MailCore_all.after.js"
    bundle_before.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    bundle_after.write_text(
        "function attachment() {\n\tuseCL = attach.contentLocation && true;\n\tattach.contentLocation = null;\n}\n",
        encoding="utf-8",
    )
    reconstruction = module.reconstruct_bundle_diff(
        {
            "github_repository": "Example/zm-web-client",
            "url": str(bundle_upstream),
            "repository": "zm-web-client",
            "source_roots": ["WebRoot/js/zimbraMail"],
            "derivation": {"type": "ajx-package-bundle", "manifest": "WebRoot/js/zimbraMail/package/MailCore.js"},
        },
        {"before_path": bundle_before, "after_path": bundle_after},
        "10.1.20",
        "10.1.21",
        temporary / "bundle-cache",
    )
    assert reconstruction["baseline"] == "10.1.20"
    assert reconstruction["sources"] == ["WebRoot/js/zimbraMail/mail/model/ZmMailMsg.js"]
    assert reconstruction["matched_hunks"] == 1
    assert not reconstruction["unmatched_hunks"]
    assert b"+\tattach.contentLocation = null;" in reconstruction["patch"]

    original_catalogue = module.INSPECTOR.write_catalogue
    original_compare = module.INSPECTOR.compare

    def fake_catalogue(destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("{}\n", encoding="utf-8")
        return catalogue

    def fake_compare(before_package, after_package, results_directory, catalogue_path):
        inspection = results_directory / after_package.name / f"{before_package.version}__to__{after_package.version}"
        before_payload = inspection / "before" / "payload" / "opt" / "zimbra"
        after_payload = inspection / "after" / "payload" / "opt" / "zimbra"
        before_payload.mkdir(parents=True)
        after_payload.mkdir(parents=True)
        (before_payload / "changed.txt").write_text("before\n", encoding="utf-8")
        (after_payload / "changed.txt").write_text("after\n", encoding="utf-8")
        (before_payload / "removed.conf").write_text("remove\n", encoding="utf-8")
        (after_payload / "added.json").write_text('{"added": true}\n', encoding="utf-8")
        (before_payload / "binary.bin").write_bytes(b"before\x00")
        (after_payload / "binary.bin").write_bytes(b"after\x00")
        before_unmapped = inspection / "before" / "payload" / "usr" / "share"
        after_unmapped = inspection / "after" / "payload" / "usr" / "share"
        before_unmapped.mkdir(parents=True)
        after_unmapped.mkdir(parents=True)
        (before_unmapped / "unmapped.txt").write_text("before\n", encoding="utf-8")
        (after_unmapped / "unmapped.txt").write_text("after\n", encoding="utf-8")
        (before_unmapped / "second.txt").write_text("before\n", encoding="utf-8")
        (after_unmapped / "second.txt").write_text("after\n", encoding="utf-8")
        (before_unmapped / "generated.java").write_text("class Before {}\n", encoding="utf-8")
        (after_unmapped / "generated.java").write_text("class After {}\n", encoding="utf-8")
        before_individual = inspection / "before" / "payload" / "etc"
        after_individual = inspection / "after" / "payload" / "etc"
        before_individual.mkdir(parents=True)
        after_individual.mkdir(parents=True)
        (before_individual / "individual.txt").write_text("before\n", encoding="utf-8")
        (after_individual / "individual.txt").write_text("after\n", encoding="utf-8")
        (before_individual / "generated.xml").write_text("<version>before</version>\n", encoding="utf-8")
        (after_individual / "generated.xml").write_text("<version>after</version>\n", encoding="utf-8")
        return inspection, []

    definitions = temporary / "definitions"
    definitions.mkdir()
    (definitions / "example.json").write_text(
        json.dumps(
            {
                "upstream": {"github_repository": "Example/example"},
                "filter-negative": [".java"],
                "mappings": [
                    {"package": "zimbra-example", "artifact-root": "opt/zimbra", "source-root": "src/zimbra"},
                    {
                        "package": "zimbra-example",
                        "artifact": "etc/individual.txt",
                        "source-roots": ["WebRoot/public"],
                    },
                    {
                        "package": "zimbra-example",
                        "artifact": "etc/generated.xml",
                        "source-roots": ["WebRoot/WEB-INF"],
                        "derivation": {
                            "type": "template-substitution",
                            "source": "WebRoot/WEB-INF/web.xml",
                            "substitutions": {"@version@": "generated release value"},
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    assert module.artifact_roots(definitions) == {"zimbra-example": ["opt/zimbra"]}
    assert module.shared_negative_filters(definitions) == [".java"]
    assert module.artifact_root_for_path(module.artifact_roots(definitions), "zimbra-example", "opt/zimbra/changed.txt") == "opt/zimbra"
    root_source = module.root_source_mapping_for_artifact(
        module.source_extractor_mappings(definitions), "zimbra-example", "opt/zimbra/changed.txt"
    )
    assert root_source is not None
    assert module.upstream_path_for_artifact(root_source, "opt/zimbra/changed.txt") == "src/zimbra/changed.txt"
    direct_source = module.direct_source_mapping_for_artifact(
        module.source_extractor_mappings(definitions), "zimbra-example", "etc/individual.txt"
    )
    assert direct_source is not None
    assert direct_source["source_root"] == "WebRoot/public"
    assert direct_source["upstream_path"] == "WebRoot/public/individual.txt"
    assert module.direct_source_mapping_for_artifact(
        {
            "zimbra-example": [{
                "artifact": "usr/share/unmapped.txt",
                "source_roots": ["WebRoot/generated"],
                "derivation": True,
            }]
        },
        "zimbra-example",
        "usr/share/unmapped.txt",
    ) is None
    generated_mapping = module.generated_mapping_for_artifact(
        module.source_extractor_mappings(definitions), "zimbra-example", "etc/generated.xml"
    )
    assert generated_mapping is not None
    assert generated_mapping["derivation"]["source"] == "WebRoot/WEB-INF/web.xml"
    assert module.upstream_for_artifact(module.source_extractor_mappings(definitions), "zimbra-example", "usr/share/unmapped.txt") == {
        "github_repository": "Example/example",
        "repository": "example",
        "selection": "package-primary",
    }

    module.INSPECTOR.write_catalogue = fake_catalogue
    module.INSPECTOR.compare = fake_compare
    try:
        output = module.create_release_text_diffs("10.1.21", None, temporary / "results", definitions=definitions)
    finally:
        module.INSPECTOR.write_catalogue = original_catalogue
        module.INSPECTOR.compare = original_compare

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads((output / "text-artifacts.json").read_text(encoding="utf-8"))
    assert output.name == "10.1.21"
    assert manifest["comparisons"] == 2
    assert manifest["text_artifacts"] == 14
    assert manifest["binary_package_diffs"] == 6
    assert manifest["binary_only_diffs"] == 4
    assert manifest["template_diffs"] == 2
    assert manifest["upstream_diffs"] == 4
    assert manifest["excluded_by_source_extractor_filters"] == 2
    assert manifest["skipped_packages"] == skipped
    assert all(len(item["text_artifacts"]) == 7 for item in report["comparisons"])
    paths = {item["path"] for item in report["comparisons"][0]["text_artifacts"]}
    assert paths == {
        "etc/generated.xml", "etc/individual.txt", "opt/zimbra/added.json", "opt/zimbra/changed.txt", "opt/zimbra/removed.conf",
        "usr/share/second.txt", "usr/share/unmapped.txt",
    }
    groups = report["comparisons"][0]["directory_diff_groups"]
    assert {(group["grouping"], group["directory"], tuple(group["artifacts"])) for group in groups} == {
        ("parent-directory", "etc", ("etc/generated.xml", "etc/individual.txt")),
        ("parent-directory", "usr/share", ("usr/share/second.txt", "usr/share/unmapped.txt")),
        ("source-extractor-artifact-root", "opt/zimbra", ("opt/zimbra/added.json", "opt/zimbra/changed.txt", "opt/zimbra/removed.conf")),
    }
    assert not list(output.rglob("*.bin.diff"))
    assert "generated.java" not in json.dumps(report)
    diffs = list((output / "binary_packages_diffs").glob("*.diff"))
    assert len(diffs) == 6
    assert all(diff.parent == output / "binary_packages_diffs" for diff in diffs)
    assert {diff.name for diff in diffs} == {
        f"example-10.1.21-generated-changes_{number:03d}.diff"
        for number in range(1, 7)
    }
    groups_by_kind = {group["grouping"]: group for group in groups}
    grouped = output / groups_by_kind["parent-directory"]["binary_package_diff"]
    assert "--- before/usr/share/second.txt" in grouped.read_text(encoding="utf-8")
    assert "+++ after/usr/share/unmapped.txt" in grouped.read_text(encoding="utf-8")
    source_grouped = output / groups_by_kind["source-extractor-artifact-root"]["binary_package_diff"]
    assert "--- before/opt/zimbra/changed.txt" in source_grouped.read_text(encoding="utf-8")
    assert "+++ after/opt/zimbra/added.json" in source_grouped.read_text(encoding="utf-8")
    upstream_groups = report["comparisons"][0]["upstream_diff_groups"]
    upstream_group = next(group for group in upstream_groups if group["mapping"] == "artifact-root/source-root")
    assert upstream_group["artifact_root"] == "opt/zimbra"
    assert upstream_group["source_root"] == "src/zimbra"
    upstream_diff = output / upstream_group["upstream_diff"]
    assert "--- before/src/zimbra/changed.txt" in upstream_diff.read_text(encoding="utf-8")
    assert "+++ after/src/zimbra/added.json" in upstream_diff.read_text(encoding="utf-8")
    direct_group = next(group for group in upstream_groups if group["mapping"] == "artifact/source-roots")
    assert direct_group["artifact"] == "etc/individual.txt"
    direct_diff = output / direct_group["upstream_diff"]
    assert "--- before/WebRoot/public/individual.txt" in direct_diff.read_text(encoding="utf-8")
    assert "+++ after/WebRoot/public/individual.txt" in direct_diff.read_text(encoding="utf-8")
    artifacts_by_path = {item["path"]: item for item in report["comparisons"][0]["text_artifacts"]}
    assert artifacts_by_path["opt/zimbra/changed.txt"]["upstream_path"] == "src/zimbra/changed.txt"
    assert artifacts_by_path["opt/zimbra/changed.txt"]["upstream_diff"] is not None
    assert artifacts_by_path["opt/zimbra/changed.txt"]["binary_only_diff"] is None
    assert artifacts_by_path["etc/individual.txt"]["upstream_path"] == "WebRoot/public/individual.txt"
    assert artifacts_by_path["etc/individual.txt"]["upstream_diff"] is not None
    assert artifacts_by_path["etc/individual.txt"]["binary_only_diff"] is None
    generated = artifacts_by_path["etc/generated.xml"]
    assert generated["template_diff"] is not None
    assert generated["binary_only_diff"] is None
    assert generated["upstream_diff"] is None
    assert generated["generated"]["source"] == "WebRoot/WEB-INF/web.xml"
    template_diffs = list((output / "template_diffs").glob("*.diff"))
    assert len(template_diffs) == 2
    assert all("-template-changes_" in diff.name for diff in template_diffs)
    assert "generated_diff" not in generated
    assert not (output / "generated_diffs").exists()
    assert len(list((output / "binary_only_diffs").glob("*.diff"))) == 4
    assert all("-orphan-changes_" in diff.name for diff in (output / "binary_only_diffs").glob("*.diff"))
    assert all("-upstream-changes_" in diff.name for diff in (output / "upstream_diffs").glob("*.diff"))
    assert all(item["upstream"]["github_repository"] == "Example/example" for item in report["comparisons"][0]["text_artifacts"])
