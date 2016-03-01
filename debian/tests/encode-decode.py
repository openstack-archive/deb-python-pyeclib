from pyeclib.ec_iface import ECDriver
import sys

input = b'test'

ec = ECDriver(k=2, m=1, ec_type=sys.argv[1])
fragments = ec.encode(input)
assert ec.decode(fragments[0:2]) == input
