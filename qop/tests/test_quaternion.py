from ..quaternion import *


def test_complex():
    assert ((2 + qi) * (2 - qi)) == 5
    assert (1 + qi) / (1 - qi) == qi


def test_quaternion_identities():
    assert 1 + qi ** 2 == 0.0
    assert (1 + 2 * qi + 3 * qj) ** 2 == -12 + 4 * qj * qk + 6 * qj
    assert ((1 + 2 * qi + 3 * qj) ** 2).D == -12 - 4 * qi - 6 * qj
    assert qi * qi * qj * qk * qi + 1 == 2
    assert 1 / (qi + qj) == -1 / 2 * (qi + qj)


def test_conjugation():
    for f in [qi, qj, qk, 1 + qi + 2 * qk]:
        assert f.D == -0.5 * (f + qi * f * qi + qj * f * qj + qk * f * qk)
