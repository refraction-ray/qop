import numpy as np
from ..fermion import *


def test_fermion_identities():
    assert (c0.D * c0) ** 3 == c0.D * c0
    assert (2.0 * c1 + c0.D * c0) ** 2 == 4.0 * c1 * c0.D * c0 + c0.D * c0


def test_fermion_states():
    assert State.from_str("011").D | OP(1).D * OP(1) | State.from_str("011") == 0
    for f in [c0.D * c0, c0 * c0.D, c0 * c0.D * c1 * c1.D]:
        assert np.allclose(f.E, V.D | f | State())
