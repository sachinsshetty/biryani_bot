import yt_dlp

def download_video(url, output_path):
    ydl_opts = {'format': 'mp4', 'outtmpl': output_path}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])