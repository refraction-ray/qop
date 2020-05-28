import numpy as np
from . import base

_name = {-1: "I", 1: "i", 2: "j", 3: "k"}


class QuaternionOperator(base.Operator):
    _exists = {}

    def __new__(cls, *args, name=None, repr_=None):
        assert len(args) <= 1  # args can be 1,2,3 for i, j, k
        if not args:
            args = [-1]
        assert args[0] in [-1, 1, 2, 3]
        return super().__new__(cls, *args, name=_name[args[0]], repr_=None)

    def __repr__(self):
        return self.name

    def strfy(self):
        return QuaternionOperatorString.from_op(self)


qi, qj, qk = [QuaternionOperator(i) for i in [1, 2, 3]]

# ×	1	i	j	k
# 1	1	i	j	k
# i	i	−1	k	−j
# j	j	−k	−1	i
# k	k	j	−i	−1

result_table = {
    (-1, -1): (1, -1),
    (-1, 1): (1, 1),
    (-1, 2): (1, 2),
    (-1, 3): (1, 3),
    (1, -1): (1, 1),
    (1, 1): (-1, -1),
    (1, 2): (1, 3),
    (1, 3): (-1, 2),
    (2, -1): (1, 2),
    (2, 1): (-1, 3),
    (2, 2): (-1, -1),
    (2, 3): (1, 1),
    (3, -1): (1, 3),
    (3, 1): (1, 2),
    (3, 2): (-1, 1),
    (3, 3): (-1, -1),
}


class QuaternionOperatorString(base.OperatorString):
    def __eq__(self, other):
        if base.is_num(other):
            other = other * self.OP()
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
            if v != 0:
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        newdict = {k: v for k, v in newdict.items() if v != 0}
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
        if len(opl) < 2:
            return opl, 1
        s, r = result_table[(opl[0].label[0], opl[1].label[0])]
        r = QuaternionOperator(r)
        nopl = [r]
        nopl.extend(opl[2:])
        r2, s2 = cls.standardize(nopl)
        return r2, s * s2
