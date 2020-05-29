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

    def __rtruediv__(self, other):
        ops = self.strfy()
        return other / ops

    def conjugate(self):
        ops = self.strfy()
        return ops.D

    @property
    def D(self):
        return self.conjugate()

    def norm(self):
        ops = self.strfy()
        return ops.norm()


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
    def conjugate(self):
        newdict = {}
        for k, v in self.opdict.items():
            sign = 1
            for op in list(k):
                if op.label[0] > 0:
                    sign *= -1
            newdict[k] = sign * v
        return self.from_opdict(newdict)

    @property
    def D(self):
        return self.conjugate()

    def norm(self):
        self.simplify()
        return np.sqrt(sum([v ** 2 for k, v in self.opdict.items()]))

    def __rtruediv__(self, other):
        # other/q = other * q*/|q|^2
        re = self.D / self.norm() ** 2
        return other * re

    def standardize(self, opl):
        if len(opl) < 2:
            return opl, 1
        s, r = result_table[(opl[0].label[0], opl[1].label[0])]
        r = QuaternionOperator(r)
        nopl = [r]
        nopl.extend(opl[2:])
        r2, s2 = self.standardize(nopl)
        return r2, s * s2
