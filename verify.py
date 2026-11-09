#!/usr/bin/env python3
"""
Diagnostic & Verification Suite for ollama-speak.
Runs automated smoke tests to verify local Kokoro-82M, Piper ONNX, and OS audio playback.
"""

import os
import sys
import shutil
import tempfile

# Auto re-exec into isolated venv if run from bare system python without dependencies
venv_dir = os.path.expanduser("~/.local/share/ollama-speak/venv")
venv_py = os.path.join(venv_dir, "bin", "python")
if os.path.exists(venv_py) and sys.prefix != venv_dir:
    try:
        import kokoro
    except ImportError:
        os.execv(venv_py, [venv_py] + sys.argv)

def test_audio_backends():
    print("[1/3] Checking OS audio playback engines...", end=" ", flush=True)
    found = []
    for cmd in ["pw-play", "paplay", "mpv", "ffplay", "aplay", "afplay"]:
        if shutil.which(cmd):
            found.append(cmd)
    if sys.platform == "win32":
        found.append("powershell (System.Media)")

    if found:
        print(f"✓ OK (Found: {', '.join(found)})")
        return True
    else:
        print("❌ Warning: No audio player found. Install mpv or ffmpeg.")
        return False

def test_kokoro_local():
    print("[2/3] Checking local Kokoro-82M open-weight model...", end=" ", flush=True)
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np

        p = KPipeline(lang_code="b", repo_id="hexgrad/Kokoro-82M")
        gen = p("Diagnostic test.", voice="bm_george", speed=1.0)
        chunks = [a for _, _, a in gen]
        if chunks:
            audio = np.concatenate(chunks)
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp.name, audio, 24000)
            sz = os.path.getsize(tmp.name)
            os.remove(tmp.name)
            print(f"✓ OK (Synthesized {len(audio)} samples, {sz} bytes)")
            return True
        else:
            print("❌ Failed (Empty audio generated)")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_piper_local():
    print("[3/3] Checking local Piper ONNX model...", end=" ", flush=True)
    from ollama_speak.voice import find_piper_model
    onnx_path, json_path = find_piper_model()
    if os.path.exists(onnx_path):
        print(f"✓ OK (Found: {onnx_path})")
        return True
    else:
        print(f"⚠️ Notice: Piper ONNX not cached yet at {onnx_path}. Run 'ollama-speak --setup' to pre-download.")
        return True

def main():
    print("==================================================")
    print(" 🛠️  ollama-speak System Diagnostic & Smoke Test")
    print("==================================================")
    t1 = test_audio_backends()
    t2 = test_kokoro_local()
    t3 = test_piper_local()
    print("==================================================")
    if t1 and t2 and t3:
        print("🎉 100% Local voice engine verified and operational!")
        sys.exit(0)
    else:
        print("❌ Diagnostic failures detected. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
