#!/usr/bin/env python3
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract-ubuntu-apt-repositories"
FIXTURE = ROOT / "tests" / "fixtures" / "ubuntu-apt-repositories" / "utilfunc.sh"


def extract(edition: str, archive: Path, output_directory: Path) -> dict:
    report = output_directory.parent / f"{edition}-report.json"
    completed = subprocess.run(
        [
            str(SCRIPT),
            "--edition",
            edition,
            "--output-directory",
            str(output_directory),
            "--report",
            str(report),
            str(archive),
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    assert "Rendered" in completed.stdout
    return json.loads(report.read_text(encoding="utf-8"))


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    archive_base = "zcs-NETWORK-example.UBUNTU24_64.1"
    archive = temporary / f"{archive_base}.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(FIXTURE, arcname=f"{archive_base}/util/utilfunc.sh")

    network_output = temporary / "network-sources"
    network = extract("network", archive, network_output)
    assert network["assumptions"]["package_server"] == "repo.example.test"
    assert network["assumptions"]["suite"] == "noble"
    assert network["input"]["installer_helper_member"] == f"{archive_base}/util/utilfunc.sh"
    assert [repository["uri"] for repository in network["repositories"]] == [
        "https://repo.example.test/apt/1010",
        "https://repo.example.test/apt/1010-ne",
        "https://repo.example.test/apt/onlyoffice-1010",
    ]
    assert network["repositories"][1]["types"] == ["deb"]
    assert (network_output / "zimbra.sources").read_text(encoding="utf-8").count("Types:") == 2
    assert (network_output / "zimbra-onlyoffice.sources").is_file()

    foss_output = temporary / "foss-sources"
    foss = extract("foss", archive, foss_output)
    assert [repository["uri"] for repository in foss["repositories"]] == ["https://repo.example.test/apt/1010"]
    assert (foss_output / "zimbra.sources").is_file()
    assert not (foss_output / "zimbra-onlyoffice.sources").exists()
