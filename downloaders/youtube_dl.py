import os
import pytube

from downloaders.downloader import Downloader


class YoutubeDownloader(Downloader):
    def download(link, filename) -> None:
        if not os.path.isdir("video"):
            os.mkdir("video")
        save_path = "video/"
        yt = pytube.YouTube(link)
        yt.streams.filter(progressive=True, file_extension='mp4').order_by(
            'resolution').desc().first().download(save_path, filename)
