from ..spin import *
from ..state import *


def test_spin_xyz():
    assert s0.x * s0.y * s0.z == 0.125j


def test_spin_state():
    assert Ss().D | s0.z | Ss() == -0.5
    assert Ss().D | s0.x | Ss("0") == 0.5
    for w in ["", "0", "1", "01"]:
        assert abs(Ss(w).D | (s0.x * s1.x + s0.y * s1.y + s0.z * s1.z) | Ss(w)) == 0.25
