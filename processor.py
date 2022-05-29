from calendar import c
import re
from downloaders.downloader import Downloader
from downloaders.youtube_dl import YoutubeDownloader
from decouple import config
import cv2
import pytesseract
import os


class Processor:
    def __init__(self, link) -> None:
        self.link = link
        self.downloader = Downloader()

    def process(self):
        self.understand_service()
        self.analyze()

    def understand_service(self):
        if re.compile('(.*)youtu(\.*)be(.*)').match(self.link):
            self.downloader = YoutubeDownloader()

    def analyze(self):
        VIDEO_FILE = config('VIDEO_FILE')
        WINDOW_CASCADE = config('WINDOW_CASCADE')

        # Cascade parameters
        SCALE_FACTOR = int(config('SCALE_FACTOR'))
        MIN_NEIGHBORS = int(config('MIN_NEIGHBORS'))
        FLAGS = int(config('FLAGS'))
        MIN_SIZE_W = int(config('MIN_SIZE_W'))
        MIN_SIZE_H = int(config('MIN_SIZE_H'))
        MAX_SIZE_W = int(config('MAX_SIZE_W'))
        MAX_SIZE_H = int(config('MAX_SIZE_H'))

        MIN_SIZE = (MIN_SIZE_W, MIN_SIZE_H)
        MAX_SIZE = (MAX_SIZE_W, MAX_SIZE_H)

        self.downloader.download(self.link, VIDEO_FILE)

        file_count = 0
        output = "can't resolve symbols"
        cap = cv2.VideoCapture(fr'{VIDEO_FILE}')

        fps = cap.get(5)
        ret, frame = cap.read()
        terminal_classifier = cv2.CascadeClassifier(WINDOW_CASCADE)

        str_list = []

        # run through every frame of the video while they exist
        while ret:
            file_count += 1
            if file_count % fps == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # locate the terminal using cascade, all variables is hard coded due they importance DO NOT CHANGE THEM!
                terminals = terminal_classifier.detectMultiScale(
                    gray, SCALE_FACTOR, MIN_NEIGHBORS, FLAGS, MIN_SIZE, MAX_SIZE)

                # skip frames without terminal
                if terminals == ():
                    continue
                for (x, y, w, h) in terminals:
                    # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    # cv2.imshow('terminals', frame)
                    scoped_frame = frame[y:y + h, x:x + w]
                    # using tesseract library to locate and transform image of letter to string
                    output = pytesseract.image_to_string(scoped_frame)
                    if output:
                        # we append text and deletes every unnecessery space and enters
                        str_list.append(" ".join(output.split()))
            ret, frame = cap.read()
        try:
            os.remove('video/{VIDEO_FILE}')
            os.rmdir("video")
        except:
            print("Video file or directory not exist or doesn't download.")

        cap.release()
        cv2.destroyAllWindows()
        return str_list
