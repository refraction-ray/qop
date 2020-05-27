from ..boson import *


def test_boson_identities():
    assert (
        b0.D * b0
    ) ** 3 == b0.D * b0 + 3.0 * b0.D ** 2 * b0 ** 2 + 1.0 * b0.D ** 3 * b0 ** 3
