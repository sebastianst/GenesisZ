from zcash.core import coreparams as coreparams
import struct
from bitstring import pack

def bytes_from_solution(sol):
    # A solution integer array contains 2^k/8 fields of values with max n/(k+1)+1 bits
    n, k = coreparams.N, coreparams.K
    size = n//(k+1) + 1
    count = 2**(coreparams.K)
    assert len(sol) == count, \
            "Solution array contains wrong number of integers."

    return pack('%i*uint:%i' % (count, size), *sol).tobytes()
