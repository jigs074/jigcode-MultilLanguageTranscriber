# app.py

import streamlit as st
from transcriber import process_audio_file

st.set_page_config(
    page_title="JigCode – Multi-Language Transcriber",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ JigCode – Free Multi-Language Transcriber")
st.write(
    "Upload any audio/video file and get **English transcript + subtitles** "
    "and translated subtitles in multiple languages. "
    "Everything runs locally – no API keys, no subscription."
)

# -----------------------------
# Language options
# -----------------------------

LANG_OPTIONS = {
    "French (fr)": "fr",
    "Spanish (es)": "es",
    "German (de)": "de",
    "Hindi (hi)": "hi",
    "Italian (it)": "it",
    "Portuguese (pt)": "pt",
    "Arabic (ar)": "ar",
    "Chinese (zh)": "zh",
}

st.sidebar.header("Settings")
selected_lang_labels = st.sidebar.multiselect(
    "Select target subtitle languages:",
    options=list(LANG_OPTIONS.keys()),
    default=["French (fr)", "Spanish (es)"],
)

target_lang_codes = [LANG_OPTIONS[label] for label in selected_lang_labels]

st.sidebar.info(
    "Note: First run for each language will download translation models. "
    "This can take a bit, but later runs are much faster."
)

# -----------------------------
# File upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload audio/video file",
    type=["mp3", "wav", "m4a", "mp4", "mkv", "mov"],
)

if uploaded_file is not None:
    st.write(f"**Selected file:** `{uploaded_file.name}` ({uploaded_file.size / 1_000_000:.2f} MB)")

    if st.button("🚀 Transcribe & Translate"):
        if not target_lang_codes:
            st.warning("Please select at least one target language in the sidebar.")
        else:
            with st.spinner("Processing... this may take a few minutes on CPU."):
                outputs = process_audio_file(
                    uploaded_file_bytes=uploaded_file.read(),
                    filename=uploaded_file.name,
                    target_lang_codes=target_lang_codes,
                )

            st.success("✅ Done! Download your transcript and subtitles below.")

            # Show English transcript preview
            transcript_en_bytes = outputs.get("transcript_en.txt", b"")
            transcript_en = transcript_en_bytes.decode("utf-8", errors="ignore")

            if transcript_en:
                st.subheader("English Transcript (Preview)")
                st.text_area(
                    "Transcript (English)",
                    value=transcript_en[:5000],  # preview only
                    height=200,
                )

            st.subheader("Download Files")

            for filename, content in outputs.items():
                st.download_button(
                    label=f"Download {filename}",
                    data=content,
                    file_name=filename,
                    mime="text/plain",
                )

else:
    st.info("👆 Upload an audio/video file to get started.")
