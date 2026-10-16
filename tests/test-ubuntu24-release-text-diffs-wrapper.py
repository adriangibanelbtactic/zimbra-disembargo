#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "ubuntu24-debian-non-patch-packages-pseudo-code-analysis"


with tempfile.TemporaryDirectory() as temporary_directory:
    temporary = Path(temporary_directory)
    binary_directory = temporary / "bin"
    binary_directory.mkdir()
    log = temporary / "docker.log"
    state = temporary / "container-state"
    docker = binary_directory / "docker"
    docker.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$FAKE_DOCKER_LOG"
case "$1 $2" in
  'image inspect') exit 0 ;;
  'container inspect') test -e "$FAKE_DOCKER_STATE" ;;
  'rm --force') rm -f "$FAKE_DOCKER_STATE" ;;
  'run --detach') touch "$FAKE_DOCKER_STATE" ;;
  'exec --user'|'exec zimbra-disembargo-ubuntu24-debian-non-patch-packages-pseudo-code-analysis') exit 0 ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    state.touch()  # A container from a different checkout already exists.
    environment = {
        **os.environ,
        "PATH": f"{binary_directory}:{os.environ['PATH']}",
        "FAKE_DOCKER_LOG": str(log),
        "FAKE_DOCKER_STATE": str(state),
    }
    subprocess.run(
        [str(WRAPPER), "release-text-diffs", "10.1.20", "10.1.21"],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    calls = log.read_text(encoding="utf-8").splitlines()
    removal_calls = [index for index, call in enumerate(calls) if call.startswith("rm --force ")]
    run_call = next(index for index, call in enumerate(calls) if call.startswith("run --detach "))
    analysis_call = next(
        index
        for index, call in enumerate(calls)
        if "/project/scripts/ubuntu24-non-patch-release-text-diffs" in call
    )
    assert len(removal_calls) == 2
    assert removal_calls[0] < run_call < analysis_call < removal_calls[1]
    assert not state.exists()
