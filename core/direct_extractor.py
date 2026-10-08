"""Direct stream extractor and merger.

Downloads raw audio and deskshare streams directly when the session consists
primarily of screen sharing and microphone audio, avoiding costly slide rendering.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
import requests
from .ffmpeg_locator import ensure_ffmpeg, get_project_root
from .url_parser import BBBUrlParser


class DirectExtractor:
    """Extracts and merges raw streams without headless browser rendering."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.root = get_project_root()
        self.output_dir = Path(output_dir).resolve() if output_dir else self.root / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_dir = ensure_ffmpeg()

    def download_file(self, url: str, target_path: Path) -> bool:
        """Downloads a remote stream with a progress indicator."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            with requests.get(url, stream=True, headers=headers, timeout=15) as resp:
                if resp.status_code != 200:
                    return False
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(target_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 512):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                percent = (downloaded / total) * 100
                                mb_done = downloaded / (1024 * 1024)
                                mb_total = total / (1024 * 1024)
                                print(f"\r    Progreso: {percent:.1f}% ({mb_done:.1f}/{mb_total:.1f} MB)", end="", flush=True)
            print()
            return True
        except Exception as exc:
            print(f"\n[-] Error al descargar {url}: {exc}")
            return False

    def extract_and_merge(self, url: str, output_filename: str = "clase_directa.mp4") -> bool:
        """Downloads audio and deskshare streams and muxes them into a single MP4."""
        meeting_id = BBBUrlParser.extract_meeting_id(url)
        if not meeting_id:
            print("[-] No se pudo identificar el ID de la reunión.")
            return False

        base_url = BBBUrlParser.get_session_base_url(url, meeting_id)
        temp_dir = self.root / "tmp_direct"
        temp_dir.mkdir(parents=True, exist_ok=True)

        audio_urls = [
            f"{base_url}/audio/audio.webm",
            f"{base_url}/audio/audio.ogg",
            f"{base_url}/audio/audio.mp4",
            f"{base_url}/video/webcams.webm",
            f"{base_url}/video/webcams.mp4",
        ]
        video_urls = [
            f"{base_url}/deskshare/deskshare.webm",
            f"{base_url}/deskshare/deskshare.mp4",
            f"{base_url}/video/webcam.webm",
        ]

        # 1. Download audio
        audio_path = temp_dir / "audio_stream.webm"
        audio_found = False
        print("[*] Buscando pista de audio...")
        for a_url in audio_urls:
            if self.download_file(a_url, audio_path):
                audio_found = True
                print(f"[+] Audio descargado desde: {a_url}")
                break

        if not audio_found:
            print("[-] No se encontró una pista de audio directa en el servidor.")
            return False

        # 2. Download video
        video_path = temp_dir / "video_stream.webm"
        video_found = False
        print("[*] Buscando pista de video (pantalla compartida o cámara)...")
        for v_url in video_urls:
            if self.download_file(v_url, video_path):
                video_found = True
                print(f"[+] Video descargado desde: {v_url}")
                break

        final_output = self.output_dir / output_filename

        # If only audio was found, save it as MP3
        if not video_found:
            print("[!] No se encontró video de pantalla compartida. Exportando solo audio.")
            mp3_output = final_output.with_suffix(".mp3")
            ffmpeg_bin = self.ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            cmd = [str(ffmpeg_bin), "-y", "-i", str(audio_path), "-vn", "-c:a", "libmp3lame", str(mp3_output)]
            subprocess.run(cmd, check=True)
            print(f"[+] Audio MP3 guardado en: {mp3_output}")
            return True

        # 3. Mux audio + video with FFmpeg
        print("[*] Uniendo audio y video con FFmpeg...")
        ffmpeg_bin = self.ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        cmd = [
            str(ffmpeg_bin),
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(final_output),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            # Fallback re-encoding if direct copy fails
            cmd = [
                str(ffmpeg_bin),
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-c:a",
                "aac",
                "-shortest",
                str(final_output),
            ]
            res = subprocess.run(cmd)

        if final_output.exists():
            print(f"\n[+] ¡Video ensamblado exitosamente en: {final_output}")
            # Clean up temp files
            if audio_path.exists():
                audio_path.unlink()
            if video_path.exists():
                video_path.unlink()
            return True

        return False
