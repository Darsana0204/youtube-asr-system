from pydub import AudioSegment
import os

def split_audio(audio_path, chunk_length_ms=30000):
    audio = AudioSegment.from_file(audio_path)

    os.makedirs("chunks", exist_ok=True)

    chunk_files = []

    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]

        chunk_path = f"chunks/chunk_{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")

        chunk_files.append(chunk_path)

    return chunk_files