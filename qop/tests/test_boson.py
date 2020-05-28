import math
from ..base import *
from ..utils import *


def test_boson_identities():
    assert (
        b0.D * b0
    ) ** 3 == b0.D * b0 + 3.0 * b0.D ** 2 * b0 ** 2 + 1.0 * b0.D ** 3 * b0 ** 3
    assert (
        round(
            State(b0.D ** 2).normalize().D | b0.D * b0 | State(b0.D ** 2).normalize(), 1
        )
        == 2.0
    )
    assert (
        round(
            State(b0 ** 2, dagger=True).normalize()
            | b0.D * b0
            | b0.D * b0
            | State(b0.D ** 2).normalize(),
            1,
        )
        == 4.0
    )
    assert (
        round(State.from_str("011").D | OP(1).D * OP(1) | State.from_str("011"), 0)
        == 2.0
    )


def test_boson_states():
    s = State.from_str() + 2.0 * State.from_str("12")
    s = s.normalize()
    assert round(s.D | OP(1).D * OP(1) | s, 1) == 0.8
    assert Sb("0,1;1,2").D | b(1, 2).D * b(1, 2) | Sb("0,1;1,2")


def test_state_norm():
    for i in range(7):
        s = b0.D ** i | Sb()
        assert s.D | s == math.factorial(i)
