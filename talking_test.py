import os
from decouple import config

from talking import *


class TestTalking:
    def test_handle_not_json(self):
        assert handle('test') == None

    def test_handle_no_link(self):
        data = '{"id": "test"}'
        assert handle(data) == None

    def test_handle_no_id(self):
        data = '{"link": "test.com"}'
        assert handle(data) == None

    # def test_handle_proper(self):
    #     data = '{"id": "test", "link": "test.com"}'
    #     assert handle(data) != None

    # auth tests need to be run
    def test_auth_no_file(self):
        file = config("ID_FILE")
        ip = config("AUTH_SERVER_IP")
        port = config("AUTH_SERVER_PORT")
        os.remove(file)
        id = auth(ip, port)
        assert isinstance(id, str) and len(id) != 0

    def test_auth_empty_file(self):
        file = config("ID_FILE")
        id = None
        ip = config("AUTH_SERVER_IP")
        port = config("AUTH_SERVER_PORT")
        with open(file, "w") as f:
            f.truncate(0)
            id = auth(ip, port)
        assert isinstance(id, str) and len(id) != 0
        os.remove(file)
