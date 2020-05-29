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
    def standardize(self, opl):
        nk, coeff = super().standardize(opl)
        if len(nk) < 2:
            return nk, coeff
        for i, op in enumerate(list(nk)[:-1]):
            if op == list(nk)[i + 1]:
                return None, 0
        return nk, coeff

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
