import yt_dlp

url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

with yt_dlp.YoutubeDL({}) as ydl:
    info = ydl.extract_info(url, download=False)
    print(info["title"])