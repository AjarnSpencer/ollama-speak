"""
Command-line interface for ollama-speak.
Accepts text from arguments or STDIN pipes (e.g. `ollama-web "query" | ollama-speak`).
"""

import os
import sys
import argparse
from .voice import synthesize_and_speak, COMMON_VOICES, detect_voice_for_text


def print_voices():
    print("Popular Edge-TTS Voices and Aliases:")
    print("------------------------------------------------------------------")
    for alias, name in COMMON_VOICES.items():
        print(f"  {alias:<15} -> {name}")
    print("\nFor full list of 400+ voices, see: https://github.com/rany2/edge-tts")


def main():
    parser = argparse.ArgumentParser(
        prog="ollama-speak",
        description="Universal multilingual neural text-to-speech CLI and pipe companion for Ollama models."
    )
    parser.add_argument("text", nargs="*", help="Text to speak (reads from STDIN if omitted)")
    parser.add_argument("-v", "--voice", default=None, help="Voice name or alias (e.g. en-gb, th, zh, ja, es)")
    parser.add_argument("-r", "--rate", default="+0%", help="Speaking rate adjustment (e.g. +10%%, -15%%)")
    parser.add_argument("-p", "--pitch", default="+0Hz", help="Voice pitch adjustment (e.g. +5Hz, -5Hz)")
    parser.add_argument("-l", "--local", action="store_true", help="Use local voice acceleration (Kokoro/Piper/ai-say) if available")
    parser.add_argument("-o", "--output", default=None, help="Save audio to specified MP3 file instead of playing")
    parser.add_argument("--list-voices", action="store_true", help="List common voice aliases")

    args = parser.parse_args()

    if args.list_voices:
        print_voices()
        return

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

    # Synthesize and speak
    success = synthesize_and_speak(
        text=content,
        voice=args.voice,
        rate=args.rate,
        pitch=args.pitch,
        local=args.local,
        output_file=output_path
    )

    if output_path and success:
        print(f"✓ Saved audio to: {output_path}")


if __name__ == "__main__":
    main()
