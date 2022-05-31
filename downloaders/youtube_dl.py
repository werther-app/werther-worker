import os
import pytube

from downloaders.downloader import Downloader


class YoutubeDownloader(Downloader):
    def download(self, link, filename, folder) -> None:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        save_path = f"{folder}/"
        yt = pytube.YouTube(link)
        yt.streams.filter(progressive=True, file_extension='mp4').order_by(
            'resolution').desc().first().download(save_path, filename)
