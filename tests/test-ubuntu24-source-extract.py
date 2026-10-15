#!/usr/bin/env python3
import hashlib
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-source-extract-manual"
loader = importlib.machinery.SourceFileLoader("ubuntu24_source_extract", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


def run(*arguments: str, cwd: Path) -> None:
    subprocess.run(arguments, cwd=cwd, check=True, capture_output=True)


def write_inventory(path: Path, payload: Path) -> None:
    artifacts = []
    for file in sorted(candidate for candidate in payload.rglob("*") if candidate.is_file()):
        artifacts.append(
            {
                "path": file.relative_to(payload).as_posix(),
                "md5": hashlib.md5(file.read_bytes()).hexdigest(),
                "size": file.stat().st_size,
            }
        )
    path.write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    upstream = temporary / "upstream"
    upstream.mkdir()
    run("git", "init", cwd=upstream)
    run("git", "config", "user.email", "test@example.test", cwd=upstream)
    run("git", "config", "user.name", "Test", cwd=upstream)
    source = upstream / "WebRoot/js/ajax/dwt/widgets/DwtListView.js"
    source.parent.mkdir(parents=True)
    source.write_text("function list() {\n\tbody += cell.innerText;\n}\n", encoding="utf-8")
    run("git", "add", ".", cwd=upstream)
    run("git", "commit", "-m", "before", cwd=upstream)
    run("git", "tag", "10.1.17", cwd=upstream)
    assert "10.1.20" not in subprocess.run(
        ["git", "tag", "--list", "10.1.20"], cwd=upstream, check=True, capture_output=True, text=True
    ).stdout

    definition = temporary / "definitions" / "example.json"
    definition.parent.mkdir()
    definition.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "example",
                "upstream": {"github_repository": "example/zm-ajax", "url": str(upstream)},
                "filter-positive": [],
                "filter-negative": [".jar", ".class", ".java", ".zgz"],
                "mappings": [
                    {
                        "package": "zimbra-mbox-webclient-war",
                        "artifact": "opt/zimbra/jetty_base/webapps/zimbra/js/Ajax_all.js",
                        "source-roots": ["WebRoot/js/ajax"],
                        "source-suffixes": [".js"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    inspection = temporary / "inspection"
    before = inspection / "before" / "payload"
    after = inspection / "after" / "payload"
    artifact = Path("opt/zimbra/jetty_base/webapps/zimbra/js/Ajax_all.js")
    (before / artifact).parent.mkdir(parents=True)
    (after / artifact).parent.mkdir(parents=True)
    (before / artifact).write_text("function list() {\n\tbody += cell.innerText;\n}\n", encoding="utf-8")
    (after / artifact).write_text(
        "function list() {\n\tbody += AjxStringUtil.htmlEncode(cell.innerText);\n}\n", encoding="utf-8"
    )
    (before / "opt/zimbra/readme.txt").parent.mkdir(parents=True, exist_ok=True)
    (after / "opt/zimbra/readme.txt").parent.mkdir(parents=True, exist_ok=True)
    (before / "opt/zimbra/readme.txt").write_text("before\n", encoding="utf-8")
    (after / "opt/zimbra/readme.txt").write_text("after\n", encoding="utf-8")
    (before / "opt/zimbra/ignored.jar").write_text("before\n", encoding="utf-8")
    (after / "opt/zimbra/ignored.jar").write_text("after\n", encoding="utf-8")
    write_inventory(inspection / "before" / "package-artifacts.json", before)
    write_inventory(inspection / "after" / "package-artifacts.json", after)
    (inspection / "manifest.json").write_text(
        json.dumps({"before": {"name": "zimbra-mbox-webclient-war"}, "after": {"name": "zimbra-mbox-webclient-war"}}),
        encoding="utf-8",
    )

    result = module.extract(
        definition, "10.1.20", inspection, temporary / "results", temporary / "cache", before_tag="10.1.17"
    )
    manifest = json.loads((result / "manifest.json").read_text(encoding="utf-8"))
    matched = json.loads((result / "matched-artifact-hunks.json").read_text(encoding="utf-8"))
    unmatched = json.loads((result / "unmatched-artifact-hunks.json").read_text(encoding="utf-8"))
    assert manifest["upstream_baseline"]["baseline"] == "10.1.17"
    assert manifest["upstream_baseline"]["target_release"] == "10.1.20"
    assert not manifest["upstream_baseline"]["target_tag_read"]
    assert manifest["artifact_hunks"]["matched"] == 1
    assert manifest["artifact_hunks"]["unmatched"] == 1
    assert matched["hunks"][0]["artifact"] == artifact.as_posix()
    assert matched["hunks"][0]["source"] == "WebRoot/js/ajax/dwt/widgets/DwtListView.js"
    assert unmatched["hunks"][0]["artifact"] == "opt/zimbra/readme.txt"
    assert "ignored.jar" not in json.dumps(unmatched)
    assert manifest["upstream_diff"] == "upstream.diff"
    assert (result / "upstream.diff").is_file()
    assert (result / "upstream-diffs/WebRoot/js/ajax/dwt/widgets/DwtListView.js.diff").is_file()
    assert "AjxStringUtil.htmlEncode(cell.innerText)" in (result / "upstream.diff").read_text(encoding="utf-8")
    run("git", "apply", "--check", str(result / "upstream.diff"), cwd=upstream)
    scoped_definition = json.loads(definition.read_text(encoding="utf-8"))
    scoped_definition["artifact-positive"] = [artifact.as_posix()]
    definition.write_text(json.dumps(scoped_definition), encoding="utf-8")
    scoped_result = module.extract(
        definition, "10.1.20", inspection, temporary / "results", temporary / "cache", before_tag="10.1.17"
    )
    scoped_manifest = json.loads((scoped_result / "manifest.json").read_text(encoding="utf-8"))
    scoped_unmatched = json.loads((scoped_result / "unmatched-artifact-hunks.json").read_text(encoding="utf-8"))
    assert scoped_manifest["artifact_hunks"]["matched"] == 1
    assert scoped_manifest["artifact_hunks"]["unmatched"] == 0
    assert scoped_manifest["artifact_hunks"]["artifact_positive_excluded_artifacts"] == 2
    assert not scoped_unmatched["hunks"]
    assert module.baseline_tag_for_release(upstream, "10.1.20")[0] == "10.1.17"
