# 🎙️ Offline AI Multilingual Subtitle Generator

> 📺 **Full step-by-step explanation is in the video:**  
> https://youtu.be/VIDEO_ID  
> _(Watch this first if you want a guided walkthrough of the code and setup.)_

Turn **any audio/video file** into:

- ✅ An English transcript (`.txt`)
- ✅ English subtitles (`.srt`)
- ✅ Subtitles in multiple languages (`.srt` per language)

All **offline**, **free**, and **no API keys**.

Powered by:

- [OpenAI Whisper](https://github.com/openai/whisper) for speech-to-text  
- [Argos Translate](https://github.com/argosopentech/argos-translate) for offline translation  
- [Streamlit](https://streamlit.io/) for the web UI  

---

## ✨ Features

- 🧠 **Speech → English text** using Whisper
- 🌍 **Multi-language subtitles** via Argos Translate (e.g. French, Spanish, Hindi…)
- 🎬 **Standard `.srt` format** with proper timestamps
- 🔒 **100% offline** after first model downloads
- 🖥️ Simple browser UI (Streamlit) – just upload & click

---

## 🏗️ Architecture Overview

High-level pipeline:

1. **Upload audio/video file** (mp3, wav, m4a, mp4, etc.)
2. **Whisper**:
   - Detects language
   - Transcribes + translates to **English**
   - Returns timestamped segments (`start`, `end`, `text`)
3. **Subtitle builder**:
   - Builds **English** `.srt` from Whisper segments
4. **Argos Translate**:
   - Translates each subtitle line **English → target language**
   - Builds `.srt` for each selected language (same timestamps)
5. **Streamlit UI**:
   - Shows English transcript preview
   - Exposes **Download** buttons for all generated files

---

## 📂 Project Structure

```text
.
├─ app.py             # Streamlit UI (file upload, settings, downloads)
├─ transcriber.py     # Core logic: Whisper, Argos, SRT generation
├─ requirements.txt   # Python dependencies
└─ README.md
