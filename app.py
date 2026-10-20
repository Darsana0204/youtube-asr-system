
import os
import re
import time
from pathlib import Path

import streamlit as st

from src.downloader import download_audio
from src.chunker import split_audio
from src.transcriber import transcribe_audio

st.set_page_config(
    page_title="YouTube ASR Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #172554;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
    }

    div.stButton > button[kind="primary"] {
        background-color: #2563eb;
        border-radius: 10px;
        border: none;
        padding: 0.65rem 1.2rem;
        font-weight: 600;
    }

    div.stDownloadButton > button {
        border-radius: 8px;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def valid_youtube_url(url: str) -> bool:
    """Check common YouTube URL formats."""
    pattern = (
        r"^(https?://)?"
        r"(www\.)?"
        r"(youtube\.com/(watch\?.*v=|shorts/|live/|embed/)"
        r"|youtu\.be/)"
        r"[A-Za-z0-9_-]{11}"
    )
    return bool(re.match(pattern, url.strip()))


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    milliseconds = round(float(seconds) * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)

    return (
        f"{hours:02}:{minutes:02}:{secs:02},"
        f"{milliseconds:03}"
    )


def create_srt(segments) -> str:
    """Build an SRT subtitle file from transcript segments."""
    subtitles = []

    for index, segment in enumerate(segments, start=1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = str(segment["text"]).strip()

        subtitles.append(
            f"{index}\n{start} --> {end}\n{text}\n"
        )

    return "\n".join(subtitles)


def create_txt(segments) -> str:
    """Build a plain-text transcript."""
    return "\n".join(
        str(segment["text"]).strip()
        for segment in segments
    )


def safe_filename(name: str) -> str:
    """Create a filename that works on common operating systems."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip(" .") or "transcript"

with st.sidebar:
    st.markdown("## 🎙️ YouTube ASR Studio")
    st.caption("Audio transcription workspace")

    st.divider()

    st.markdown("### How to use")
    st.markdown(
        """
        1. Paste a YouTube video URL.
        2. Click **Transcribe Audio**.
        3. Wait for processing to finish.
        4. Read or download the transcript.
        """
    )

    st.divider()

    st.markdown("### Features")
    st.markdown(
        """
        - YouTube audio downloading
        - Timestamped transcription
        - Plain-text export
        - SRT subtitle export
        """
    )

    st.divider()
    st.caption("Use videos you have permission to access and transcribe.")

st.markdown(
    '<div class="main-title">🎙️ YouTube ASR Studio</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Convert YouTube audio into readable, timestamped text.'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown("### 🔗 Enter a YouTube video")

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=XXXXXXXXXXX",
    help="Paste a YouTube video link.",
)

transcribe_clicked = st.button(
    "🚀 Transcribe Audio",
    type="primary",
    use_container_width=True,
)

if transcribe_clicked:
    if not url.strip():
        st.warning("Please enter a YouTube URL.")

    elif not valid_youtube_url(url):
        st.error(
            "That URL does not look like a standard YouTube video link. "
            "Please check it and try again."
        )

    else:
        start_time = time.time()

        try:
            with st.status(
                "Starting transcription workflow...",
                expanded=True,
            ) as status:
                st.write("📥 Downloading audio from YouTube...")

                audio_path = download_audio(url.strip())

                if not audio_path or not os.path.isfile(audio_path):
                    raise FileNotFoundError(
                        "The downloader did not produce an audio file."
                    )

                st.write("✅ Audio downloaded successfully.")

                st.write("🧠 Transcribing audio...")

                transcript_data = transcribe_audio(audio_path)

                if not transcript_data:
                    raise ValueError(
                        "No transcript was returned. "
                        "The video may contain no recognizable speech."
                    )

                segments = []

                for segment in transcript_data:
                    if not isinstance(segment, dict):
                        continue

                    if "text" not in segment:
                        continue

                    segments.append(
                        {
                            "start": float(segment.get("start", 0)),
                            "end": float(segment.get("end", 0)),
                            "text": str(segment["text"]).strip(),
                        }
                    )

                if not segments:
                    raise ValueError(
                        "The transcription result contained no usable segments."
                    )

                status.update(
                    label="Transcription completed!",
                    state="complete",
                    expanded=False,
                )

            elapsed_time = time.time() - start_time

            os.makedirs("transcripts", exist_ok=True)

            filename = safe_filename(
                Path(str(audio_path)).stem
            )

            txt_content = create_txt(segments)
            srt_content = create_srt(segments)

            txt_path = os.path.join(
                "transcripts",
                f"{filename}.txt",
            )
            srt_path = os.path.join(
                "transcripts",
                f"{filename}.srt",
            )

            with open(txt_path, "w", encoding="utf-8") as file:
                file.write(txt_content)

            with open(srt_path, "w", encoding="utf-8") as file:
                file.write(srt_content)

            st.session_state["transcript_segments"] = segments
            st.session_state["transcript_txt"] = txt_content
            st.session_state["transcript_srt"] = srt_content
            st.session_state["processing_time"] = elapsed_time
            st.session_state["transcript_filename"] = filename
            st.session_state["transcript_source_url"] = url.strip()

            st.success("Your transcript is ready!")

        except Exception as error:
            st.error(
                "Transcription failed. Check the URL, internet connection, "
                "FFmpeg setup, and transcription model."
            )
            st.exception(error)


if st.session_state.get("transcript_segments"):
    segments = st.session_state["transcript_segments"]
    txt_content = st.session_state["transcript_txt"]
    srt_content = st.session_state["transcript_srt"]
    elapsed_time = st.session_state["processing_time"]
    filename = st.session_state["transcript_filename"]

    st.divider()
    st.markdown("## 📊 Transcription Summary")

    total_segments = len(segments)
    total_duration = max(
        (segment["end"] for segment in segments),
        default=0,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Audio duration",
            f"{total_duration:.1f} sec",
        )

    with col2:
        st.metric(
            "Processing time",
            f"{elapsed_time:.2f} sec",
        )

    with col3:
        st.metric(
            "Transcript segments",
            total_segments,
        )

    st.divider()
    st.markdown("## 📝 Transcript")

    tab1, tab2 = st.tabs(
        ["📄 Timestamped transcript", "🔤 Full text"]
    )

    with tab1:
        search_text = st.text_input(
            "Search transcript",
            placeholder="Type a word or phrase...",
            key="transcript_search",
        )

        filtered_segments = [
            segment
            for segment in segments
            if search_text.lower() in segment["text"].lower()
        ]

        if not filtered_segments:
            st.info("No matching transcript segments found.")

        for index, segment in enumerate(filtered_segments):
            with st.container(border=True):
                st.caption(
                    f"{segment['start']:.2f}s – "
                    f"{segment['end']:.2f}s"
                )
                st.write(segment["text"])

    with tab2:
        st.text_area(
            "Complete transcript",
            value=txt_content,
            height=350,
        )

    st.markdown("### ⬇️ Download your transcript")

    download_col1, download_col2 = st.columns(2)

    with download_col1:
        st.download_button(
            label="📄 Download TXT",
            data=txt_content,
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with download_col2:
        st.download_button(
            label="🎬 Download SRT subtitles",
            data=srt_content,
            file_name=f"{filename}.srt",
            mime="application/x-subrip",
            use_container_width=True,
        )

    st.caption(
        "Transcription accuracy depends on audio quality, "
        "the selected model, and the language spoken."
    )

else:
    st.divider()
    st.info(
        "Your transcript will appear here after you transcribe a video."
    )

st.divider()
st.caption(
    "YouTube ASR Studio · Built with Python and Streamlit"
)
