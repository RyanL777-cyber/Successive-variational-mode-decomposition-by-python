from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "svmd_prototype.py"


def main() -> None:
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--quiet",
        "--max-modes",
        "5",
        "--max-iter",
        "80",
        "--debug-save",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
