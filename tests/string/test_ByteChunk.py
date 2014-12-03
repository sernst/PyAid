from pyaid.string.ByteChunk import ByteChunk
from array import array

import random

a = array('d')
for i in range(100):
    a.append(10000.0*(random.random() - 0.5))

bc = ByteChunk()
bc.writeArrayChunk(a)
bc.position = 0
out = bc.readArrayChunk()
print('[TEST] Array Chunk I/O: %s' % ('PASSED' if a == out else 'FAILED'))
