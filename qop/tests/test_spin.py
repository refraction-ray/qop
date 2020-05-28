from ..spin import *
from ..state import *


def test_spin_xyz():
    assert s0.x * s0.y * s0.z == 0.125j


def test_spin_state():
    assert Ss().D | s0.z | Ss() == -0.5
    assert Ss().D | s0.x | Ss("0") == 0.5
