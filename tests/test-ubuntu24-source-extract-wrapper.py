#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-source-extract"
loader = importlib.machinery.SourceFileLoader("ubuntu24_source_extract_wrapper", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


package = module.INSPECTOR.DebianPackage
catalogue = {
    "zimbra-mbox-webclient-war": [
        package("zimbra-mbox-webclient-war", "10.1.17.1776247000-1.u24", "amd64", ("test",)),
        package("zimbra-mbox-webclient-war", "10.1.17.1776247073-1.u24", "amd64", ("test",)),
        package("zimbra-mbox-webclient-war", "10.1.20.1783414000-1.u24", "amd64", ("test",)),
        package("zimbra-mbox-webclient-war", "10.1.20.1783414027-1.u24", "amd64", ("test",)),
    ],
    "zimbra-mta-components": [
        package("zimbra-mta-components", "10.1.1-1zimbra8.8b1.18.04", "all", ("test",)),
        package("zimbra-mta-components", "10.1.2-1zimbra8.8b1.18.04", "all", ("test",)),
    ],
}
assert module.package_for_release(catalogue, "zimbra-mbox-webclient-war", "10.1.17").version == "10.1.17.1776247073-1.u24"
assert module.package_for_release(catalogue, "zimbra-mbox-webclient-war", "10.1.20").version == "10.1.20.1783414027-1.u24"
assert [item.version for item in module.packages_for_release(catalogue, "zimbra-mbox-webclient-war", "10.1.20")] == [
    "10.1.20.1783414000-1.u24",
    "10.1.20.1783414027-1.u24",
]
assert module.package_for_release(catalogue, "zimbra-mta-components", "10.1.1").version == "10.1.1-1zimbra8.8b1.18.04"
comparisons = module.package_comparisons(catalogue, "zimbra-mbox-webclient-war", "10.1.17", "10.1.20")
assert [(before.version, after.version) for before, after in comparisons] == [
    ("10.1.17.1776247073-1.u24", "10.1.20.1783414000-1.u24"),
    ("10.1.17.1776247073-1.u24", "10.1.20.1783414027-1.u24"),
    ("10.1.20.1783414000-1.u24", "10.1.20.1783414027-1.u24"),
]
try:
    module.package_for_release(catalogue, "zimbra-mbox-webclient-war", "10.1.18")
except module.MANUAL.ExtractionError:
    pass
else:
    raise AssertionError("a missing package release must fail")

definition = {"upstream": {"url": "https://example.test/zm-ajax.git", "github_repository": "Example/zm-ajax"}}
original_ensure = module.MANUAL.ensure_repository
original_resolve = module.MANUAL.baseline_tag_for_release
try:
    module.MANUAL.ensure_repository = lambda url, destination: destination
    module.MANUAL.baseline_tag_for_release = lambda repository, after: ("10.1.17", "before")
    assert module.selected_releases(definition, "10.1.20", None, Path("/cache")) == ("10.1.17", "10.1.20")
    assert module.selected_releases(definition, "10.1.17", "10.1.20", Path("/cache")) == ("10.1.17", "10.1.20")
finally:
    module.MANUAL.ensure_repository = original_ensure
    module.MANUAL.baseline_tag_for_release = original_resolve
