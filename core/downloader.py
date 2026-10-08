"""Downloader orchestrator using bbb-dl engine.

Coordinates execution of bbb-dl with automatic FFmpeg discovery,
custom output directory handling, and progress visualization.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from .ffmpeg_locator import ensure_ffmpeg, get_project_root


class BBBDownloader:
    """Manages BigBlueButton session download jobs via bbb-dl."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.root = get_project_root()
        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = self.root / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.ffmpeg_dir = ensure_ffmpeg()

    def download(
        self,
        url: str,
        filename: str | None = None,
        audio_only: bool = False,
        skip_webcam: bool = False,
        skip_annotations: bool = False,
        skip_cursor: bool = False,
        fast_preset: bool = True,
        max_parallel_chromes: int = 4,
        force_width: int | None = None,
        force_height: int | None = None,
        verbose: bool = False,
    ) -> bool:
        """Executes the download process.

        Args:
            url: The BigBlueButton playback URL.
            filename: Target file name (optional).
            audio_only: Only extract audio MP3.
            skip_webcam: Do not overlay teacher webcam.
            skip_annotations: Skip chalkboard annotations.
            skip_cursor: Skip rendering laser/pointer cursor.
            fast_preset: Use ultrafast FFmpeg preset for maximum speed.
            max_parallel_chromes: Browser workers for slide rendering.
            force_width: Custom output resolution width.
            force_height: Custom output resolution height.
            verbose: Output full debug logs.

        Returns:
            bool: True if download succeeded, False otherwise.
        """
        venv_scripts = Path(sys.executable).parent
        bbb_dl_exe = venv_scripts / ("bbb-dl.exe" if sys.platform == "win32" else "bbb-dl")

        if bbb_dl_exe.is_file():
            cmd = [str(bbb_dl_exe)]
        else:
            cmd = [
                sys.executable,
                "-c",
                "import sys, bbb_dl.main; sys.argv = ['bbb-dl'] + sys.argv[1:]; bbb_dl.main.main()",
            ]

        cmd.extend([
            "--ffmpeg-location",
            str(self.ffmpeg_dir),
            "--output-dir",
            str(self.output_dir),
            "--audiocodec",
            "aac",
        ])

        if filename:
            cmd.extend(["-f", filename])
        if audio_only:
            cmd.append("--audio-only")
        if skip_webcam:
            cmd.append("--skip-webcam")
        if skip_annotations:
            cmd.append("--skip-annotations")
        if skip_cursor:
            cmd.append("--skip-cursor")
        if fast_preset:
            cmd.extend(["--preset", "ultrafast"])
        if max_parallel_chromes > 0:
            cmd.extend(["-mpc", str(max_parallel_chromes)])
        if force_width:
            cmd.extend(["-fw", str(force_width)])
        if force_height:
            cmd.extend(["-fh", str(force_height)])
        if verbose:
            cmd.append("--verbose")

        # Positional URL argument must be last
        cmd.append(url)

        print(f"[*] Destino de salida: {self.output_dir}")
        print(f"[*] Directorio de FFmpeg: {self.ffmpeg_dir}")
        print(f"[*] Iniciando motor bbb-dl...\n")

        # Set environment PATH to prioritize local FFmpeg
        env = os.environ.copy()
        env["PATH"] = f"{self.ffmpeg_dir}{os.pathsep}{env.get('PATH', '')}"

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            if process.stdout:
                for line in process.stdout:
                    print(line, end="", flush=True)

            process.wait()
            if process.returncode == 0:
                print(f"\n[+] ¡Descarga finalizada con éxito! Archivos guardados en: {self.output_dir}")
                return True
            else:
                print(f"\n[-] bbb-dl finalizó con código de error: {process.returncode}")
                return False

        except KeyboardInterrupt:
            print("\n[!] Operación cancelada por el usuario.")
            return False
        except Exception as exc:
            print(f"\n[-] Error al ejecutar el proceso de descarga: {exc}")
            return False
