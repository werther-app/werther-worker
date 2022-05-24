from datetime import datetime
import os
import socket
import requests
import json

from process import process


class Auth:
    def __init__(self, auth_ip, auth_port, file) -> None:
        self.ip = auth_ip
        self.port = auth_port
        self.file = file

    def auth(self, read=True):
        if read == False:
            self.get_id()
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

    # method to request id from authentication server
    def request_id(self):
        response = requests.get('http://' + self.ip + ':' +
                                str(self.port) + '/auth?type=worker')
        id = response.text
        return id


class Connection:
    def __init__(self, id, order_ip, order_port) -> None:
        self.id = id
        self.ip = order_ip
        self.port = order_port

    def connect(self, auth):
        sock = socket.socket()
        sock.connect((self.ip, self.port))
        self.sock = sock
        self.login(auth)

    # login method sends first data to socket — id of worker
    # before running login worker needs to be authenticated
    def login(self, auth):
        self.sock.send(str.encode(self.id + '\n'))
        data = self.sock.recv(1024)
        if data.decode("utf-8") == 'Cannot login, wrong id.':
            self.id = auth.auth(False)
            self.login(auth)

    # method that permanently listens for data
    # if it receives data, than it passes data to handler and gets result from
    # next result is checked and send to server
    def listen(self):
        while True:
            data = self.sock.recv(1024)
            result = self.handle(data)
            if result != None:
                id = json.loads(data)['id']
                self.send_result(self.sock, id, result)
            else:
                # close socket if we have one of problems with data (server problems)
                self.sock.send(str.encode('Error' + '\n'))
                self.sock.close()
                # continue
            if not data:
                break

    # method for parsing data. it checks if we have all needed information
    # and runs processor — function that process video with neural engine and returns result
    def handle(self, data):
        try:
            order = json.loads(data)
            try:
                link = order['link']
                try:
                    # we are checking for id in data
                    _ = order['id']
                    # processor function
                    return process(link)
                except KeyError:
                    # if no id we can't response with result
                    print(
                        'No id of order, we can\'t send appropriate response to server without knowing id.')
                    return None
            except KeyError:
                # if no link, we can't process video
                print('No link in order, we can\'t process order without it\'s link.')
                return None
        except json.decoder.JSONDecodeError:
            # if not a json, bad
            print('Problem with parsing request from server.')
            return None

    # this method generates current date and time and result for server
    # it needs socket where to send, id of order and result of order
    def send_result(self, sock, id, result):
        endTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        str_result = json.dumps(result)
        if len(result) != 0:
            sock.send(str.encode(' {"id": "' + id + '", "result": ' +
                                 str_result + ', "endTime": "' + endTime + '"}' + '\n'))
        else:
            sock.send(str.encode(
                ' {"id": "' + id + '", "result": [], "endTime": "' + endTime + '"}' + '\n'))
