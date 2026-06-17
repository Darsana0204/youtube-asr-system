from faster_whisper import WhisperModel
model= WhisperModel(
    "base", device="cpu", compute_type="int8"
)

def transcribe_audio(audio_path):
    segments, info= model.transcribe(audio_path)
    transcript_data= []

    for segment in segments:
        transcript_data.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })
    
    return transcript_data