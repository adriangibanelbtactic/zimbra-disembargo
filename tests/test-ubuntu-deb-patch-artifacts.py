#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-deb-package-inspect"
loader = importlib.machinery.SourceFileLoader("ubuntu24_deb_package_inspect", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    before_payload = temporary / "before" / "payload"
    after_payload = temporary / "after" / "payload"
    before_patches = before_payload / "opt/zimbra/lib/patches"
    after_patches = after_payload / "opt/zimbra/lib/patches"
    before_patches.mkdir(parents=True)
    after_patches.mkdir(parents=True)
    (before_patches / "zmcontrol").write_bytes(b"before\x00payload\n")
    (after_patches / "zmcontrol").write_bytes(b"after\x00payload\n")
    (before_patches / "unchanged").write_text("same\n", encoding="utf-8")
    (after_patches / "unchanged").write_text("same\n", encoding="utf-8")
    (before_patches / "before-only").write_text("old\n", encoding="utf-8")
    (after_patches / "after-only").write_text("new\n", encoding="utf-8")
    (before_patches / "symlink").symlink_to("zmcontrol")

    before = module.inventory_patch_artifacts(before_payload)
    after = module.inventory_patch_artifacts(after_payload)
    assert sorted(before) == [
        "opt/zimbra/lib/patches/before-only",
        "opt/zimbra/lib/patches/unchanged",
        "opt/zimbra/lib/patches/zmcontrol",
    ]
    assert "opt/zimbra/lib/patches/symlink" not in before
    changed = module.changed_patch_artifacts(before, after)
    assert [after_artifact.relative_path for _, after_artifact in changed] == ["opt/zimbra/lib/patches/zmcontrol"]

    result = temporary / "result"
    result.mkdir()
    (result / "manifest.json").write_text("{}\n", encoding="utf-8")
    diff = module.write_artifact_diff(result, before_payload, after_payload, changed[0])
    assert diff == result / "artifact-diffs/opt/zimbra/lib/patches/zmcontrol.diff"
    assert diff.is_file()
    manifest = json.loads((result / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["selected_artifact"]["path"] == "opt/zimbra/lib/patches/zmcontrol"
    assert manifest["selected_artifact"]["binary_diff"] == "artifact-diffs/opt/zimbra/lib/patches/zmcontrol.diff"
