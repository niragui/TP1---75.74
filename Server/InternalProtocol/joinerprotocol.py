import json

from common import int_to_bytes, int_from_bytes, INT_LENGTH
from constants import STOP_TYPE


ENCODING = "utf-8"

JOIN_TYPE = 1

class JoinerMessage():
    def __init__(self, data):
        self.type = self.get_type(data)
        self.data = data

    def get_type(self, data):
        if isinstance(data, int):
            return STOP_TYPE
        else:
            return JOIN_TYPE

    def create_message(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        string_json = json.dumps(self.data).encode(ENCODING)

        bytes += string_json

        return bytes


def read_message(bytes_read):
    message_type = int_from_bytes(bytes_read[:INT_LENGTH])
    message = json.loads(bytes_read[INT_LENGTH:].decode(ENCODING))

    return message_type, message
