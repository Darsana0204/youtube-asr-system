import streamlit as st
import time
from src.downloader import download_audio
from src.transcriber import transcribe_audio
st.title("YouTube Speech recognition")
url= st.text_input("Enter YouTube URL")
if st.button("Transcribe"):
    start_time= time.time()
    st.write("Downloading audio...")
    audio_path= download_audio(url)

    st.write("Transcribing...")
    transcript_data = transcribe_audio(audio_path)
    st.write(type(transcript_data))
    st.write(transcript_data)
    end_time= time.time()
    st.success("Completed!")
    st.write(f"Proccessing Time: {end_time-start_time:.2f} seconds")
    st.subheader("Transcript")
    full_text= ""
    for segment in transcript_data: 
        st.write(
            f"[{segment['start']}s -> {segment['end']}s] "
            f"{segment['text']}"
        )

        full_text+= segment["text"]+ "\n"

    with open(
        "transcripts/transcript.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(full_text)

    st.success("Transcript saved!")
    