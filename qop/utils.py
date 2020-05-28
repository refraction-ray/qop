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


for i in range(10):
    setattr(thismodule, "c" + str(i), base.f(i, name="c", repr=repr_short))
for i in range(10):
    setattr(thismodule, "b" + str(i), base.b(i, name="b", repr=repr_short))
