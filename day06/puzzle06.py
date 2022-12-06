"""https://adventofcode.com/2022/day/6"""
from collections import deque

def search_unique_sequence(data: bytes, num_unique: int) -> int:
    """returns the index of the start of the datagram"""
    buf = deque(maxlen=num_unique-1)
    for (idx, ch) in enumerate(data):
        while ch in buf:
            # can't have duplicate characters. remove characters until there are no dups
            buf.popleft()
        if ch not in buf and buf.maxlen == len(buf):
            # found our marker
            return idx + 1
        buf.append(ch)
    raise ValueError(f"unique sequence of length {num_unique} not found in data")

if __name__ == '__main__':
    with open('input.txt', 'rb') as fptr:
        data: bytes = fptr.read()
    datagram_idx = search_unique_sequence(data, num_unique=4)
    print(f"start-of-packet idx = {datagram_idx}")
    msg_idx = search_unique_sequence(data[datagram_idx:], num_unique=14) + datagram_idx
    print(f"start-of-msg idx = {msg_idx}")

