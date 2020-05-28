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

    def exchange(self, opa, opb, coeff=1):
        # looks like fermion on the same label and looks like boson on the different label
        if (opa.d and opb.d) or (not opa.d and not opb.d):
            if opa.label[:-1] == opb.label[:-1]:
                return type(self)([[opb, opa]], [0.0])
            return type(self)([[opb, opa]], [coeff])
        if opa.d and not opb.d:  # a^\dagger b
            if opa.label[:-1] == opb.label[:-1]:
                return type(self)([[self.OP()], [opb, opa]], [coeff, -coeff])
            return type(self)([[opb, opa]], [coeff])
        if not opa.d and opb.d:  # ab^\dagger
            if opa.label[:-1] == opb.label[:-1]:
                return type(self)([[self.OP()], [opb, opa]], [coeff, -coeff])
            return type(self)([[opb, opa]], [coeff])


for i in range(10):
    setattr(thismodule, "hb" + str(i), hb(i, name="hb", repr_=repr_short))

HBOS = HardcoreBosonOperatorString
