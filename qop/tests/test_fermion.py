import numpy as np
from ..base import *
from ..utils import *


def test_fermion_identities():
    assert (c0.D * c0) ** 3 == c0.D * c0
    assert (2.0 * c1 + c0.D * c0) ** 2 == 4.0 * c1 * c0.D * c0 + c0.D * c0


def test_fermion_states():
    assert Sf("011").D | f(1).D * f(1) | Sf("011") == 0
    for s in [c0.D * c0, c0 * c0.D, c0 * c0.D * c1 * c1.D]:
        assert np.allclose(s.E, Sf().D | s | State(zeta=1))
    assert Sf("1").D | c1.D * c1 | c1.D | Sf() == 1.0
    for s in ["", "0", "1", "01", "135"]:
        assert Sf(s).D | Sf(s) == 1


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


def test_hamiltonian():
    n = 12
    h = sum([f(i).D * f((i + 1) % n) + f((i + 1) % n).D * f(i) for i in range(n)])
    assert Sf("0;11;").D | h | Sf("1;11") == 1
