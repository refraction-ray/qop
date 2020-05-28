from ..hardcoreboson import *
from ..state import *


def test_hardcoreboson_state():
    assert Shb().D | ((hb0 * hb0.D) ** 3) | Shb() == 1
    assert Shb().D | ((hb0 * hb0.D) ** 3) * hb0.D | Shb() == 0
    assert Shb("00").norm() == 0
    assert Shb("0").norm() == 1
    assert hb0 * hb1.D == hb1.D * hb0
