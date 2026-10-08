"""FFmpeg and FFprobe locator module.

Resolves paths to ffmpeg and ffprobe executables across local directories,
user application data caches, and system PATH to guarantee error-free execution.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Returns the absolute root directory of the BBB-Scribe project."""
    return Path(__file__).resolve().parent.parent


def find_ffmpeg_bin_dir() -> Path | None:
    """Locates the directory containing both ffmpeg and ffprobe executables.

    Checks the local project bin directory first, followed by known application
    data caches, and finally the operating system PATH.

    Returns:
        Path: Directory containing the binaries, or None if not found.
    """
    root = get_project_root()
    local_bin = root / "bin"

    # 1. Check local project bin folder
    ffmpeg_exe = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    ffprobe_exe = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"

    if (local_bin / ffmpeg_exe).is_file() and (local_bin / ffprobe_exe).is_file():
        return local_bin

    # 2. Check system PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    ffprobe_in_path = shutil.which("ffprobe")
    if ffmpeg_in_path and ffprobe_in_path:
        return Path(ffmpeg_in_path).parent

    # 3. Check AppData cache from ffmpeg-downloader on Windows
    if sys.platform == "win32":
        appdata_bin = (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "ffmpegio"
            / "ffmpeg-downloader"
            / "ffmpeg"
            / "bin"
        )
        if (appdata_bin / ffmpeg_exe).is_file() and (appdata_bin / ffprobe_exe).is_file():
            return appdata_bin

    return None


def ensure_ffmpeg() -> Path:
    """Ensures FFmpeg binaries are available, downloading them if absent.

    Raises:
        RuntimeError: If FFmpeg binaries cannot be found or downloaded.
    """
    existing_dir = find_ffmpeg_bin_dir()
    if existing_dir:
        return existing_dir

    print("[*] FFmpeg o FFprobe no detectados. Iniciando descarga automática de binarios...")
    try:
        import subprocess

        cmd = [sys.executable, "-m", "ffmpeg_downloader", "install", "-y"]
        subprocess.run(cmd, check=True)
    except Exception as exc:
        raise RuntimeError(
            f"Fallo al descargar automáticamente FFmpeg: {exc}. "
            "Instale FFmpeg manualmente y colóquelo en la carpeta 'bin'."
        ) from exc

    resolved_dir = find_ffmpeg_bin_dir()
    if not resolved_dir:
        raise RuntimeError("FFmpeg fue instalado pero no se pudo localizar el directorio de binarios.")
    return resolved_dir
