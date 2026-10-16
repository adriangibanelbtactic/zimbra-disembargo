#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import json
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
        before_individual = inspection / "before" / "payload" / "etc"
        after_individual = inspection / "after" / "payload" / "etc"
        before_individual.mkdir(parents=True)
        after_individual.mkdir(parents=True)
        (before_individual / "individual.txt").write_text("before\n", encoding="utf-8")
        (after_individual / "individual.txt").write_text("after\n", encoding="utf-8")
        return inspection, []

    definitions = temporary / "definitions"
    definitions.mkdir()
    (definitions / "example.json").write_text(
        json.dumps({"mappings": [{"package": "zimbra-example", "artifact-root": "opt/zimbra"}]}),
        encoding="utf-8",
    )
    assert module.artifact_roots(definitions) == {"zimbra-example": ["opt/zimbra"]}
    assert module.artifact_root_for_path(module.artifact_roots(definitions), "zimbra-example", "opt/zimbra/changed.txt") == "opt/zimbra"

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
    assert manifest["text_artifacts"] == 12
    assert manifest["text_diffs"] == 6
    assert manifest["skipped_packages"] == skipped
    assert all(len(item["text_artifacts"]) == 6 for item in report["comparisons"])
    paths = {item["path"] for item in report["comparisons"][0]["text_artifacts"]}
    assert paths == {
        "etc/individual.txt", "opt/zimbra/added.json", "opt/zimbra/changed.txt", "opt/zimbra/removed.conf",
        "usr/share/second.txt", "usr/share/unmapped.txt",
    }
    groups = report["comparisons"][0]["directory_diff_groups"]
    assert [(group["grouping"], group["directory"], group["artifacts"]) for group in groups] == [
        ("parent-directory", "usr/share", ["usr/share/second.txt", "usr/share/unmapped.txt"]),
        ("source-extractor-artifact-root", "opt/zimbra", ["opt/zimbra/added.json", "opt/zimbra/changed.txt", "opt/zimbra/removed.conf"]),
    ]
    assert not list(output.rglob("*.bin.diff"))
    diffs = list((output / "diffs").glob("*.diff"))
    assert len(diffs) == 6
    assert all(diff.parent == output / "diffs" for diff in diffs)
    grouped = output / groups[0]["diff"]
    assert "--- before/usr/share/second.txt" in grouped.read_text(encoding="utf-8")
    assert "+++ after/usr/share/unmapped.txt" in grouped.read_text(encoding="utf-8")
    source_grouped = output / groups[1]["diff"]
    assert "--- before/opt/zimbra/changed.txt" in source_grouped.read_text(encoding="utf-8")
    assert "+++ after/opt/zimbra/added.json" in source_grouped.read_text(encoding="utf-8")
    assert any("etc%2Findividual.txt.diff" in diff.name for diff in diffs)
