from zcash.core import coreparams as coreparams
import struct

def bytes_from_solution(sol):
    # A solution integer array contains 2^k/8 fields of values with max n/(k+1)+1 bits
    n, k = coreparams.N, coreparams.K
    size = n//(k+1) + 1
    count = 2**(coreparams.K)
    assert len(sol) == count, \
            "Solution array contains wrong number of integers."

    u = 0
    for s in sol:
        assert (s-1) >> size == 0, "Solution field is too large: %i" % s
        u = (u << size) + s-1

    return uintvar_to_bytes(u, size*count//8)

def uintvar_to_bytes(u, l):
    """converts the variable size integer to a big-endian bytes array"""
    assert u >> (l*8) == 0, "Integer larger than 2^" + l*8
    r = b''
    for i in range(l):
        r += struct.pack('>B', u >> (i * 8) & 0xff) # TODO reverse order?!
    return r
