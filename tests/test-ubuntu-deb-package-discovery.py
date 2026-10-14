#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-deb-package-inspect"
loader = importlib.machinery.SourceFileLoader("ubuntu24_deb_package_discovery", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


targets = module.parse_index_targets(
    "Packages\thttps://repo.zimbra.com/apt/1010-ne/dists/noble/zimbra/binary-amd64/Packages\t/var/lib/apt/lists/zimbra\n"
    "Sources\thttps://repo.zimbra.com/apt/1010-ne/dists/noble/zimbra/source/Sources\t/var/lib/apt/lists/sources\n"
    "Packages\thttp://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages\t/var/lib/apt/lists/ubuntu\n"
)
assert targets == [
    (
        "https://repo.zimbra.com/apt/1010-ne/dists/noble/zimbra/binary-amd64/Packages",
        Path("/var/lib/apt/lists/zimbra"),
    )
]

records = module.parse_debian_control(
    """Package: zimbra-example
Version: 10.1.0-1.u24
Architecture: amd64
Filename: pool/zimbra-example.deb

Package: zimbra-common
Version: 10.1.0-1.u24
Architecture: all
Filename: pool/zimbra-common.deb

Package: zimbra-arm
Version: 10.1.0-1.u24
Architecture: arm64
Filename: pool/zimbra-arm.deb
""",
    "https://repo.zimbra.com/apt/1010-ne/index",
)
assert [(record.name, record.architecture) for record in records] == [
    ("zimbra-example", "amd64"),
    ("zimbra-common", "all"),
]
merged = module.merge_packages(records + [records[0].__class__("zimbra-example", "10.1.0-1.u24", "amd64", ("https://repo.zimbra.com/apt/1010/index",))])
assert len(merged) == 2
assert merged[1].sources == (
    "https://repo.zimbra.com/apt/1010-ne/index",
    "https://repo.zimbra.com/apt/1010/index",
)
