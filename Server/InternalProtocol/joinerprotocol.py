import json

from .common import int_to_bytes, int_from_bytes, INT_LENGTH

ENCODING = "utf-8"

PRECIPITATION_FILTER = 1
YEAR_FILTER = 2
MONTREAL_FILTER = 3


class JoinerMessage():
    def __init__(self, type, data):
        self.type = type
        self.contet = data

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
