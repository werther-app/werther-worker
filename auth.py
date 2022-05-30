import os
from time import sleep
import requests


class Auth:
    def __init__(self, auth_ip: str, auth_port: str, file: str) -> None:
        self.ip = auth_ip
        self.port = auth_port
        self.file = file

    def auth(self, read=True):
        if read == False:
            return self.get_id()
        id = self.read_id()
        if id == None:
            self.get_id()
        else:
            self.id = id
        return self.id

    def read_id(self):
        try:
            with open(self.file, "r") as f:
                # check if file is empty
                if os.stat(self.file).st_size == 0:
                    return None
                else:
                    id = f.readline()
                    return id
        except FileNotFoundError:
            return None

    def get_id(self):
        self.id = self.request_id()
        with open(self.file, "w") as f:
            f.write(self.id)
        return self.id

    # Method to request id from authentication server..
    def request_id(self):
        try:
            response = requests.get('http://' + self.ip + ':' +
                                    str(self.port) + '/auth?type=worker')
            id = response.text
        except:
            print('Cannot auth, no response from server. Retrying')
            sleep(1)
            id = self.request_id()
        return id
