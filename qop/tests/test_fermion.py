from ..fermion import *


def test_fermion_identities():
    assert (c0.D * c0) ** 3 == c0.D * c0
    assert (2.0 * c1 + c0.D * c0) ** 2 == 4.0 * c1 * c0.D * c0 + c0.D * c0
    assert State.from_str("011").D | OP(1).D * OP(1) | State.from_str("011") == 0
