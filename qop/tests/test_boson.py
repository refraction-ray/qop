import math
from ..boson import *
from ..state import *


def test_boson_identities():
    assert (
        b0.D * b0
    ) ** 3 == b0.D * b0 + 3.0 * b0.D ** 2 * b0 ** 2 + 1.0 * b0.D ** 3 * b0 ** 3
    assert (
        round(
            BosonState(b0.D ** 2).normalize().D
            | b0.D * b0
            | BosonState(b0.D ** 2).normalize(),
            1,
        )
        == 2.0
    )
    assert (
        round(
            BosonState(b0 ** 2, dagger=True).normalize()
            | b0.D * b0
            | b0.D * b0
            | BosonState(b0.D ** 2).normalize(),
            1,
        )
        == 4.0
    )
    assert round(BosonState.from_str("011").D | b(1).D * b(1) | Sb("011"), 0) == 2.0


def test_boson_states():
    s = BosonState.from_str() + 2.0 * BosonState.from_str("12")
    s = s.normalize()
    assert round(s.D | b(1).D * b(1) | s, 1) == 0.8
    assert Sb("0,1;1,2").D | b(1, 2).D * b(1, 2) | Sb("0,1;1,2")


def test_state_norm():
    for i in range(7):
        s = b0.D ** i | Sb()
        assert s.D | s == math.factorial(i)
