# transcriber.py

import os
import tempfile
from typing import List, Dict

import whisper
import argostranslate.package
import argostranslate.translate


# -----------------------------
# 1) Load Whisper model (once)
# -----------------------------
# Options: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_SIZE = "base"
_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    return _whisper_model


# -----------------------------
# 2) Transcription
# -----------------------------

def transcribe_file_to_english(path: str) -> Dict:
    
    model = get_whisper_model()

    # task="translate" forces output to English, even if source is not English
    result = model.transcribe(path, task="translate", verbose=False)
    return result


# -----------------------------
# 3) Argos Translate: Language setup
# -----------------------------

def ensure_language_pair(from_code: str, to_code: str):
  
    # 1) Check installed translation packages first
    installed_packages = argostranslate.package.get_installed_packages()
    if any(p.from_code == from_code and p.to_code == to_code for p in installed_packages):
        return  # already installed

    # 2) If not installed, look in available packages
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    matching_packages = [
        p for p in available_packages
        if p.from_code == from_code and p.to_code == to_code
    ]
    if not matching_packages:
        raise RuntimeError(f"No Argos package found for {from_code} -> {to_code}")

    package = matching_packages[0]
    download_path = package.download()
    argostranslate.package.install_from_path(download_path)


def get_translator(from_code: str, to_code: str):
    
    languages = argostranslate.translate.get_installed_languages()

    from_lang = next((l for l in languages if l.code == from_code), None)
    to_lang = next((l for l in languages if l.code == to_code), None)

    if not from_lang:
        raise RuntimeError(f"Language '{from_code}' not installed")
    if not to_lang:
        raise RuntimeError(f"Language '{to_code}' not installed")

    return from_lang.get_translation(to_lang)


# -----------------------------
# 4) Translation
# -----------------------------

def translate_text(text: str, to_code: str, from_code: str = "en") -> str:
    """
    Translate text from from_code to to_code using Argos Translate.
    """
    ensure_language_pair(from_code, to_code)
    translator = get_translator(from_code, to_code)
    return translator.translate(text)


# -----------------------------
# 5) SRT helpers
# -----------------------------

def _format_timestamp(seconds: float) -> str:
    
    ms = int(seconds * 1000)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def build_srt_from_segments(segments: List[Dict]) -> str:
    
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = _format_timestamp(seg["start"])
        end = _format_timestamp(seg["end"])
        text = seg["text"].strip()

        if not text:
            continue

        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")  # blank line between entries

    return "\n".join(lines)


def build_translated_srt(segments: List[Dict], target_lang_code: str) -> str:
    
    ensure_language_pair("en", target_lang_code)
    translator = get_translator("en", target_lang_code)

    lines = []
    for i, seg in enumerate(segments, start=1):
        start = _format_timestamp(seg["start"])
        end = _format_timestamp(seg["end"])
        text_en = seg["text"].strip()
        if not text_en:
            continue

        text_translated = translator.translate(text_en).strip()

        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text_translated)
        lines.append("")

    return "\n".join(lines)


# -----------------------------
# 6) High-level pipeline
# -----------------------------

def process_audio_file(
    uploaded_file_bytes: bytes,
    filename: str,
    target_lang_codes: List[str],
) -> Dict[str, bytes]:
    
    # Save to temp file
    suffix = os.path.splitext(filename)[1] or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file_bytes)
        tmp_path = tmp.name

    try:
        # 1) Transcribe + translate to English (Whisper)
        result = transcribe_file_to_english(tmp_path)
        text_en = result["text"].strip()
        segments = result.get("segments", [])

        outputs: Dict[str, bytes] = {}

        # 2) Raw English transcript
        outputs["transcript_en.txt"] = text_en.encode("utf-8")

        # 3) English SRT
        srt_en = build_srt_from_segments(segments)
        outputs["subtitles_en.srt"] = srt_en.encode("utf-8")

        # 4) Translated SRTs
        for code in target_lang_codes:
            srt_translated = build_translated_srt(segments, code)
            outputs[f"subtitles_{code}.srt"] = srt_translated.encode("utf-8")

        return outputs

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
