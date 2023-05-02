INT_LENGTH = 4


def int_to_bytes(x: int, length: int = INT_LENGTH) -> bytes:
    return x.to_bytes(length, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')