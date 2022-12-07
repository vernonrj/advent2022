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

def search_unique_sequence_2(data: bytes, num_unique: int) -> int:
    """returns the index of the start of the datagram, but better"""
    mask = int("ff" * (num_unique-1), 16)
    stream = data[0] # start with a byte from the stream
    last_dup = 0 # track the index of our previously found duplicate
    for (idx, byte) in enumerate(data[1:], 1):
        num_to_check = min(idx, num_unique-1) # this will help us build our masks
        bitpat = int("7F" * num_to_check, 16)
        # duplicate byte N times, xor with our stream, then check the result for 0x00
        bytemask = int(hex(byte)[2:] * num_to_check, 16)
        xord = stream ^ bytemask # matching bytes will now be zeroed (0x00)
        # detect zero bytes in a word.
        # stolen from https://graphics.stanford.edu/~seander/bithacks.html#ZeroInWord
        # python supports integer math on arbitrary-size integers :)
        shifted = ~((((xord & bitpat) + bitpat) | xord) | bitpat)
        zero_detected = shifted == (-1 << (num_to_check*8))
        if zero_detected and (idx - last_dup) >= num_unique:
            # we found the unique sequence!
            return idx + 1
        elif not zero_detected: # duplicate byte found in stream
            # I dunno how we do this efficiently ¯\_(ツ)_/¯
            for (dup_idx, c) in enumerate(data[idx-num_to_check:idx], start=idx-num_to_check):
                # if we find the offending char and it occurs later than our previous dup, mark it
                if c == byte and dup_idx > last_dup:
                    last_dup = dup_idx
        stream = ((stream << 8) | byte) & mask # cycle the byte into the stream
        

if __name__ == '__main__':
    with open('input.txt', 'rb') as fptr:
        data: bytes = fptr.read()
    datagram_idx = search_unique_sequence_2(data, num_unique=4)
    print(f"start-of-packet idx = {datagram_idx}")
    msg_idx = search_unique_sequence_2(data[datagram_idx:], num_unique=14) + datagram_idx
    print(f"start-of-msg idx = {msg_idx}")

