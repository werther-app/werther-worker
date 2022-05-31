from decouple import config

from auth import Auth
from connection import Connection


if __name__ == '__main__':
    auth_ip = config('AUTH_SERVER_IP')
    auth_port = int(config('AUTH_SERVER_PORT'))
    order_ip = config('ORDER_SERVER_IP')
    order_port = int(config('ORDER_SERVER_PORT'))
    id_file = config('ID_FILE')

    auth = Auth(auth_ip, auth_port, id_file)
    id = auth.auth()

    print(id)

    connection = Connection(id, order_ip, order_port)
    connection.connect(auth)

    connection.listen()
