from qop.grassmann import *


def test_grassmann_number():
    assert (1 + g(0) * g(1)) ** 2 == 1 - 2 * g(1) * g(0)
