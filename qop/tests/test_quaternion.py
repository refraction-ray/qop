from ..quaternion import *


def test_quaternion_identities():
    assert 1 + qi ** 2 == 0.0
    assert (1 + 2 * qi + 3 * qj) ** 2 == -12 + 4 * qj * qk + 6 * qj
    assert qi * qi * qj * qk * qi + 1 == 2
