from bitcoin.core import *
import struct

SOL_SIZE = 1344
ZERO32 = b'\x00'*32

class CEquihashHeader(Serializable): # TODO or make it ImmutableSerializable?
    """A Zcash Equihash solver block header - without solution"""
    __slots__ = ['nVersion', 'hashPrevBlock', 'hashMerkleRoot', 'hashReserved', 'nTime', 'nBits', 'nNonce']

    def __init__(self, nVersion=4, hashPrevBlock=ZERO32,
            hashMerkleRoot=ZERO32, hashReserved=ZERO32, nTime=0, nBits=0, nNonce=ZERO32):
        object.__setattr__(self, 'nVersion', nVersion)
        assert len(hashPrevBlock) == 32
        object.__setattr__(self, 'hashPrevBlock', hashPrevBlock)
        assert len(hashMerkleRoot) == 32
        object.__setattr__(self, 'hashMerkleRoot', hashMerkleRoot)
        assert len(hashReserved) == 32
        object.__setattr__(self, 'hashReserved', hashReserved)
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
            hashMerkleRoot=ZERO32, hashReserved=ZERO32, nTime=0, nBits=0, nNonce=ZERO32,
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
        return "%s, lx(%s))" % (super().__repr__()[:-1], b2lx(self.solution))
