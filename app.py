import streamlit as st
import time

from src.downloader import download_audio
from src.chunker import split_audio
from src.transcriber import transcribe_audio

st.title("YouTube Speech Recognition")

url = st.text_input("Enter YouTube URL")

if st.button("Transcribe"):

    start_time = time.time()

    # Download
    st.write("Downloading audio...")
    audio_path = download_audio(url)

    # Split
    st.write("Splitting audio into chunks...")
    chunks = split_audio(audio_path)

    st.write(f"Total chunks: {len(chunks)}")

    transcript_data = []

    # Transcribe
    st.write("Transcribing chunks...")

    progress = st.progress(0)

    for i, chunk in enumerate(chunks):
        result = transcribe_audio(chunk)
        transcript_data.extend(result)

        progress.progress((i + 1) / len(chunks))

    end_time = time.time()

    st.success("Completed!")
    st.write(f"Processing Time: {end_time - start_time:.2f} seconds")

    st.subheader("Transcript")

    full_text = ""

    for segment in transcript_data:
        st.write(
            f"[{segment['start']:.1f}s → {segment['end']:.1f}s] "
            f"{segment['text']}"
        )

        full_text += segment["text"] + "\n"

    with open(
        "transcripts/transcript.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(full_text)

    st.success("Transcript saved!")

    st.download_button(
        "Download Transcript",
        data=full_text,
        file_name="transcript.txt",
        mime="text/plain",
    )