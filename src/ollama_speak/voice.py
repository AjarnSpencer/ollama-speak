"""
Core voice engine for ollama-speak.
Provides script-aware multilingual text-to-speech with cross-platform native playback.
"""

import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path


COMMON_VOICES = {
    "en-gb": "en-GB-RyanNeural",
    "en-us": "en-US-GuyNeural",
    "en-us-female": "en-US-JennyNeural",
    "th": "th-TH-NiwatNeural",
    "th-female": "th-TH-PremwadeeNeural",
    "zh": "zh-CN-YunxiNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "ru": "ru-RU-DmitryNeural",
    "ar": "ar-SA-HamedNeural",
}


def play_audio_file(file_path: str) -> bool:
    """Plays an audio file (.mp3 or .wav) natively across Linux, macOS, and Windows."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
        return False

    # macOS: native afplay plays mp3/wav directly on every Mac
    if sys.platform == "darwin":
        if shutil.which("afplay"):
            res = subprocess.run(["afplay", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0

    # Windows: native PowerShell Media Player
    if sys.platform == "win32":
        abs_p = os.path.abspath(file_path).replace("\\", "\\\\")
        if file_path.endswith(".mp3"):
            ps_cmd = (
                f"$wmp = New-Object -ComObject WMPlayer.OCX; "
                f"$wmp.URL = '{abs_p}'; $wmp.controls.play(); "
                f"while ($wmp.playState -ne 1) {{ Start-Sleep -Milliseconds 100 }}"
            )
        else:
            ps_cmd = (
                f"$player = New-Object System.Media.SoundPlayer('{abs_p}'); "
                f"if ($player) {{ $player.PlaySync() }}"
            )
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0

    # Linux: check audio backends in order of reliability
    if shutil.which("mpv"):
        res = subprocess.run(["mpv", "--no-video", "--really-quiet", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    if shutil.which("ffplay"):
        res = subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    if shutil.which("mpg123") and file_path.endswith(".mp3"):
        res = subprocess.run(["mpg123", "-q", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    if shutil.which("cvlc"):
        res = subprocess.run(["cvlc", "--play-and-exit", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    if shutil.which("pw-play"):
        res = subprocess.run(["pw-play", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    if shutil.which("paplay"):
        if file_path.endswith(".mp3") and shutil.which("ffmpeg"):
            wav_tmp = file_path.rsplit(".", 1)[0] + ".wav"
            subprocess.run(["ffmpeg", "-y", "-i", file_path, wav_tmp], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(wav_tmp):
                res = subprocess.run(["paplay", wav_tmp], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    os.remove(wav_tmp)
                except OSError:
                    pass
                if res.returncode == 0:
                    return True
        elif file_path.endswith(".wav"):
            res = subprocess.run(["paplay", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return True

    if shutil.which("aplay") and file_path.endswith(".wav"):
        res = subprocess.run(["aplay", "-q", file_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

    return False


def detect_voice_for_text(text: str) -> str:
    """
    Selects high-fidelity neural voice model matched to the primary linguistic script.
    Zero phonetic corruption: ensures Thai and Asian scripts are never fed to Latin-only models.
    """
    # Thai script
    if re.search(r"[\u0e00-\u0e7f]", text):
        return "th-TH-NiwatNeural"

    # CJK scripts (Chinese, Japanese, Korean)
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh-CN-YunxiNeural"
    if re.search(r"[\u3040-\u30ff]", text):
        return "ja-JP-NanamiNeural"
    if re.search(r"[\uac00-\ud7af]", text):
        return "ko-KR-SunHiNeural"

    # Cyrillic script
    if re.search(r"[\u0400-\u04ff]", text):
        return "ru-RU-DmitryNeural"

    # Arabic script
    if re.search(r"[\u0600-\u06ff]", text):
        return "ar-SA-HamedNeural"

    # Spanish script
    if re.search(r"[áéíóúñ¿¡]", text, re.IGNORECASE):
        return "es-ES-AlvaroNeural"

    # Default to warm British Baritone
    return "en-GB-RyanNeural"


def synthesize_and_speak(
    text: str,
    voice: str = None,
    rate: str = "+0%",
    pitch: str = "+0Hz",
    local: bool = False,
    output_file: str = None
) -> bool:
    """
    Synthesizes and speaks text using Edge-TTS or local acceleration.
    """
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"[`*_#>\[\]()~|]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return False

    is_thai = bool(re.search(r"[\u0e00-\u0e7f]", clean))
    is_cjk = bool(re.search(r"[\u4e00-\u9fff\u3040-\u30ff]", clean))

    # Optional local acceleration for English/Latin
    if local and not (is_thai or is_cjk):
        if shutil.which("ai-say"):
            res = subprocess.run(["ai-say", "--kokoro", clean], check=False)
            if res.returncode == 0:
                return True
        elif shutil.which("kokoro"):
            res = subprocess.run(["kokoro", "-t", clean], check=False)
            if res.returncode == 0:
                return True

    # Universal Edge-TTS
    try:
        import asyncio
        import edge_tts

        selected_voice = voice
        if not selected_voice:
            selected_voice = detect_voice_for_text(clean)
        elif selected_voice.lower() in COMMON_VOICES:
            selected_voice = COMMON_VOICES[selected_voice.lower()]

        save_path = output_file
        is_temp = False
        if not save_path:
            is_temp = True
            tmp_dir = Path(tempfile.gettempdir())
            save_path = str(tmp_dir / "ollama_speak_voice.mp3")

        comm = edge_tts.Communicate(clean, selected_voice, rate=rate, pitch=pitch)
        if hasattr(comm, "save_sync"):
            comm.save_sync(save_path)
        else:
            asyncio.run(comm.save(save_path))

        if is_temp:
            played = play_audio_file(save_path)
            try:
                os.remove(save_path)
            except OSError:
                pass
            return played
        else:
            return os.path.exists(save_path) and os.path.getsize(save_path) > 100
    except Exception as e:
        # Fall back to OS speech synthesizer
        if sys.platform == "darwin" and shutil.which("say"):
            subprocess.run(["say", clean], check=False)
            return True
        elif sys.platform == "win32":
            escaped = clean.replace('"', '""').replace("'", "''")
            ps_cmd = (
                f"Add-Type -AssemblyName System.Speech; "
                f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$synth.Speak('{escaped}')"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False)
            return True
        elif sys.platform.startswith("linux"):
            if shutil.which("espeak-ng"):
                subprocess.run(["espeak-ng", clean], check=False)
                return True
            elif shutil.which("espeak"):
                subprocess.run(["espeak", clean], check=False)
                return True
        return False
