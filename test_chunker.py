from src.chunker import split_audio

audio_path = "audio/audio.webm"  # your downloaded file

chunks = split_audio(audio_path)

print(chunks)