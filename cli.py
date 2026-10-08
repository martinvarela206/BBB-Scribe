"""Interactive and scripted Command Line Interface for BBB-Scribe.

Provides menu-driven options and argument parsing to download and transcribe
BigBlueButton classes into unified media and timestamped Markdown notes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.direct_extractor import DirectExtractor
from core.transcriber import AudioTranscriber
from core.downloader import BBBDownloader
from core.url_parser import BBBUrlParser


def print_banner() -> None:
    """Displays the application banner."""
    print("=" * 65)
    print("                 BBB-SCRIBE (BigBlueButton Suite)")
    print("    Descarga, recomposición y transcripción de clases grabadas")
    print("=" * 65)


def interactive_mode() -> None:
    """Guides the user through an interactive prompt flow."""
    print_banner()
    try:
        url = input("\n[?] Ingrese la URL de la clase grabada (BBB): ").strip()
        while not url:
            url = input("[?] La URL no puede estar vacía. Ingrese la URL: ").strip()

        print("\n[*] Inspeccionando la sesión en el servidor...")
        try:
            meta = BBBUrlParser.inspect_session(url)
            print(f"    - ID de reunión: {meta.meeting_id}")
            print(f"    - Audio disponible: {'Sí' if meta.has_audio else 'No detectado'}")
            print(f"    - Pantalla compartida (Deskshare): {'Sí' if meta.has_deskshare else 'No'}")
            print(f"    - Cámara web docente: {'Sí' if meta.has_webcam else 'No'}")
            print(f"    - Diapositivas / Pizarra: {'Sí' if meta.has_shapes else 'No'}")
        except Exception as exc:
            print(f"    [!] Aviso de inspección: {exc}")

        print("\nSeleccione el modo de descarga:")
        print(" [1] Descarga Completa (MP4 completo con pizarra, diapositivas y webcam)")
        print(" [2] Descarga Ligera (MP4 sin webcam superpuesta, procesa más rápido)")
        print(" [3] Descarga Directa Ultra Rápida (Solo streams crudos: pantalla + audio)")
        print(" [4] Solo Audio (MP3)")
        print(" [5] Transcribir video o audio existente a texto (Whisper)")

        choice = input("\n[?] Opción [1-4] (Por defecto 1): ").strip() or "1"
        out_name = input("[?] Nombre de archivo de salida (Enter para automático): ").strip() or None

        downloader = BBBDownloader()
        extractor = DirectExtractor()

        if choice == "1":
            print("\n[*] Iniciando descarga completa...")
            downloader.download(url=url, filename=out_name, skip_webcam=False)
        elif choice == "2":
            print("\n[*] Iniciando descarga ligera (sin webcam)...")
            downloader.download(url=url, filename=out_name, skip_webcam=True)
        elif choice == "3":
            print("\n[*] Iniciando descarga directa de streams...")
            target_name = (out_name if out_name and out_name.endswith(".mp4") else f"{out_name or 'clase'}.mp4")
            extractor.extract_and_merge(url=url, output_filename=target_name)
        elif choice == "4":
            print("\n[*] Extrayendo solo audio MP3...")
            downloader.download(url=url, filename=out_name, audio_only=True)
        elif choice == "5":
            file_path = input("\n[?] Ruta del archivo MP4 o audio a transcribir: ").strip().strip('"')
            transcriber = AudioTranscriber(model_size="small")
            transcriber.transcribe(file_path)
            return
        else:
            print("\n[*] Opción no reconocida. Utilizando modo por defecto [1]...")
            downloader.download(url=url, filename=out_name)

    except KeyboardInterrupt:
        print("\n[!] Proceso interrumpido por el usuario.")
        sys.exit(0)


def build_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="BBB-downloader: Descarga grabaciones de BigBlueButton como MP4/MP3."
    )
    parser.add_argument("url", nargs="?", help="URL de la grabación de BigBlueButton")
    parser.add_argument("-o", "--output-dir", help="Carpeta de destino para los videos", default=None)
    parser.add_argument("-f", "--filename", help="Nombre del archivo de salida", default=None)
    parser.add_argument("--audio-only", action="store_true", help="Descargar únicamente el audio en MP3")
    parser.add_argument("--skip-webcam", action="store_true", help="Omitir la cámara del docente en el video")
    parser.add_argument("--direct", action="store_true", help="Descarga directa de streams sin renderizado")
    parser.add_argument("--transcribe", help="Ruta de archivo MP4/audio a transcribir a texto con Whisper", default=None)
    parser.add_argument("--model-size", help="Tamaño de modelo Whisper (tiny, base, small, medium)", default="small")
    parser.add_argument("--verbose", action="store_true", help="Mostrar logs detallados de depuración")
    return parser


def main() -> None:
    """Entry point for CLI execution."""
    parser = build_parser()
    args = parser.parse_args()

    if args.transcribe:
        transcriber = AudioTranscriber(model_size=args.model_size)
        transcriber.transcribe(args.transcribe)
        return

    if not args.url:
        interactive_mode()
        return

    if args.direct:
        extractor = DirectExtractor(output_dir=args.output_dir)
        filename = args.filename if args.filename else "clase_directa.mp4"
        extractor.extract_and_merge(args.url, output_filename=filename)
    else:
        downloader = BBBDownloader(output_dir=args.output_dir)
        downloader.download(
            url=args.url,
            filename=args.filename,
            audio_only=args.audio_only,
            skip_webcam=args.skip_webcam,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()
