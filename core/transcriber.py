"""Audio transcription engine powered by faster-whisper.

Converts meeting video or audio recordings into timestamped text transcripts
optimized for LLM summarization and academic study notes generation.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Generator
from faster_whisper import WhisperModel
from .ffmpeg_locator import ensure_ffmpeg, get_project_root


def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS string."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


class AudioTranscriber:
    """Manages audio extraction and faster-whisper transcription."""

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        output_dir: Path | str | None = None,
    ) -> None:
        self.root = get_project_root()
        self.output_dir = Path(output_dir).resolve() if output_dir else self.root / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_dir = ensure_ffmpeg()
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        """Lazily loads the Whisper model."""
        if self._model is None:
            print(f"[*] Cargando modelo faster-whisper '{self.model_size}' ({self.device}, {self.compute_type})...")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=os.cpu_count() or 6,
            )
        return self._model

    def extract_audio(self, media_path: Path) -> Path:
        """Extracts audio track as 16kHz mono WAV optimized for Whisper."""
        wav_path = self.output_dir / f"{media_path.stem}_audio16k.wav"
        if wav_path.exists() and wav_path.stat().st_size > 1000:
            print(f"[*] Reutilizando audio extraído: {wav_path.name}")
            return wav_path

        ffmpeg_bin = self.ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        print(f"[*] Extrayendo audio de '{media_path.name}' a 16kHz mono...")
        cmd = [
            str(ffmpeg_bin),
            "-y",
            "-i",
            str(media_path),
            "-vn",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return wav_path

    def transcribe(
        self,
        media_input: str | Path,
        language: str = "es",
        vad_filter: bool = True,
    ) -> Path:
        """Transcribes media file to timestamped Markdown and TXT files.

        Args:
            media_input: Path to video (MP4) or audio file.
            language: Spoken language code (default: 'es').
            vad_filter: Filter out non-speech silence intervals.

        Returns:
            Path: Path to generated transcript file (.md).
        """
        media_path = Path(media_input).resolve()
        if not media_path.is_file():
            raise FileNotFoundError(f"Archivo no encontrado: {media_path}")

        wav_path = self.extract_audio(media_path)
        model = self._get_model()

        print(f"[*] Iniciando transcripción de '{media_path.stem}' en idioma '{language}'...")
        start_time = time.time()

        segments, info = model.transcribe(
            str(wav_path),
            language=language,
            vad_filter=vad_filter,
            beam_size=5,
        )

        txt_out = self.output_dir / f"{media_path.stem}_transcripcion.txt"
        md_out = self.output_dir / f"{media_path.stem}_transcripcion.md"

        print(f"[*] Idioma detectado: {info.language} (Probabilidad: {info.language_probability:.2f})")
        print(f"[*] Duración estimada de audio: {format_timestamp(info.duration)}")
        print("[*] Procesando segmentos (esto tomará unos minutos)...\n")

        lines_txt = []
        lines_md = [
            f"# Transcripción de Clase: {media_path.stem}\n",
            f"- **Archivo fuente:** `{media_path.name}`",
            f"- **Duración:** {format_timestamp(info.duration)}",
            f"- **Modelo:** `faster-whisper/{self.model_size}`",
            f"- **Fecha:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---",
            "## Registro Cronológico\n",
        ]

        count = 0
        with open(txt_out, "w", encoding="utf-8") as f_txt:
            for seg in segments:
                count += 1
                start_str = format_timestamp(seg.start)
                end_str = format_timestamp(seg.end)
                text = seg.text.strip()

                line_txt = f"[{start_str} - {end_str}] {text}"
                f_txt.write(line_txt + "\n")
                f_txt.flush()

                line_md = f"**[{start_str}]** {text}"
                lines_md.append(line_md + "\n")

                if count % 20 == 0:
                    print(f"    [{start_str}] {text[:75]}...")

        with open(md_out, "w", encoding="utf-8") as f_md:
            f_md.write("\n".join(lines_md))

        # Cleanup temporary audio WAV
        if wav_path.exists():
            try:
                wav_path.unlink()
            except Exception:
                pass

        elapsed = time.time() - start_time
        print(f"\n[+] Transcripción completada en {elapsed:.1f} segundos ({elapsed/60:.1f} minutos).")
        print(f"[+] Archivo TXT: {txt_out}")
        print(f"[+] Archivo Markdown: {md_out}")
        return md_out
