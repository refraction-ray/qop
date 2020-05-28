import sys
import numpy as np
from .particle import ParticleOperator, ParticleOperatorString
from .utils import repr_short

thismodule = sys.modules[__name__]


class HardcoreBosonOperator(ParticleOperator):
    def __new__(cls, *args, dagger=False, name="hb", repr_=None):
        return super().__new__(cls, *args, dagger=dagger, name=name, repr_=repr_)

    def strfy(self):
        return HardcoreBosonOperatorString.from_op(self)


hb = HardcoreBosonOperator


class HardcoreBosonOperatorString(ParticleOperatorString):
    def simplify(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk = []
            zeroflag = False
            for op in k:
                if op.label[0] == -1:
                    continue
                if len(nk) > 0:
                    if op == nk[-1]:
                        zeroflag = True
                        break
                nk.append(op)
            if len(nk) == 0:
                nk = [self.OP()]
            if not zeroflag and v != 0:
                nk, coeff = self.standardize(nk)
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        self.opdict = newdict
        return self

    def exchange(self, opa, opb, coeff=1, zeta=1):
        return super().exchange(opa, opb, coeff=coeff, zeta=zeta)


for i in range(10):
    setattr(thismodule, "hb" + str(i), hb(i, name="hb", repr_=repr_short))

HBOS = HardcoreBosonOperatorString
