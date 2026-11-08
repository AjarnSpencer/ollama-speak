# 🗣️ ollama-speak (`ospeak`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)](https://ollama.ai/)
[![Zero API Keys](https://img.shields.io/badge/API%20Keys-Zero%20Required-green.svg)](#zero-key-architecture)

> **Universal multilingual neural text-to-speech CLI and pipe companion for Ollama models on Linux, macOS, and Windows.**

`ollama-speak` (`ospeak`) is a standalone, lightweight voice narration engine designed to give local LLMs, shell commands, and `ollama-web` search results a high-fidelity voice. Powered out of the box by Microsoft Edge-TTS, it requires **zero API keys**, **zero local model downloads**, and **zero C++ compilation**, supporting 75+ languages with intelligent script routing.

---

## ✨ Features

- **Universal Out-of-the-Box TTS:** High-fidelity neural voice synthesis powered by Edge-TTS across 75+ languages.
- **Intelligent Script Routing:** Automatically detects text language and routes to native voices:
  - **Thai:** `th-TH-NiwatNeural` (zero phonetic corruption or Unicode spelling bugs)
  - **Chinese / Japanese / Korean:** `zh-CN-YunxiNeural`, `ja-JP-NanamiNeural`, `ko-KR-SunHiNeural`
  - **English / Latin:** Warm British Baritone (`en-GB-RyanNeural`) or American (`en-US-GuyNeural`)
  - **Spanish / French / German:** `es-ES-AlvaroNeural`, `fr-FR-HenriNeural`, `de-DE-ConradNeural`
- **Unix Composable with Zero Text Loss:** Pipe text directly from any command or LLM CLI (`ollama run llama3 "..." | ollama-speak`). **Pipes never swallow your screen text**—`ollama-speak` automatically mirrors incoming text to your terminal so you can read, copy, and paste while listening!
- **Zero-Flag Pairing with `ollama-web`:** When companion `ollama-speak` is installed, simply running `ollama-web "your question"` automatically streams the text on screen and speaks the summary aloud without requiring any flags or pipes!
- **Native Cross-Platform Playback:** Uses pre-installed operating system audio tools:
  - **macOS:** Native `afplay`
  - **Windows:** Native PowerShell `WMPlayer.OCX` / `SoundPlayer`
  - **Linux:** Automatically cascades through `mpv`, `ffplay`, `mpg123`, `cvlc`, `pw-play`, and `paplay`
- **Optional Local Acceleration:** Supports local offline Piper, Kokoro-82M, or `ai-say` when `--local` is specified.
- **Save to File:** Export spoken audio directly to standard directories (e.g. `-o ~/Music/summary.mp3`). Supports `~` home directory expansion.

---

## 🚀 Quickstart and Installation

### Option 1 — Via PyPI
```bash
pip install --upgrade ollama-speak
```

### Option 2 — From GitHub
```bash
pip install --upgrade git+https://github.com/AjarnSpencer/ollama-speak.git
```

### Option 3 — One-Line Installer Script
**Linux & macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.ps1 | iex
```

---

## 📖 Complete Command Line Reference and Flags

`ollama-speak` can be invoked as either `ollama-speak` or `ospeak`.

### Flags Table

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `text` | | STDIN | Text string to speak (if omitted, reads streaming or piped input from STDIN) |
| `--voice VOICE` | `-v` | Auto-detect | Specific voice name or short alias (`en-gb`, `th`, `ja`, `zh`, `es`, etc.) |
| `--rate RATE` | `-r` | `+0%` | Speaking speed adjustment (e.g. `+15%`, `-10%`) |
| `--pitch PITCH` | `-p` | `+0Hz` | Speaking pitch adjustment (e.g. `+5Hz`, `-5Hz`) |
| `--local` | `-l` | `False` | Use local voice engine (Kokoro-82M, Piper, or `ai-say`) for Latin text |
| `--output FILE` | `-o` | `None` | Save audio output to an `.mp3` file instead of playing aloud |
| `--list-voices` | | | Print table of popular voice aliases and language codes |
| `-h`, `--help` | | | Display full help manual and flag usage |

---

## 💡 Practical Tutorials and Workflows

### Tutorial 1 — Direct Text Narration
Speak any phrase directly from your terminal:
```bash
ollama-speak "All systems are operational and ready for deployment."
```

---

### Tutorial 2 — Zero-Swallow Piped Input
When you pipe output from any command into `ollama-speak`, it mirrors the text directly to your terminal before playing audio, so your screen transcript is never lost:
```bash
# Pipe from any Ollama model or shell command:
ollama run llama3 "Explain quantum tunneling in two sentences" | ollama-speak
```
The full answer prints on your screen in real time, and the voice begins speaking immediately!

*(Note: With [`ollama-web`](https://github.com/AjarnSpencer/ollama-web), voice is already enabled by default—just run `ollama-web "your question"` without any pipe!)*

---

### Tutorial 3 — Voice Companion for Local LLMs
Turn any local Ollama model into a conversational voice assistant:
```bash
# Ask llama3 for a bedtime story and listen:
ollama run llama3 "Tell me a short 3-sentence fable about a wise owl" | ollama-speak

# Ask Mistral for advice:
ollama run mistral "Give me one piece of life advice" | ollama-speak
```

---

### Tutorial 4 — Multi-Language Script Routing
`ollama-speak` automatically identifies language scripts without requiring manual flags:
```bash
# Automatic Thai detection (speaks in natural Thai via th-TH-NiwatNeural):
ollama-speak "พระราชบัญญัติ สมุนไพรควบคุม กัญชา พ.ศ. 2568"

# Automatic Japanese detection:
ollama-speak "こんにちは、世界！"

# Automatic Spanish detection:
ollama-speak "Buenos días a todos. Bienvenidos a la conferencia."
```
To force a specific voice or alternate gender, pass `-v`:
```bash
# Thai female voice:
ollama-speak -v th-female "สวัสดีค่ะ ยินดีต้อนรับค่ะ"

# American English female voice:
ollama-speak -v en-us-female "Good morning, how can I assist you today?"
```

---

### Tutorial 5 — Adjusting Speed and Pitch
Fine-tune narration pacing for quick briefings or slower pronunciation:
```bash
# 20% faster speech for fast news briefings:
ollama-speak -r "+20%" "Breaking news: New developments in renewable energy announced today."

# 10% slower speech with a deeper pitch:
ollama-speak -r "-10%" -p "-3Hz" "Please listen carefully to the following safety instructions."
```

---

### Tutorial 6 — Saving Spoken Audio to MP3 Files
Export audio directly to an `.mp3` file instead of playing through your speakers:
```bash
# Save an article summary to audio:
ollama-web "Explain quantum computing in simple terms" | ollama-speak -o quantum_summary.mp3

# Verify the file was written:
ls -lh quantum_summary.mp3
```

---

### Tutorial 7 — Local Offline Acceleration (`--local`)
If you have local offline TTS tooling installed (such as Kokoro-82M, Piper, or an `ai-say` workstation wrapper) and want zero network calls for English text:
```bash
ollama-speak --local "Running completely offline using local workstation weights."
```
*Note: If Thai or Asian text is detected, `ollama-speak` automatically routes to native Edge-TTS to protect local English models from character spelling bugs (`tailaty`).*

---

### Tutorial 8 — Listing Voice Aliases
To inspect common voice presets at a glance:
```bash
ollama-speak --list-voices
```

Output:
```text
Popular Edge-TTS Voices and Aliases:
------------------------------------------------------------------
  en-gb           -> en-GB-RyanNeural
  en-us           -> en-US-GuyNeural
  en-us-female    -> en-US-JennyNeural
  th              -> th-TH-NiwatNeural
  th-female       -> th-TH-PremwadeeNeural
  zh              -> zh-CN-YunxiNeural
  ja              -> ja-JP-NanamiNeural
  ko              -> ko-KR-SunHiNeural
  es              -> es-ES-AlvaroNeural
  fr              -> fr-FR-HenriNeural
  de              -> de-DE-ConradNeural
  ru              -> ru-RU-DmitryNeural
  ar              -> ar-SA-HamedNeural
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
