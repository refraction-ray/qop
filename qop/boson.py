import sys
from . import base
from .utils import repr_short

thismodule = sys.modules[__name__]


class Operator(base.Operator):
    def __new__(self, *args, dagger=False, name="OP", repr=None):
        inst = super().__new__(self, *args, dagger=dagger, name=name, repr=repr)
        inst.type = -1
        return inst


class OperatorString(base.OperatorString):
    pass


class State(base.State):
    @classmethod
    def from_str(cls, s, nomarlized=True):
        ops = OP()
        if len(s.split(",")) > 1:
            s = s.split(",")
        for i in s:
            ops *= OP(int(i)).D
        st = cls(ops, dagger=False)
        if nomarlized:
            st = st.normalize()
        return st


OP = Operator
OPS = OperatorString

# some precached ops
for i in range(10):
    setattr(thismodule, "b" + str(i), OP(i, name="b", repr=repr_short))
