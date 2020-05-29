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
    def standardize(self, opl):
        """

        :param opl:
        :return:
        """
        nk = []
        for op in opl:
            if op.label[0] == -1:
                continue
            nk.append(op)
        if len(nk) == 0:
            return [self.OP()], 1
        if len(nk) == 1:
            return nk, 1
        ti = sorted([[t, i] for i, t in enumerate(nk)], key=lambda s: s[0])
        pm = np.zeros([len(nk), len(nk)])
        for j, tt in enumerate(ti):
            pm[j, int(tt[1])] = 1.0
        sign = np.linalg.det(pm)
        nopl = [tt[0] for tt in ti]
        for i, op in enumerate(list(nopl)[:-1]):
            if op == list(nopl)[i + 1]:
                return None, 0
        return nopl, sign
