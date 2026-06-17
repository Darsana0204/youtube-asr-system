import yt_dlp

url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "audio/test.%(ext)s"
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("Downloaded successfully!")