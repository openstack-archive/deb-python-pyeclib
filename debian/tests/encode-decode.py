from __future__ import print_function
from pyeclib.ec_iface import ECDriver
import sys

input = b'test'

# Init
print("init:", end=" ")
ec = ECDriver(k=3, m=3, hd=3, ec_type=sys.argv[1])
print("OK")

# Encode
print("encode:", end=" ")
fragments = ec.encode(input)
print("OK")

# Decode
print("decode:", end=" ")
assert ec.decode(fragments[0:ec.k]) == input
print("OK")
