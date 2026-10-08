"""Utility script to extract video frames by timestamp for visual context in notes.

Usage:
    python extract_frame.py "output/Clase 9.mp4" 01:42:15
    python extract_frame.py "output/Clase 9.mp4" 01:42:15 -o "output/frames/detalle.jpg"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Auto-delegate to .venv if running with global Python
current_dir = Path(__file__).resolve().parent
venv_python = current_dir / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
    cmd = [str(venv_python), str(__file__)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))

from core.ffmpeg_locator import ensure_ffmpeg


def extract_frame(
    video_path: str | Path,
    timestamp: str,
    output_path: str | Path | None = None,
) -> Path:
    """Extracts a single high-quality frame from a video at the given timestamp.

    Args:
        video_path: Path to the MP4 video file.
        timestamp: Time string in format HH:MM:SS or SS.
        output_path: Destination path for the extracted image (optional).

    Returns:
        Path to the saved image file.
    """
    video = Path(video_path).resolve()
    if not video.is_file():
        raise FileNotFoundError(f"Archivo de video no encontrado: {video}")

    ffmpeg_dir = ensure_ffmpeg()
    ffmpeg_bin = ffmpeg_dir / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")

    if output_path is None:
        frames_dir = video.parent / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        safe_time = timestamp.replace(":", "-").replace(".", "-")
        out_file = frames_dir / f"{video.stem}_{safe_time}.jpg"
    else:
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(ffmpeg_bin),
        "-ss",
        str(timestamp),
        "-i",
        str(video),
        "-vframes",
        "1",
        "-q:v",
        "2",
        "-y",
        str(out_file),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Extraer fotograma de un video en un timestamp específico")
    parser.add_argument("video", help="Ruta del archivo de video MP4")
    parser.add_argument("timestamp", help="Marca de tiempo en formato HH:MM:SS o segundos")
    parser.add_argument("-o", "--output", help="Ruta de salida para la imagen extraída")
    args = parser.parse_args()

    try:
        saved_path = extract_frame(args.video, args.timestamp, args.output)
        print(f"[+] Fotograma extraído con éxito: {saved_path}")
    except Exception as exc:
        print(f"[-] Error al extraer fotograma: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
