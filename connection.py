from datetime import datetime
import socket
from time import sleep
import json

from processor import Processor
from auth import Auth

class Connection:
    def __init__(self, id, order_ip, order_port) -> None:
        self.id = id
        self.ip = order_ip
        self.port = order_port

    def connect(self, auth):
        sock = None
        while True:
            try:
                sock = socket.socket()
                sock.connect((self.ip, self.port))
                break
            except:
                print('Cannot login, no response from server. Retrying.')
                sleep(1)
        self.sock = sock
        self.login(auth)

    # Login method sends first data to socket — id of worker.
    # Before running login worker needs to be authenticated.
    def login(self, auth):
        self.sock.send(str.encode(self.id + '\n'))
        data = self.sock.recv(1024)
        if data.decode("utf-8") == 'Cannot login, wrong id.':
            self.id = auth.Auth.auth(False)
            self.login(auth)

    # Method that permanently listens for data
    # if it receives data, than it passes data to handler and gets result from
    # next result is checked and send to server.
    def listen(self):
        while True:
            data = self.sock.recv(1024)
            result = self.handle(data)
            if result != None:
                id = json.loads(data)['id']
                self.send_result(self.sock, id, result)
            else:
                # Close socket if we have one of problems with data (server problems).
                self.sock.send(str.encode('Error' + '\n'))
                self.sock.close()

                # Continue.
            if not data:
                break

    # Method for parsing data. it checks if we have all needed information
    # and runs processor — function that process video with neural engine and returns result.
    def handle(self, data):
        try:
            order = json.loads(data)
            try:
                link = order['link']
                try:
                    # We are checking for id in data.
                    _ = order['id']
                    # Processor function.
                    processor = Processor(link)
                    return processor.process()
                except KeyError:
                    # If no id we can't response with result.
                    print(
                        'No id of order, we can\'t send appropriate response to server without knowing id.')
                    return None
            except KeyError:
                # If no link, we can't process video.
                print('No link in order, we can\'t process order without it\'s link.')
                return None
        except json.decoder.JSONDecodeError:
            # If not a json, bad.
            print('Problem with parsing request from server.')
            return None

    # This method generates current date and time and result for server.
    # It needs socket where to send, id of order and result of order.
    def send_result(self, sock, id, result):
        endTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        str_result = json.dumps(result)
        if len(result) != 0:
            sock.send(str.encode(' {"id": "' + id + '", "result": ' +
                                 str_result + ', "endTime": "' + endTime + '"}' + '\n'))
        else:
            sock.send(str.encode(
                ' {"id": "' + id + '", "result": [], "endTime": "' + endTime + '"}' + '\n'))