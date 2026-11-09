"""
Core local voice engine for ollama-speak.
100% Local, Offline, Private Neural Text-to-Speech using Kokoro-82M and Piper ONNX.
Zero cloud APIs, zero big-tech telemetry, zero external data leaks.
"""

import os
import re
import sys
import time
import socket
import shutil
import urllib.request
import tempfile
import subprocess
from pathlib import Path

# Common Kokoro-82M open-weight voices
KOKORO_VOICES = {
    # British English (b)
    "en-gb": ("bm_george", "b"),
    "british": ("bm_george", "b"),
    "bm_george": ("bm_george", "b"),
    "bm_lewis": ("bm_lewis", "b"),
    "bm_daniel": ("bm_daniel", "b"),
    "bm_fable": ("bm_fable", "b"),
    "bf_alice": ("bf_alice", "b"),
    "bf_isabella": ("bf_isabella", "b"),
    "bf_emma": ("bf_emma", "b"),
    "bf_lily": ("bf_lily", "b"),

    # American English (a)
    "en-us": ("af_heart", "a"),
    "american": ("af_heart", "a"),
    "af_heart": ("af_heart", "a"),
    "af_bella": ("af_bella", "a"),
    "af_sarah": ("af_sarah", "a"),
    "af_nicole": ("af_nicole", "a"),
    "af_sky": ("af_sky", "a"),
    "am_adam": ("am_adam", "a"),
    "am_michael": ("am_michael", "a"),
    "am_echo": ("am_echo", "a"),
    "am_eric": ("am_eric", "a"),
    "am_onyx": ("am_onyx", "a"),

    # Japanese (j)
    "ja": ("jf_tebukuro", "j"),
    "japanese": ("jf_tebukuro", "j"),
    "jf_tebukuro": ("jf_tebukuro", "j"),
    "jm_kumo": ("jm_kumo", "j"),

    # Mandarin Chinese (z)
    "zh": ("zf_xiaobei", "z"),
    "chinese": ("zf_xiaobei", "z"),
    "zf_xiaobei": ("zf_xiaobei", "z"),
    "zm_yunjian": ("zm_yunjian", "z"),

    # Spanish (e)
    "es": ("ef_dora", "e"),
    "spanish": ("ef_dora", "e"),
    "ef_dora": ("ef_dora", "e"),
    "em_alex": ("em_alex", "e"),

    # French (f)
    "fr": ("ff_siwis", "f"),
    "french": ("ff_siwis", "f"),
    "ff_siwis": ("ff_siwis", "f"),

    # Italian (i)
    "it": ("if_sara", "i"),
    "italian": ("if_sara", "i"),
    "if_sara": ("if_sara", "i"),
    "im_nicola": ("im_nicola", "i"),

    # Portuguese (p)
    "pt": ("pf_dora", "p"),
    "portuguese": ("pf_dora", "p"),
    "pf_dora": ("pf_dora", "p"),
    "pm_alex": ("pm_alex", "p"),

    # Hindi (h)
    "hi": ("hf_alpha", "h"),
    "hindi": ("hf_alpha", "h"),
    "hf_alpha": ("hf_alpha", "h"),
    "hm_psi": ("hm_psi", "h"),
}

DEFAULT_KOKORO_VOICE = "bm_george"
DEFAULT_KOKORO_LANG = "b"


def get_models_dir() -> Path:
    """Returns local model cache directory (~/.local/share/ollama-speak/models)."""
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    d = base / "ollama-speak" / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_piper_model() -> tuple[str, str]:
    """Finds or returns expected path for local Piper ONNX model and config."""
    # 1. Custom env var
    custom = os.environ.get("PIPER_MODEL")
    if custom and os.path.exists(custom):
        json_path = custom + ".json" if not custom.endswith(".json") else custom
        onnx_path = custom.replace(".json", "")
        return onnx_path, json_path

    # 2. DGX / Host workspace path
    workspace_piper = Path.home() / "ai-workspace" / "models" / "tts" / "piper" / "en_GB-alan-medium.onnx"
    if workspace_piper.exists():
        return str(workspace_piper), str(workspace_piper) + ".json"

    # 3. Standard user data dir
    user_piper = get_models_dir() / "piper" / "en_GB-alan-medium.onnx"
    return str(user_piper), str(user_piper) + ".json"


