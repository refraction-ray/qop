import sys
from . import base
from .utils import repr_short

thismodule = sys.modules[__name__]


class Operator(base.Operator):
    def __new__(self, *args, dagger=False, name="OP", repr=None):
        inst = super().__new__(self, *args, dagger=dagger, name=name, repr=repr)
        inst.type = 1
        return inst


class OperatorString(base.OperatorString):
    pass


OP = Operator
OPS = OperatorString

for i in range(10):
    setattr(thismodule, "c" + str(i), OP(i, name="c", repr=repr_short))
