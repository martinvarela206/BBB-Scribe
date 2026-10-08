import os
import sys
import subprocess
from pathlib import Path

# Auto-delegate to .venv if running with global Python
current_dir = Path(__file__).resolve().parent
venv_python = current_dir / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
    cmd = [str(venv_python), str(__file__)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))

"""Standalone script for transcribing audio/video files with faster-whisper.

Usage:
    python transcribe.py "output/Clase 8.mp4"
    python transcribe.py "output/Clase 8.mp4" --model medium
"""

import sys
import argparse
from pathlib import Path
from core.transcriber import AudioTranscriber

def main():
    parser = argparse.ArgumentParser(description="Transcribir clase MP4/audio a texto con faster-whisper")
    parser.add_argument("file", nargs="?", help="Ruta del archivo de video o audio a transcribir")
    parser.add_argument("--model", default="small", help="Modelo Whisper: tiny, base, small, medium (por defecto: small)")
    args = parser.parse_args()

    target = args.file
    if not target:
        output_dir = Path("output")
        candidates = list(output_dir.glob("*.mp4")) + list(output_dir.glob("*.mp3"))
        if candidates:
            print("\nArchivos encontrados en carpeta output/:")
            for idx, c in enumerate(candidates, 1):
                print(f" [{idx}] {c.name}")
            sel = input(f"\nSeleccione archivo [1-{len(candidates)}] o escriba una ruta: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(candidates):
                target = str(candidates[int(sel) - 1])
            else:
                target = sel
        else:
            target = input("\nIngrese la ruta del archivo de audio o video: ").strip().strip('"')

    if not target:
        print("[-] No se especificó ningún archivo.")
        sys.exit(1)

    transcriber = AudioTranscriber(model_size=args.model)
    transcriber.transcribe(target)

if __name__ == "__main__":
    main()
