import numpy as np
from ..fermion import *
from ..utils import *


def test_fermion_identities():
    assert (c0.D * c0) ** 3 == c0.D * c0
    assert (2.0 * c1 + c0.D * c0) ** 2 == 4.0 * c1 * c0.D * c0 + c0.D * c0


def test_fermion_states():
    assert State.from_str("011").D | OP(1).D * OP(1) | State.from_str("011") == 0
    for f in [c0.D * c0, c0 * c0.D, c0 * c0.D * c1 * c1.D]:
        assert np.allclose(f.E, V.D | f | State())


def test_hubbard_int_identity():
    assert (
        2
        / 3
        * (
            OPS.from_matrix(x_matrix / 2.0, [c0, c1]) ** 2
            + OPS.from_matrix(y_matrix / 2.0, [c0, c1]) ** 2
            + OPS.from_matrix(z_matrix / 2.0, [c0, c1]) ** 2
        )
        == 1 / 2 * OPS.from_matrix(i_matrix, [c0, c1]) - c0.D * c0 * c1.D * c1
    )

    for w in ["", "0", "1", "01"]:
        s = State.from_str(w)
        s = s.normalize()
        print(s.D | (c1.D * c1 - 1 / 2) * (c0.D * c0 - 1 / 2) | s)
