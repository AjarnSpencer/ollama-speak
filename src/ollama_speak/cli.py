"""
Command-line interface for ollama-speak.
100% Local, Offline Multilingual Neural Text-to-Speech CLI for Ollama (Kokoro-82M & Piper).
Accepts text from arguments or STDIN pipes (e.g. `ollama-web "query" | ollama-speak`).
"""

import os
import sys
import argparse
from .voice import (
    synthesize_and_speak,
    download_all_models,
    KOKORO_VOICES,
    DEFAULT_KOKORO_VOICE
)


def print_voices():
    print("==================================================================")
    print(" 🗣️ ollama-speak 100% Local Neural Voices (Kokoro-82M & Piper)")
    print("==================================================================")
    print(f"\nDefault Local Voice: {DEFAULT_KOKORO_VOICE} (Warm British Baritone, Kokoro-82M)")
    print("\nSupported Local Open-Weight Voices:")
    print("-" * 66)
    print(f"  {'ALIAS / NAME':<18} {'LANGUAGE':<18} {'GENDER / STYLE'}")
    print("-" * 66)
    print(f"  {'bm_george (default)':<18} {'British English':<18} {'Male (Warm Baritone)'}")
    print(f"  {'bm_lewis':<18} {'British English':<18} {'Male'}")
    print(f"  {'bf_alice':<18} {'British English':<18} {'Female'}")
    print(f"  {'af_heart':<18} {'American English':<18} {'Female (Warm)'}")
    print(f"  {'am_adam':<18} {'American English':<18} {'Male'}")
    print(f"  {'jf_tebukuro':<18} {'Japanese':<18} {'Female'}")
    print(f"  {'zf_xiaobei':<18} {'Mandarin Chinese':<18} {'Female'}")
    print(f"  {'ef_dora':<18} {'Spanish':<18} {'Female'}")
    print(f"  {'ff_siwis':<18} {'French':<18} {'Female'}")
    print(f"  {'if_sara':<18} {'Italian':<18} {'Female'}")
    print(f"  {'pf_dora':<18} {'Portuguese':<18} {'Female'}")
    print(f"  {'hf_alpha':<18} {'Hindi':<18} {'Female'}")
    print(f"  {'piper (engine)':<18} {'British / English':<18} {'Ultra-lightweight ONNX'}")
    print("\nAll models run 100% locally and offline on your CPU or GPU.")


def main():
    parser = argparse.ArgumentParser(
        prog="ollama-speak",
        description="100%% Local, Offline Multilingual Neural Text-to-Speech CLI for Ollama (Kokoro-82M and Piper)."
    )
    parser.add_argument("text", nargs="*", help="Text to speak (reads from STDIN if omitted)")
    parser.add_argument("-v", "--voice", default=None, help="Local voice name (e.g. bm_george, af_heart, bf_alice)")
    parser.add_argument("-e", "--engine", choices=["kokoro", "piper"], default="kokoro", help="TTS engine: kokoro (default, studio quality) or piper (ultra-fast ONNX)")
    parser.add_argument("--piper", action="store_true", help="Shortcut for --engine piper (ultra-lightweight local ONNX)")
    parser.add_argument("--kokoro", action="store_true", help="Shortcut for --engine kokoro (studio quality open-weights)")
    parser.add_argument("-o", "--output", default=None, help="Save audio to specified WAV/MP3 file instead of playing")
    parser.add_argument("--setup", "--download-models", action="store_true", help="Pre-download local model weights for 100%% offline use")
    parser.add_argument("--list-voices", action="store_true", help="List available local open-weight voices")

    args = parser.parse_args()

    if args.setup:
        download_all_models()
        return

    if args.list_voices:
        print_voices()
        return

    engine = "piper" if args.piper else ("kokoro" if args.kokoro else args.engine)

    # 1. Check positional arguments
    if args.text:
        content = " ".join(args.text).strip()
    # 2. Check STDIN pipe (e.g. ollama-web ... | ollama-speak)
    elif not sys.stdin.isatty():
        content = sys.stdin.read().strip()
        # Always echo piped text to stdout so the human sees, reads, and can copy-paste it!
        if content:
            print(content, flush=True)
    else:
        parser.print_help()
        sys.exit(0)

    if not content:
        sys.exit(0)

    output_path = os.path.expanduser(args.output) if args.output else None

    # Synthesize and speak using 100% local model
    success = synthesize_and_speak(
        text=content,
        voice=args.voice,
        engine=engine,
        output_file=output_path
    )

    if output_path and success:
        print(f"✓ Saved audio to: {output_path}")


if __name__ == "__main__":
    main()
