import yt_dlp

def download_audio(url):
    ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "audio/audio.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "audio/audio.webm"