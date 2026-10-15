#!/usr/bin/env python3
"""Validate every checked-in source extractor definition."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ubuntu24-source-extract-manual"
loader = importlib.machinery.SourceFileLoader("source_extractor_manual", str(SCRIPT))
specification = importlib.util.spec_from_loader(loader.name, loader)
assert specification is not None
module = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = module
loader.exec_module(module)


definitions = sorted((ROOT / "source-extractors").glob("*.json"))
assert definitions
for definition in definitions:
    loaded = module.load_definition(definition)
    assert loaded["name"] == definition.stem
    assert "ZaMsg*properties" in loaded["filter-negative"]
    assert "ZsMsg*properties" in loaded["filter-negative"]
