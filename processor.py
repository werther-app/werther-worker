from calendar import c
import math
import re

from numpy import double
from downloaders.downloader import Downloader
from downloaders.youtube_dl import YoutubeDownloader
from decouple import config
import cv2
import pytesseract
import os


class Processor:
    def __init__(self, link) -> None:
        self.VIDEO_FILE = config('VIDEO_FILE')
        self.VIDEO_FOLDER = config('VIDEO_FOLDER')
        self.link = link
        self.understand_service()

    def process(self):
        self.downloader.download(self.link, self.VIDEO_FILE)
        self.analyze()

    def understand_service(self):
        if re.compile('(.*)youtu(\.*)be(.*)').match(self.link):
            self.downloader = YoutubeDownloader()
        else:
            self.downloader = Downloader()

    def analyze(self):
        WINDOW_CASCADE = config('WINDOW_CASCADE')

        # Cascade parameters
        SCALE_FACTOR = double(config('SCALE_FACTOR'))
        MIN_NEIGHBORS = int(config('MIN_NEIGHBORS'))
        FLAGS = int(config('FLAGS'))
        MIN_SIZE_W = int(config('MIN_SIZE_W'))
        MIN_SIZE_H = int(config('MIN_SIZE_H'))
        MAX_SIZE_W = int(config('MAX_SIZE_W'))
        MAX_SIZE_H = int(config('MAX_SIZE_H'))

        MIN_SIZE = (MIN_SIZE_W, MIN_SIZE_H)
        MAX_SIZE = (MAX_SIZE_W, MAX_SIZE_H)

        file_count = 0
        output = "Can't resolve symbols"
            cap = cv2.VideoCapture(fr'{self.VIDEO_FOLDER}/{self.VIDEO_FILE}')

        fps = math.floor(cap.get(5))
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
                if len(terminals) == 0:
                    ret, frame = cap.read()
                    continue
                for (x, y, w, h) in terminals:
                        cv2.rectangle(frame, (x, y), (x+w, y+h),
                                      (0, 255, 0), 2)
                    cv2.imshow('terminals', frame)
                    scoped_frame = frame[y:y + h, x:x + w]
                    # using tesseract library to locate and transform image of letter to string
                    output = pytesseract.image_to_string(scoped_frame)
                    if output:
                        # we append text and deletes every unnecessery space and enters
                        str_list.append(" ".join(output.split()))
            ret, frame = cap.read()
            print("frame " + str(file_count) + " is done")
        try:
                os.remove(f'{self.VIDEO_FOLDER}/{self.VIDEO_FILE}')
                os.rmdir(self.VIDEO_FOLDER)
        except:
            print("Video file or directory not exist or doesn't download.")

        cap.release()
        cv2.destroyAllWindows()
        return str_list
