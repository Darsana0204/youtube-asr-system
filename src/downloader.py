import yt_dlp
import os
import glob

def download_audio(url):
    os.makedirs("audio", exist_ok=True)

    # Delete any previously downloaded audio
    for file in glob.glob("audio/audio.*"):
        os.remove(file)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio/audio.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename