# Whisper Voice to Text & AI Assistant

A system-wide macOS utility that transcribes speech to text using the OpenAI Whisper API and automatically types it at the current cursor position. Optionally, the transcribed text can be sent as a prompt to ChatGPT (including the current clipboard content as context) to generate and automatically type a response.

## Features

- **Whisper Mode (`Ctrl + Alt/Option`):** Hold the keys, speak, release. The speech is transcribed and typed automatically.
- **ChatGPT Mode (`Ctrl + Cmd`):** Hold the keys, speak a prompt, release. The prompt and the current clipboard content are sent to ChatGPT. The generated response is typed automatically.
- **Smart Model Routing:** The tool automatically detects mathematical requests and uses `o3-mini`. For general requests, `gpt-4o-mini` is used.

## Requirements and Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables:
   Copy `.env.template` to `.env` and insert your OpenAI API key:
   ```bash
   cp .env.template .env
   ```
   *(Edit `.env` and set `OPENAI_API_KEY=sk-...`)*

## Local Execution

```bash
python src/main.py
```

## Compiling a Standalone Executable

The project can be compiled into a single macOS executable using PyInstaller:

```bash
pyinstaller --onefile --noconsole --name "WhisperAssistant" src/main.py
```
*Note: Allow the compiled app access in macOS System Settings > Privacy & Security > Accessibility, so it can monitor keystrokes and automatically type text.*

## Architecture & Modules

The project is divided into clear modules under the `src/` folder:
- `src/main.py`: Entry point and management of global keyboard events.
- `src/audio_recorder.py`: Logic for microphone recording and audio queuing.
- `src/openai_api.py`: Communication with the OpenAI API (Whisper & ChatGPT).
- `src/system_utils.py`: macOS-specific functions (reading the clipboard, simulating keystrokes via `osascript`).
- `src/config.py`: Loading environment variables and defining central constants.