def play_audio_file(file_path: str) -> bool:
    """Plays an audio file (.wav or .mp3) natively across Linux, macOS, and Windows."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
        return False

    # macOS: native afplay
    if sys.platform == "darwin":
        if shutil.which("afplay"):
            res = subprocess.run(["afplay", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0

    # Windows: native PowerShell
    if sys.platform == "win32":
        abs_p = os.path.abspath(file_path).replace("\\", "\\\\")
        ps_cmd = (
            f"$player = New-Object System.Media.SoundPlayer('{abs_p}'); "
            f"if ($player) {{ $player.PlaySync() }}"
        )
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0

    # Linux: check audio players
    for cmd in ["pw-play", "paplay", "mpv", "ffplay", "aplay"]:
        if shutil.which(cmd):
            if cmd == "mpv":
                res = subprocess.run(["mpv", "--no-video", "--really-quiet", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "ffplay":
                res = subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd in ("pw-play", "paplay"):
                res = subprocess.run([cmd, file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "aplay" and file_path.endswith(".wav"):
                res = subprocess.run(["aplay", "-q", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                continue

            if res.returncode == 0:
                return True

    return False


def try_local_daemon(text: str, engine: str = "kokoro") -> bool:
    """
    Checks if a local sovereign voice daemon is already active on localhost.
    Provides sub-50ms warm inference without reloading weights into memory.
    """
    uid = os.getuid() if hasattr(os, "getuid") else 1000
    socket_path = f"/run/user/{uid}/voice_dictate.sock"
    if not os.path.exists(socket_path):
        return False

    cmd = f"SPEAK_KOKORO:{text}\n" if engine == "kokoro" else f"SPEAK:{text}\n"
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(10.0)
        s.connect(socket_path)
        s.sendall(cmd.encode("utf-8"))
        resp = s.recv(1024).decode("utf-8", errors="replace")
        s.close()
        return "OK:" in resp
    except Exception:
        return False


def synthesize_with_kokoro(
    text: str,
    voice_name: str = None,
    speed: float = 1.0,
    output_path: str = None
) -> bool:
    """
    Synthesizes speech using local Kokoro-82M open-weight model.
    Runs 100% locally on CPU or GPU with zero cloud network calls.
    """
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError as e:
        print(f"[!] Kokoro dependencies not found ({e}). Run: pip install kokoro soundfile", file=sys.stderr)
        return False

    # Resolve voice and language code
    selected_voice = DEFAULT_KOKORO_VOICE
    selected_lang = DEFAULT_KOKORO_LANG

    if voice_name:
        v_lower = voice_name.lower().strip()
        if v_lower in KOKORO_VOICES:
            selected_voice, selected_lang = KOKORO_VOICES[v_lower]
        else:
            selected_voice = voice_name
            # Auto-detect lang from prefix
            prefix = voice_name[0].lower()
            if prefix in ("b", "a", "j", "z", "e", "f", "i", "p", "h"):
                selected_lang = prefix

    # Load local Kokoro pipeline
    try:
        pipeline = KPipeline(lang_code=selected_lang, repo_id="hexgrad/Kokoro-82M")
        generator = pipeline(text, voice=selected_voice, speed=speed)
        chunks = [a for _, _, a in generator]
        if not chunks:
            return False

        audio = np.concatenate(chunks)
        save_file = output_path
        is_temp = False
        if not save_file:
            is_temp = True
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            save_file = tmp.name
            tmp.close()

        sf.write(save_file, audio, 24000)

        if is_temp:
            success = play_audio_file(save_file)
            try:
                os.remove(save_file)
            except OSError:
                pass
            return success
        else:
            return os.path.exists(save_file) and os.path.getsize(save_file) > 100
    except Exception as e:
        print(f"[!] Kokoro synthesis error: {e}", file=sys.stderr)
        return False


def synthesize_with_piper(
    text: str,
    output_path: str = None
) -> bool:
    """
    Synthesizes speech using local Piper ONNX model.
    Ultra-lightweight local engine (~35MB model) for low-spec PCs.
    """
    onnx_path, json_path = find_piper_model()
    if not os.path.exists(onnx_path):
        print(f"[!] Piper ONNX model not found at: {onnx_path}", file=sys.stderr)
        print("    Download it with: ollama-speak --setup", file=sys.stderr)
        return False

    save_file = output_path
    is_temp = False
    if not save_file:
        is_temp = True
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        save_file = tmp.name
        tmp.close()

    try:
        # Try python piper module
        import wave
        from piper.voice import PiperVoice
        voice = PiperVoice.load(onnx_path, config_path=json_path if os.path.exists(json_path) else None)
        with wave.open(save_file, "wb") as wf:
            voice.synthesize_wav(text, wf)
    except Exception:
        # Fall back to piper CLI if available
        piper_bin = shutil.which("piper")
        if piper_bin:
            res = subprocess.run([piper_bin, "-m", onnx_path, "-f", save_file], input=text.encode("utf-8"), check=False)
            if res.returncode != 0:
                return False
        else:
            return False

    if is_temp:
        success = play_audio_file(save_file)
        try:
            os.remove(save_file)
        except OSError:
            pass
        return success
    else:
        return os.path.exists(save_file) and os.path.getsize(save_file) > 100


def download_all_models() -> None:
    """
    Pre-downloads Kokoro-82M and Piper open-weight models for 100% offline use.
    """
    print("==================================================================")
    print(" 📥 ollama-speak Local Model Downloader (100% Offline Setup)")
    print("==================================================================")

    # 1. Kokoro-82M
    print("\n1. Verifying / Downloading Kokoro-82M open-weight model (~350 MB)...")
    try:
        from kokoro import KPipeline
        p = KPipeline(lang_code="b", repo_id="hexgrad/Kokoro-82M")
        # Synthesize a 1-word smoke test to cache default voices
        for v in ["bm_george", "af_heart"]:
            gen = p("Ready", voice=v)
            _ = [a for _, _, a in gen]
        print("✓ Kokoro-82M weights verified and cached locally.")
    except Exception as e:
        print(f"[!] Kokoro download error: {e}")

    # 2. Piper ONNX
    print("\n2. Verifying / Downloading Piper British ONNX model (~35 MB)...")
    onnx_path, json_path = find_piper_model()
    if os.path.exists(onnx_path):
        print(f"✓ Piper ONNX already exists at: {onnx_path}")
    else:
        try:
            target_dir = Path(onnx_path).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            url_base = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium"
            print(f"Downloading {onnx_path}...")
            urllib.request.urlretrieve(f"{url_base}/en_GB-alan-medium.onnx", onnx_path)
            urllib.request.urlretrieve(f"{url_base}/en_GB-alan-medium.onnx.json", json_path)
            print("✓ Piper ONNX model downloaded successfully.")
        except Exception as e:
            print(f"[!] Piper download warning: {e}")

    print("\n==================================================================")
    print(" All local models are ready. ollama-speak is 100% offline and sovereign!")
    print("==================================================================")


def synthesize_and_speak(
    text: str,
    voice: str = None,
    engine: str = "kokoro",
    output_file: str = None
) -> bool:
    """
    Main dispatch function for ollama-speak.
    Synthesizes and speaks text using 100% LOCAL models.
    """
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"[`*_#>\[\]()~|]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return False

    # Detect unsupported scripts for local models
    if re.search(r"[\u0e00-\u0e7f]", clean):
        print("[ollama-speak] Note: Thai script detected. Local Kokoro/Piper currently support English, Japanese, Chinese, Spanish, French, Italian, Portuguese, and Hindi.", file=sys.stderr)

    # 1. Fast-path: Check for already warm local voice daemon on host
    if not output_file and try_local_daemon(clean, engine=engine):
        return True

    # 2. Piper Engine
    if engine.lower() in ("piper", "fast"):
        return synthesize_with_piper(clean, output_path=output_file)

    # 3. Kokoro Engine (Default Local SOTA)
    return synthesize_with_kokoro(clean, voice_name=voice, output_path=output_file)
