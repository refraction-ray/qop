import sys
import numpy as np
from . import base

thismodule = sys.modules[__name__]


i_matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
x_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
y_matrix = np.array([[0.0, -1j], [1j, 0.0]])
z_matrix = np.array([[1.0, 0.0], [0.0, -1.0]])


def repr_short(self):
    return self.name + str(self.label[0]) + (".D" if self.d else "")


def generate_basis(n, s=2):
    last = [0] * n
    yield last
    while last != [s - 1] * n:
        i = 0
        last = last.copy()
        while last[-i - 1] == s - 1:
            last[-i - 1] = 0
            i += 1
        last[-i - 1] += 1
        yield last


def commutator(ops1, ops2, zeta=-1):
    zeta = float(zeta)
    return ops1 * ops2 + zeta * ops2 * ops1


def exp(ops, cutoff=2):
    s = 1.0
    last = 1.0
    for i in range(1, cutoff + 1):
        last = ops / float(i) * last
        s += last
    return s
