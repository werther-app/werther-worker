from datetime import datetime
import os
import socket
import requests
import json
from decouple import config

from talking import *


if __name__ == '__main__':
    auth_ip = config('AUTH_SERVER_IP')
    auth_port = config('AUTH_SERVER_PORT')
    order_ip = config('ORDER_SERVER_IP')
    order_port = config('ORDER_SERVER_PORT')

    test()

    id = auth(auth_ip, auth_port)
    server = connect(order_ip, order_port)
    login(server, id)

    listen()
