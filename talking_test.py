from decouple import config
import os

from auth import Auth
from connection import Connection


class TestTalking:
    def test_handle_not_json(self):
        conn = Connection('test', config('ORDER_SERVER_IP'), #+ connection
                          config('ORDER_SERVER_PORT'))
        assert conn.handle('test') == None

    def test_handle_no_link(self):
        conn = Connection('test', config('ORDER_SERVER_IP'), #+ connection
                          config('ORDER_SERVER_PORT'))
        data = '{"id": "test"}'
        assert conn.handle(data) == None

    def test_handle_no_id(self):
        conn = Connection('test', config('ORDER_SERVER_IP'), #+ connection
                          config('ORDER_SERVER_PORT'))
        data = '{"link": "test.com"}'
        assert conn.handle(data) == None

    # def test_handle_proper(self):
    #     data = '{"id": "test", "link": "test.com"}'
    #     assert handle(data) != None

    # Auth tests need to be run.
    def test_auth_no_file(self):
        file = config("ID_FILE")
        ip = config("AUTH_SERVER_IP")
        port = config("AUTH_SERVER_PORT")
        auth = Auth(ip, port, file) #+ auth
        try:
            os.remove(file)
        except:
            pass
        id = auth.auth()
        assert isinstance(id, str) and len(id) != 0

    def test_auth_empty_file(self):
        file = config("ID_FILE")
        id = None
        ip = config("AUTH_SERVER_IP")
        port = config("AUTH_SERVER_PORT")
        auth = Auth(ip, port, file) #+ auth
        with open(file, "w") as f:
            f.truncate(0)
            id = auth.auth()
        assert isinstance(id, str) and len(id) != 0
        os.remove(file)

    def test_auth_no_read_file(self):
        file = config("ID_FILE")
        ip = config("AUTH_SERVER_IP")
        port = config("AUTH_SERVER_PORT")
        auth = Auth(ip, port, file) #+ auth
        id = auth.auth(False)
        assert isinstance(id, str) and len(id) != 0
