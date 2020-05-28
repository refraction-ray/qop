import numpy as np
from . import base


class GrassmannOperator(base.Operator):
    _exists = {}

    def __new__(cls, *args, name="g", repr_=None):
        return super().__new__(cls, *args, name="g", repr_=None)

    def strfy(self):
        return GrassmannOperatorString.from_op(self)


g = GrassmannOperator


class GrassmannOperatorString(base.OperatorString):
    def __eq__(self, other):
        opdict1 = self.simplify().opdict
        opdict2 = other.simplify().opdict
        if len(opdict1) != len(opdict2):
            return False
        for k, v in opdict1.items():
            if not np.allclose(opdict2.get(k, 0.0), v):
                return False
        return True

    def simplify(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk, coeff = self.standardize(list(k))
            zeroflag = False
            nnk = []
            for op in nk:
                if op.label[0] == -1:
                    continue
                if len(nnk) > 0 and nnk[-1] == op:
                    zeroflag = True
                    break
                nnk.append(op)
            if len(nk) == 0:
                nk = [self.OP()]
            if v != 0 and not zeroflag:
                newdict[tuple(nnk)] = newdict.get(tuple(nnk), 0) + coeff * v
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        self.opdict = newdict
        return self

    @classmethod
    def standardize(cls, opl):
        """

        :param opl:
        :return:
        """
        nopl = []
        ti = sorted([[t, i] for i, t in enumerate(opl)], key=lambda s: s[0])
        pm = np.zeros([len(opl), len(opl)])
        for j, tt in enumerate(ti):
            pm[j, int(tt[1])] = 1.0
        sign = np.linalg.det(pm)
        nopl = [tt[0] for tt in ti]
        return nopl, sign
