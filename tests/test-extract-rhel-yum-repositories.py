#!/usr/bin/env python3
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract-rhel-yum-repositories"
FIXTURE = ROOT / "tests" / "fixtures" / "rhel-yum-repositories" / "utilfunc.sh"


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
    archive_base = "zcs-NETWORK-example.RHEL9_64.1"
    archive = temporary / f"{archive_base}.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(FIXTURE, arcname=f"{archive_base}/util/utilfunc.sh")

    network_output = temporary / "network-repos"
    network = extract("network", archive, network_output)
    assert network["assumptions"]["package_server"] == "repo.example.test"
    assert network["input"]["installer_helper_member"] == f"{archive_base}/util/utilfunc.sh"
    assert [repository["id"] for repository in network["repositories"]] == [
        "zimbra-oss",
        "zimbra-network",
        "zimbra-onlyoffice",
    ]
    assert network["repositories"][1]["baseurl"] == "https://repo.example.test/rpm/1010-ne/rhel9"
    assert (network_output / "zimbra.repo").read_text(encoding="utf-8").count("[") == 2
    assert (network_output / "zimbra-onlyoffice.repo").is_file()

    foss_output = temporary / "foss-repos"
    foss = extract("foss", archive, foss_output)
    assert [repository["id"] for repository in foss["repositories"]] == ["zimbra-oss"]
    assert (foss_output / "zimbra.repo").is_file()
    assert not (foss_output / "zimbra-onlyoffice.repo").exists()
