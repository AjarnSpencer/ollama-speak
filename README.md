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
- **Unix Composable (STDIN Pipe):** Pipe text directly from any command or LLM CLI:
  ```bash
  ollama-web "Who won the Champions League?" | ollama-speak
  ollama run llama3 "Tell me a joke" | ollama-speak
  ```
- **Native Cross-Platform Playback:** Uses pre-installed operating system audio tools:
  - **macOS:** `afplay`
  - **Windows:** PowerShell `WMPlayer.OCX` / `SoundPlayer`
  - **Linux:** Automatically cascades through `mpv`, `ffplay`, `mpg123`, `cvlc`, `pw-play`, and `paplay`
- **Optional Local Acceleration:** Supports local offline Piper, Kokoro-82M, or `ai-say` when `--local` is specified.
- **Save to File:** Export spoken audio directly to `.mp3` via `-o <file.mp3>`.

---

## 🚀 Quickstart and Installation

### Option 1: Via PyPI
```bash
pip install --upgrade ollama-speak
```

### Option 2: From GitHub
```bash
pip install --upgrade git+https://github.com/AjarnSpencer/ollama-speak.git
```

### Option 3: One-Line Installer Script
**Linux & macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/AjarnSpencer/ollama-speak/main/install.ps1 | iex
```

---

## 🖥️ CLI Usage Examples

### 1. Direct Text Narration
```bash
ollama-speak "Welcome back. All systems are operational."
```

### 2. Piped Input from ollama-web
```bash
ollama-web "What is the capital of Thailand?" | ollama-speak
```

### 3. Piped Input from Ollama LLM
```bash
ollama run llama3 "Give me a 3-sentence inspirational quote" | ollama-speak
```

### 4. Specifying Voice or Language
```bash
# Speak in Thai:
ollama-speak -v th "พระราชบัญญัติ สมุนไพรควบคุม กัญชา พ.ศ. 2568"

# Speak in Japanese:
ollama-speak -v ja "こんにちは、世界！"

# List popular voice aliases:
ollama-speak --list-voices
```

### 5. Adjust Speed and Pitch
```bash
ollama-speak -r "+20%" "Reading at twenty percent higher speed."
```

### 6. Save Audio to MP3
```bash
ollama-speak -o summary.mp3 "Saving audio output to disk."
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
