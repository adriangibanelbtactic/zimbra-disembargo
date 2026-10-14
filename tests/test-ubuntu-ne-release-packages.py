#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import io
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu-ne-release-packages"
loader = importlib.machinery.SourceFileLoader("ubuntu_ne_release_packages", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


manifest = module.read_manifest(ROOT / "manifests/ne-releases/10.1.0-ubuntu18.json", "10.1.0", "18")
assert manifest["archive"]["url"].endswith("UBUNTU18_64.20240610085557.tgz")
assert manifest["archive"]["md5"] == "21b87d5e3db90ec68c77cbc4e0238e26"

with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    archive = temporary / "installer.tgz"
    with tarfile.open(archive, "w:gz") as output:
        for name, contents in {
            "zcs-test/packages/Packages": b"Package: zimbra-test\nVersion: 1\nArchitecture: amd64\n",
            "zcs-test/packages/zimbra-test_1_amd64.deb": b"not a real package",
        }.items():
            member = tarfile.TarInfo(name)
            member.size = len(contents)
            output.addfile(member, io.BytesIO(contents))
    packages = temporary / "cache" / "zcs-test" / "packages"
    module.extract_packages(archive, packages)
    assert (packages / "Packages").is_file()
    assert (packages / "zimbra-test_1_amd64.deb").read_bytes() == b"not a real package"

    unsafe = temporary / "unsafe.tgz"
    with tarfile.open(unsafe, "w:gz") as output:
        member = tarfile.TarInfo("zcs-test/packages/outside")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        output.addfile(member)
    try:
        module.extract_packages(unsafe, temporary / "unsafe-cache" / "packages")
    except module.ReleaseError:
        pass
    else:
        raise AssertionError("a package symlink must be rejected")
