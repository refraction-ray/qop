from ..symbol import *
from ..base import *


def test_evaluate_symbol():
    a = Symbol("a")
    b = Symbol("b")
    assert np.conj(a + 2 * b ** 2).evaluate({"a": 2j, "b": 1.5}) == 4.5 - 2j


def test_within_np():
    a = Symbol("a")
    np.allclose(evaluate_all(a * np.ones([3, 3]), {"a": 2}), 2 * np.ones([3, 3]))
    b = Symbol("b")
    evaluate_all(np.array([[a, b], [b, a]]) @ np.ones([2, 2]), {"a": 3, "b": 1j})[
        0, 0
    ] == 3 + 1j
