import numpy as np

i_matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
x_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
y_matrix = np.array([[0.0, -1j], [1j, 0.0]])
z_matrix = np.array([[1.0, 0.0], [0.0, -1.0]])


def repr_short(self):
    return self.name + str(self.label[0]) + (".D" if self.d else "")
