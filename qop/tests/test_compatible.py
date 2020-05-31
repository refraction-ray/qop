import numpy as np
from opt_einsum import contract
from ..symbol import Symbols
from ..base import simplify

a, b, c = Symbols("abc")


def test_einsum():
    contract("i->", np.array([a, b]), backend="qop")
    simplify(
        contract(
            "ijk,i->jk", c * np.ones([3, 3, 3]), np.array([a, b, c]), backend="qop"
        )
    )
