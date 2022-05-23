from datetime import datetime
import os
import socket
import requests
import json
from decouple import config

from process import process


def connect(ip, port):
    sock = socket.socket()
    sock.connect((ip, port))
    return sock


# method that returns id
# it needs ip and port of authentication server
# to get id it checks id file and if there is checks for first line of file
# if file is empty or doesn't present, method runs another method to get id from server
def auth(ip, port):
    id_file = config("ID_FILE")
    id = None
    try:
        with open(id_file, "r") as file:
            # check if file is empty
            if os.stat(id_file).st_size == 0:
                id = get_id(ip, port, id_file)
            else:
                id = file.readline()
    except FileNotFoundError:
        id = get_id(ip, port, id_file)
    return id


# method to get id from authentication server and write to file
def get_id(ip, port, file):
    id = request_id(ip, port)
    with open(file, "w") as f:
        f.write(id)
    return id


# method to request id from authentication server
def request_id(ip, port):
    response = requests.get('http://' + ip + ':' + port + '/auth?type=worker')
    id = response.text
    return id


# login method sends first data to socket — id of worker
# before running login worker needs to be authenticated
def login(sock, id):
    sock.send(str.encode(id + '\n'))


# method that permanently listens for data
# if it receives data, than it passes data to handler and gets result from
# next result is checked and send to server
def listen(sock):
    while True:
        data = sock.recv(1024)
        result = handle(data)
        if result != None:
            id = data['id']
            send_result(sock, id, result)
        else:
            # close socket if we have one of problems with data (server problems)
            sock.send(str.encode('Error' + '\n'))
            sock.close()
        if not data:
            break


# method for parsing data. it checks if we have all needed information
# and runs processor — function that process video with neural engine and returns result
def handle(data):
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
def send_result(sock, id, result):
    endTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    if len(result != 0):
        sock.send(str.encode('{"id": "' + id + '", "result": ' +
                  result + ', "endTime": "' + endTime + '"}' + '\n'))
    else:
        sock.send(str.encode(
            '{"id": "' + id + '", "result": [], "endTime": "' + endTime + '"}' + '\n'))
