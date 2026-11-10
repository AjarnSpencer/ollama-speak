# 🗣️ ollama-speak (`ospeak`)

[![PyPI version](https://img.shields.io/pypi/v/ollama-speak.svg?color=blue)](https://pypi.org/project/ollama-speak/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)](https://ollama.ai/)
[![100% Local AI](https://img.shields.io/badge/Privacy-100%25%20Offline%20Local-success.svg)](#100-offline-and-sovereign-guarantee)

> **100% Local, Offline Multilingual Neural Text-to-Speech CLI for Ollama (Kokoro-82M and Piper ONNX).**

`ollama-speak` (`ospeak`) is a standalone, sovereign voice engine built specifically for the local AI and Ollama community. It runs **100% locally on your own machine** using open-weights models:

- **Kokoro-82M (Default):** Apache 2.0 open-weight 82M-parameter neural model providing studio-grade broadcast speech.
- **Piper TTS (Ultra-lightweight):** Fast ONNX neural voice engine designed to run with sub-100ms latency even on low-spec hardware or a Raspberry Pi.

Zero cloud API calls, zero telemetry, zero corporate tracking, and zero accounts. Once local weights are downloaded, `ollama-speak` works completely with your internet disconnected.

---

## 💻 Minimum System and Hardware Requirements

`ollama-speak` is designed to run smoothly across consumer laptops, older desktop PCs, MacBooks, and high-performance workstations.

### Hardware Requirements Table

| Component | Piper ONNX (Ultra-Lightweight) | Kokoro-82M (Studio Quality Default) |
| :--- | :--- | :--- |
| **CPU** | Any 64-bit CPU (Intel, AMD, ARM64 / Apple Silicon, Raspberry Pi 4/5) | Modern multi-core CPU (AVX2 recommended) or Apple Silicon M1–M4 |
| **GPU (Optional)** | Not needed (pure CPU ONNX) | Accelerated on CUDA / ROCm / Metal, runs easily on CPU |
| **System RAM** | **1 GB minimum** (uses ~80 MB during inference) | **2 GB to 4 GB RAM** (uses ~350 MB during inference) |
| **Disk Space** | **~35 MB** for voice model | **~350 MB** for open-weight model checkpoint |
| **Audio System** | Standard OS sound (ALSA, PulseAudio, PipeWire, CoreAudio, WASAPI) | Standard OS sound |
| **Internet** | Only required once for initial model download | Only required once for initial model download |

### Supported Operating Systems

- **Linux:** Ubuntu 20.04+, Debian 11+, Fedora 38+, Arch Linux, DGX OS (x86_64 and ARM64).
- **macOS:** macOS 11 (Big Sur) and newer (Intel and Apple Silicon M1/M2/M3/M4). Uses native `afplay`.
- **Windows:** Windows 10 & 11 (64-bit). Uses native PowerShell / System.Media audio backend.

---

## ✨ Features

- **100% Sovereign and Offline:** No queries leave your computer. Never sends your text to Microsoft, Google, Bing, or any remote server.
- **Dual Local Engine Architecture:**
  - **Kokoro-82M:** Deeply expressive, human-like voice with natural breath pacing and emotional cadence.
  - **Piper ONNX:** Blazing fast sub-100ms latency for real-time voice assistants.
- **Self-Contained Model Downloader:** Run `ollama-speak --setup` to pre-download open weights once, or let it fetch them on first run. Once cached, it runs offline indefinitely.
- **Zero-Swallow Pipe Echo:** When piping text from any command (`ollama run llama3 "..." | ollama-speak`), it mirrors text directly to your terminal so your transcript remains visible and copy-pasteable.
- **Zero-Flag Pairing with `ollama-web`:** Simply run `ollama-web "your question"`. The text streams live to your terminal while local voice speaks the answer automatically.
- **Native Cross-Platform Playback:** Automatically utilizes local audio players (`pw-play`, `paplay`, `mpv`, `ffplay`, `afplay` on macOS, PowerShell on Windows).

---

## 🚀 Installation

### Option 1 — Install via PyPI (Recommended for Python users)
`ollama-speak` is published to the official Python Package Index (PyPI). You can install it directly into any active Python environment:

```bash
pip install --upgrade ollama-speak
```

Or install in an isolated global CLI environment using `pipx` (recommended by the Python Packaging Authority for standalone command line utilities):
```bash
pipx install ollama-speak
```

To install with optional Piper ONNX support:
```bash
pip install --upgrade "ollama-speak[all]"
```

---

### Option 2 — One-Line Turnkey Installer (Zero Configuration)
Works automatically on fresh Linux, macOS, and WSL systems without requiring manual virtual environments or encountering PEP 668 system python locks.

**Linux and macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.ps1 | iex
```

What the turnkey installer does:
- Sets up an isolated virtual environment in `~/.local/share/ollama-speak/venv` (zero system conflicts).
- Symlinks `ollama-speak` and `ospeak` launchers into `~/.local/bin/`.
- Configures user `PATH` if not already set.
- Automatically pre-downloads local model weights so it works offline immediately.

---

### Option 3 — Install from GitHub
```bash
pip install git+https://github.com/AjarnSpencer/ollama-speak.git
```

Or clone and run locally:
```bash
git clone https://github.com/AjarnSpencer/ollama-speak.git
cd ollama-speak
./install.sh
```

---

### Pre-Download Local Models for 100% Offline Use
```bash
ollama-speak --setup
```
This downloads and caches the Kokoro-82M and Piper open weights into your local user directory. After this step, you can disconnect your computer from the internet completely.

---

### 📦 PyPI Package Information (For Maintainers)
- **PyPI Release:** [https://pypi.org/project/ollama-speak/](https://pypi.org/project/ollama-speak/)
- **Release Automation:** Pushing a version tag (e.g. `git tag v1.1.1 && git push origin v1.1.1`) automatically triggers GitHub Actions (`.github/workflows/release.yml`) to build and publish updates to PyPI.

---

## 📖 Command Line Reference and Flags

`ollama-speak` can be invoked as either `ollama-speak` or `ospeak`.

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `text` | | STDIN | Text string to speak aloud (reads from STDIN pipe if omitted) |
| `--engine ENGINE` | `-e` | `kokoro` | Local TTS engine: `kokoro` (studio quality) or `piper` (ultra-fast ONNX) |
| `--kokoro` | | | Shortcut for `--engine kokoro` |
| `--piper` | | | Shortcut for `--engine piper` |
| `--voice VOICE` | `-v` | `bm_george` | Select specific local voice (e.g. `bm_george`, `af_heart`, `bf_alice`) |
| `--output FILE` | `-o` | `None` | Save spoken audio to a local WAV/MP3 file instead of playing |
| `--setup` | `--download-models` | | Pre-download all local weights for 100% offline use |
| `--list-voices` | | | List all available local open-weight voices and aliases |
| `-h`, `--help` | | | Show full help manual and flags |

---

## 🎙️ Supported Local Open-Weight Voices

Run `ollama-speak --list-voices` to see all local voices:

| Voice Name | Language | Gender / Style | Engine |
| :--- | :--- | :--- | :--- |
| **`bm_george` (Default)** | British English | Male (Warm Baritone) | Kokoro-82M |
| **`bm_lewis`** | British English | Male | Kokoro-82M |
| **`bf_alice`** | British English | Female | Kokoro-82M |
| **`af_heart`** | American English | Female (Warm) | Kokoro-82M |
| **`am_adam`** | American English | Male | Kokoro-82M |
| **`jf_tebukuro`** | Japanese | Female | Kokoro-82M |
| **`zf_xiaobei`** | Mandarin Chinese | Female | Kokoro-82M |
| **`ef_dora`** | Spanish | Female | Kokoro-82M |
| **`ff_siwis`** | French | Female | Kokoro-82M |
| **`if_sara`** | Italian | Female | Kokoro-82M |
| **`pf_dora`** | Portuguese | Female | Kokoro-82M |
| **`hf_alpha`** | Hindi | Female | Kokoro-82M |
| **`piper`** | British English | Clear / Fast ONNX | Piper |

---

## 💡 Practical Tutorials and Workflows

### Tutorial 1 — Direct Local Text Narration
Speak any text locally using your default Kokoro voice:
```bash
ollama-speak "All local systems are operational and running completely offline."
```

### Tutorial 2 — Zero-Swallow Piped Input from Local Ollama
Pipe output from any local Ollama model directly into `ollama-speak`. The text prints on screen in real-time, and local voice speaks the answer:
```bash
ollama run llama3 "Explain quantum computing in two sentences" | ollama-speak
```

### Tutorial 3 — Fast Piper ONNX for Low-Spec PCs
If you are running on a Raspberry Pi or low-spec laptop, pass `--piper` for ultra-fast, lightweight inference:
```bash
ollama run llama3 "Give me one piece of life advice" | ollama-speak --piper
```

### Tutorial 4 — Changing Local Voices
Choose between different genders, accents, and languages:
```bash
# American Female (Kokoro-82M):
ollama-speak -v af_heart "Welcome to the future of sovereign, local artificial intelligence."

# British Female (Kokoro-82M):
ollama-speak -v bf_alice "It is a pleasure to assist you today."
```

### Tutorial 5 — Exporting Audio to File
Save the synthesized speech directly to a standard audio file:
```bash
ollama-speak -o ~/Music/summary.wav "Your daily briefing has been saved locally."
```

---

## 🔒 100% Offline and Sovereign Guarantee

- **No Remote Servers:** Text is synthesized entirely inside your computer's RAM using open-weights models.
- **No Cloud Fallbacks:** It will never silently phone home to Microsoft, Bing, Google, or any cloud API.
- **No API Keys or Subscriptions:** You own your hardware, and you own your voice assistant.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Kokoro-82M model weights are released under the [Apache 2.0 License](https://huggingface.co/hexgrad/Kokoro-82M).
Piper TTS is released under the [MIT License](https://github.com/rhasspy/piper).
