#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu-package-repository-map"
loader = importlib.machinery.SourceFileLoader("ubuntu_package_repository_map", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


catalogue = {
    "schema_version": 1,
    "created_at": "2026-10-14T00:00:00+00:00",
    "source_indexes": [{"uri": "https://repo.zimbra.test/apt/1010-ne/dists/bionic/zimbra/binary-amd64/Packages"}],
    "package_count": 1,
    "packages": [
        {
            "name": "zimbra-mbox-webclient-war",
            "versions": [
                {
                    "version": "10.1.1.1723653022-1.u18",
                    "architecture": "amd64",
                    "sources": ["https://repo.zimbra.test/apt/1010-ne/dists/bionic/zimbra/binary-amd64/Packages"],
                }
            ],
        }
    ],
}

with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    path = temporary / "catalogue.json"
    path.write_text(__import__("json").dumps(catalogue), encoding="utf-8")
    document = module.availability_map({"18": {**module.read_catalogue(path), "catalogue_path": str(path)}})
    assert document["catalogues"]["ubuntu18"]["catalogue"] == str(path)
    package = document["packages"][0]
    assert package["name"] == "zimbra-mbox-webclient-war"
    assert package["availability"] == [{"ubuntu_series": "18", "sources": catalogue["packages"][0]["versions"][0]["sources"]}]

assert module.parse_input("22=/results/ubuntu22/catalogue.json") == ("22", Path("/results/ubuntu22/catalogue.json"))
try:
    module.parse_input("noble=/results/catalogue.json")
except module.MapError:
    pass
else:
    raise AssertionError("an unsupported Ubuntu series must fail")
