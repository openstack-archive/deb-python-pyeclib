from pyeclib.ec_iface import ECDriver
import sys

input = b'test'

ec = ECDriver(k=3, m=3, hd=3, ec_type=sys.argv[1])
fragments = ec.encode(input)
assert ec.decode(fragments[0:ec.k]) == input
