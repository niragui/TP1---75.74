MAX_SIZE = 8000
INT_LENGTH = 4


def int_to_bytes(x: int, length: int = INT_LENGTH) -> bytes:
    return x.to_bytes(length, 'big')

 
def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def read_socket(socket_connected, bytes):
    buffer = b""
    while len(buffer) < bytes:
        missing = bytes - len(buffer)
        if missing > MAX_SIZE:
            missing = MAX_SIZE
        aux = socket_connected.recv(missing)
        buffer += aux

    return buffer


def write_socket(socket_connected, bytes):
    sent = 0

    while sent < len(bytes):
        end = len(bytes) - sent
        if end - sent > MAX_SIZE:
            end = sent + MAX_SIZE
        aux = socket_connected.send(bytes[sent:end])
        sent += aux

    return sent


def read_int(socket_connected):
    aux = read_socket(socket_connected, INT_LENGTH)
    return int_from_bytes(aux)


def send_int(socket_connected, number):
    value = int_to_bytes(number)
    write_socket(socket_connected, value)
