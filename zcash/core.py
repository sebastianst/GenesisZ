from bitcoin.core import *
import struct

def compactSize_from_int(s):
    BO = 'big' # TODO Check byteorder
    assert 0 <= s <= 0xffffffffffffffff
    if s <= 0xfc:
        return s.to_bytes(1, byteorder=BO)
    elif s <= 0xffff:
        return [b'0xfd'] + s.to_bytes(2, byteorder=BO)
    elif s <= 0xffffffff:
        return [b'0xfe'] + s.to_bytes(4, byteorder=BO)
    else:
        return [b'0xff'] + s.to_bytes(8, byteorder=BO)

def deserialize_compactSize(f):
    csc = {0xdf: 'H', 0xfe: 'I', 0xff: 'Q'}
    s = struct.unpack(b'<B', ser_read(f,1))
    if s < 0xfd:
        return s
    else:
        t = 2**(s-0xfc)
        return struct.unpack('<{}s'.format(t), ser_read(f,t))

SOL_SIZE = 1344
ZERO32 = b'\x00'*32

class CEquihashHeader(Serializable): # TODO or make it ImmutableSerializable?
    """A Zcash Equihash solver block header - without solution"""
    __slots__ = ['nVersion', 'hashPrevBlock', 'hashMerkleRoot', 'hashReserved', 'nTime', 'nBits', 'nNonce']

    def __init__(self, nVersion=4, hashPrevBlock=ZERO32,
            hashMerkleRoot=ZERO32, hashReserved=ZERO_QUAD, nTime=0, nBits=0, nNonce=ZERO32):
        object.__setattr__(self, 'nVersion', nVersion)
        assert len(hashPrevBlock) == 32
        object.__setattr__(self, 'hashPrevBlock', hashPrevBlock)
        assert len(hashMerkleRoot) == 32
        object.__setattr__(self, 'hashMerkleRoot', hashMerkleRoot)
        assert len(hashReserved) == 32
        object.__setattr__(self, 'hashReserved', hashMerkleRoot)
        object.__setattr__(self, 'nTime', nTime)
        object.__setattr__(self, 'nBits', nBits)
        assert len(nNonce) == 32
        object.__setattr__(self, 'nNonce', nNonce)

    @classmethod
    def stream_deserialize(cls, f):
        nVersion = struct.unpack(b"<i", ser_read(f,4))[0]
        hashPrevBlock = ser_read(f,32)
        hashMerkleRoot = ser_read(f,32)
        hashReserved = ser_read(f,32)
        nTime = struct.unpack(b"<I", ser_read(f,4))[0]
        nBits = struct.unpack(b"<I", ser_read(f,4))[0]
        nNonce = ser_read(f,32)
        return cls(nVersion, hashPrevBlock, hashMerkleRoot, hashReserved, nTime, nBits, nNonce)

    def stream_serialize(self, f):
        f.write(struct.pack(b"<i", self.nVersion))
        assert len(self.hashPrevBlock) == 32
        f.write(self.hashPrevBlock)
        assert len(self.hashMerkleRoot) == 32
        f.write(self.hashMerkleRoot)
        assert len(self.hashReserved) == 32
        f.write(self.hashReserved)
        f.write(struct.pack(b"<I", self.nTime))
        f.write(struct.pack(b"<I", self.nBits))
        assert len(self.nNonce) == 32
        f.write(self.nNonce)

    @staticmethod
    def calc_difficulty(nBits):
        return CBlockHeader.calc_difficulty(nBits)

    def __repr__(self):
        return "%s(%i, lx(%s), lx(%s), lx(%s), %s, 0x%08x, lx(%s))" % \
                (self.__class__.__name__, self.nVersion, b2lx(self.hashPrevBlock),
                        b2lx(self.hashMerkleRoot), b2lx(self.hashReserved),
                        self.nTime, self.nBits, b2lx(self.nNonce))

class CZBlockHeader(CEquihashHeader):
    """A Zcash Block header"""
    __slots__ = ['solution']

    def __init__(self, nVersion=4, hashPrevBlock=ZERO32,
            hashMerkleRoot=ZERO32, nTime=0, nBits=0, nNonce=ZERO32,
            solution=b'\x00'*SOL_SIZE):
        super(CZBlockHeader, self).__init__(nVersion, hashPrevBlock, hashMerkleRoot, nTime, nBits, nNonce)
        object.__setattr__(self, 'solution', solution)

    def __init__(self, equihashHeader=CEquihashHeader(), solution=b'\x00'*SOL_SIZE):
        self = equihashHeader
        object.__setattr__(self, 'solution', solution)

    @classmethod
    def stream_deserialize(cls, f):
        self = super(CZBlockHeader, cls).stream_deserialize(f)
        object.__setattr__(self, 'solution', BytesSerializer.stream_deserialize(f))
        return self

    def stream_serialize(self, f):
        super(CZBlockHeader, self).stream_serialize(f)
        BytesSerializer.stream_serialize(self.solution, f)

    def __repr__(self):
        return "%s(%i, lx(%s), lx(%s), %s, 0x%08x, lx(%s), lx(%s))" % \
                (self.__class__.__name__, self.nVersion, b2lx(self.hashPrevBlock),
                        b2lx(self.hashMerkleRoot), self.nTime, self.nBits,
                        b2lx(self.nNonce), b2lx(self.solution))
