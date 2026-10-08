"""Project bootstrap launcher.

Ensures the script executes inside the project virtual environment,
delegating seamlessly to the CLI entrypoint.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def bootstrap() -> None:
    """Delegates execution to the virtual environment Python interpreter if needed."""
    current_dir = Path(__file__).resolve().parent
    venv_python = (
        current_dir / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    )

    # If running outside the local venv, redirect to the venv interpreter
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        cmd = [str(venv_python), str(current_dir / "cli.py")] + sys.argv[1:]
        sys.exit(subprocess.call(cmd))

    # Already in venv or no venv found; run cli directly
    from cli import main
    main()


if __name__ == "__main__":
    bootstrap()
