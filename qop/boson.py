import sys
import numpy as np
from .particle import ParticleOperator, ParticleOperatorString
from .utils import repr_short

thismodule = sys.modules[__name__]


class BosonOperator(ParticleOperator):
    def strfy(self):
        return BosonOperatorString.from_op(self)


b = BosonOperator


class BosonOperatorString(ParticleOperatorString):
    pass


for i in range(10):
    setattr(thismodule, "b" + str(i), b(i, name="b", repr_=repr_short))

BOS = BosonOperatorString
