#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-deb-non-patch-package-inspect"
loader = importlib.machinery.SourceFileLoader("ubuntu24_deb_non_patch_package_inspect", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    first_index = temporary / "1010_Packages"
    second_index = temporary / "1010-ne_Packages"
    first_index.write_text(
        """Package: zimbra-common-core
Version: 1.0-1.u24
Architecture: amd64

Package: zimbra-patch
Version: 1.0-1.u24
Architecture: amd64

Package: zimbra-common-core
Version: 2.0-1.u24
Architecture: amd64
""",
        encoding="utf-8",
    )
    second_index.write_text(
        """Package: zimbra-common-core
Version: 2.0-1.u24
Architecture: amd64

Package: zimbra-mta-patch
Version: 2.0-1.u24
Architecture: amd64
""",
        encoding="utf-8",
    )
    packages, metadata = module.catalogue_from_indexes(
        [
            ("https://repo.zimbra.com/apt/1010/dists/noble/zimbra/binary-amd64/Packages", first_index),
            ("https://repo.zimbra.com/apt/1010-ne/dists/noble/zimbra/binary-amd64/Packages", second_index),
        ]
    )
    assert list(packages) == ["zimbra-common-core"]
    assert [package.version for package in packages["zimbra-common-core"]] == ["1.0-1.u24", "2.0-1.u24"]
    assert packages["zimbra-common-core"][1].sources == (
        "https://repo.zimbra.com/apt/1010-ne/dists/noble/zimbra/binary-amd64/Packages",
        "https://repo.zimbra.com/apt/1010/dists/noble/zimbra/binary-amd64/Packages",
    )
    assert [item["package_records"] for item in metadata] == [3, 2]
    assert module.is_patch_package("zimbra-patch")
    assert module.is_patch_package("zimbra-mta-patch")
    assert not module.is_patch_package("zimbra-common-core")

    compressed_index = temporary / "1010-ne_Packages.lz4"
    compressed_index.write_bytes(module.LZ4_FRAME_MAGIC + b"placeholder")
    original_run = module.run

    def fake_lz4_run(command, **kwargs):
        assert command == ["lz4", "--decompress", "--stdout", str(compressed_index)]
        assert kwargs == {"capture_output": True}
        return subprocess.CompletedProcess(
            command, 0, stdout="Package: zimbra-from-lz4\nVersion: 1.0-1.u24\nArchitecture: amd64\n"
        )

    module.run = fake_lz4_run
    try:
        assert module.package_index_records(compressed_index) == [("zimbra-from-lz4", "1.0-1.u24", "amd64")]
    finally:
        module.run = original_run

    before_payload = temporary / "before" / "payload"
    after_payload = temporary / "after" / "payload"
    (before_payload / "usr/bin").mkdir(parents=True)
    (after_payload / "usr/bin").mkdir(parents=True)
    (before_payload / "usr/bin/zimbra-tool").write_bytes(b"before\x00payload\n")
    (after_payload / "usr/bin/zimbra-tool").write_bytes(b"after\x00payload\n")
    (before_payload / "opt/zimbra/lib").mkdir(parents=True)
    (after_payload / "opt/zimbra/lib").mkdir(parents=True)
    (before_payload / "opt/zimbra/lib/unchanged").write_text("same\n", encoding="utf-8")
    (after_payload / "opt/zimbra/lib/unchanged").write_text("same\n", encoding="utf-8")
    (before_payload / "usr/bin/symlink").symlink_to("zimbra-tool")

    before = module.inventory_package_artifacts(before_payload)
    after = module.inventory_package_artifacts(after_payload)
    assert sorted(before) == ["opt/zimbra/lib/unchanged", "usr/bin/zimbra-tool"]
    assert "usr/bin/symlink" not in before
    changed = module.changed_package_artifacts(before, after)
    assert [after_artifact.relative_path for _, after_artifact in changed] == ["usr/bin/zimbra-tool"]
