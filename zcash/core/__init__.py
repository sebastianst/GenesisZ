import bitcoin.core as bcore
from bitcoin.core import *
from bitcoin.core.serialize import *
import struct

ZERO32 = b'\x00'*32

class ZCoreMainParams(CoreMainParams):
    N, K = 200, 9
    SOL_SIZE = 1344 # (n/(k+1)+1) *2^k /8
    GENESIS_BLOCK = None # TODO Still need to code CZBlock
    PROOF_OF_WORK_LIMIT = 0x0007ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class ZCoreTestNetParams(ZCoreMainParams, CoreTestNetParams):
    PROOF_OF_WORK_LIMIT = 0x07ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class ZCoreRegTestParams(ZCoreTestNetParams, CoreRegTestParams):
    N, K = 48, 5
    SOL_SIZE = 36
    PROOF_OF_WORK_LIMIT = 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f

"""Master global setting for what core chain params we're using"""
# Inject zcash core parameters into bitcoin lib
bcore.coreparams = ZCoreMainParams()
coreparams = ZCoreMainParams() # internal pointer for shorter access...

def SelectCoreParams(name):
    """Select the core chain parameters to use

    Don't use this directly, use zcash.SelectParams() instead so both
    consensus-critical and general parameters are set properly.
    """
    if name == 'mainnet':
        bcore.coreparams = ZCoreMainParams()
        coreparams = ZCoreMainParams()
    elif name == 'testnet':
        bcore.coreparams = ZCoreTestNetParams()
        coreparams = ZCoreTestNetParams()
    elif name == 'regtest':
        bcore.coreparams = ZCoreRegTestParams()
        coreparams = ZCoreRegTestParams()
    else:
        raise ValueError('Unknown chain %r' % name)


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

    def checkSolutionSize(self):
        # Currently (v. 4), the only accepted solution size is 1344
        if self.nVersion == 4:
            assert len(self.solution) == coreparams.SOL_SIZE

    def __init__(self, nVersion=4, hashPrevBlock=ZERO32,
            hashMerkleRoot=ZERO32, hashReserved=ZERO32, nTime=0, nBits=0,
            nNonce=ZERO32, solution=b'\x00'*coreparams.SOL_SIZE):
        super().__init__(nVersion, hashPrevBlock, hashMerkleRoot, hashReserved,
                nTime, nBits, nNonce)
        object.__setattr__(self, 'solution', solution)
        self.checkSolutionSize()

    @classmethod
    def from_EquihashHeader(cls, equihashHeader=CEquihashHeader(),
            solution=b'\x00'*coreparams.SOL_SIZE, nonce=None):
        """Returns a CZBlockHeader object extending the passed equihash header
        by nonce and solution. If nonce is ommited, it will be taken from the
        equihash header."""
        if not nonce:
            nonce = equihashHeader.nNonce
        return cls(equihashHeader.nVersion, equihashHeader.hashPrevBlock,
                equihashHeader.hashMerkleRoot, equihashHeader.hashReserved,
                equihashHeader.nTime, equihashHeader.nBits, nonce, solution)

    @classmethod
    def stream_deserialize(cls, f):
        h = super(CZBlockHeader, cls).stream_deserialize(f)
        object.__setattr__(h, 'solution', BytesSerializer.stream_deserialize(f))
        h.checkSolutionSize()
        return h

    def stream_serialize(self, f):
        super().stream_serialize(f)
        BytesSerializer.stream_serialize(self.solution, f)

    def __repr__(self):
        return "%s, lx(%s))" % (super().__repr__()[:-1], b2lx(self.solution))

def IsValidSolution(block_header, nonce=None, solution=None):
    """Check if the given solution leads to a valid block header.
    solution or nonce can be ommitted, in which case the solution or nonce
    contained in the given block header will be used. Othweise, an equihash
    header (without solution) may be passed as block_header"""
    if nonce:
        block_header.nNonce = nonce
    if not solution:
        try:
            solution = block_header.solution
        except AttributeError:
            raise Exception("No solution passed nor contained in block_header.")

    h = CZBlockHeader.from_EquihashHeader(block_header, solution, nonce)
    # Note: CheckProofOfWork also checks against Bitcoin main net Proof-of-work limit
    try:
        CheckProofOfWork(h.GetHash(), h.nBits)
        return True
    except CheckProofOfWorkError:
        return False
