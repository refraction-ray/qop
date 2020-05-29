from functools import total_ordering
import numpy as np


def assert_num(c):
    if isinstance(c, int):
        return float(c)
    if isinstance(c, float) or isinstance(c, complex):
        return c
    raise ValueError("Only float/complex number is supported in this operation.")


def is_num(c):
    if isinstance(c, int) or isinstance(c, float) or isinstance(c, complex):
        return True
    return False


@total_ordering
class Operator:
    _exists = {}

    def __new__(cls, *args, name="OP", repr_=None):
        key = (tuple(args), name)
        if key in cls._exists:
            return cls._exists[key]
        op = super().__new__(cls)
        if len(args) == 0:
            op.label = (-1,)
        else:
            op.label = tuple(args)
        op.key = key
        op.name = name
        op.repr = repr_
        cls._exists[key] = op
        return op

    def __repr__(self):
        if self.repr is not None:
            return self.repr(self)
        if self.label[0] == -1:
            return "I"
        return self.name + str(self.label)

    __str__ = __repr__

    def simplify(self):
        return self

    def strfy(self):
        return OperatorString.from_op

    def __add__(self, other):
        lops = self.strfy()
        return lops + other

    def __sub__(self, other):
        lops = self.strfy()
        return lops - other

    def __mul__(self, other):
        lops = self.strfy()
        return lops * other

    def __rmul__(self, other):
        lops = self.strfy()
        return other * lops

    def __truediv__(self, other):
        ops = self.strfy()
        return ops / other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return -1 * self.__sub__(other)

    def __pow__(self, n):
        ops = self.strfy()
        return ops ** n

    def __neg__(self):
        ops = self.strfy()
        return -1.0 * ops

    def __eq__(self, other):  # break hashable
        if isinstance(other, Operator):
            return self.key == other.key
        else:  # other is ops
            return other.__eq__(self)

    def __lt__(self, other):
        return self.label < other.label

    def __hash__(self):
        return hash(self.key)


class OperatorString:
    def __init__(self, ops=None, coeff=None):
        self.opdict = {}
        if not ops:
            pass
            # empty instance, need hand crafted
        else:
            if not coeff:
                coeff = [1.0] * len(ops)
            for i, oplist in enumerate(ops):
                self.opdict[tuple(oplist)] = (
                    self.opdict.get(tuple(oplist), 0) + coeff[i]
                )
            self.OP = type(ops[0][0])

    @classmethod
    def from_op(cls, op, coeff=None):
        return cls([[op]], coeff=coeff)

    @classmethod
    def from_opdict(cls, opdict):
        _instance = cls()
        _instance.opdict = opdict
        for k, v in opdict.items():
            _instance.OP = type(k[0])
            break
        return _instance

    @classmethod
    def from_matrix(cls, matrix, cv, rv):
        assert len(cv) == len(rv) == matrix.shape[0] == matrix.shape[1]
        s = 0.0
        for i in range(len(cv)):
            for j in range(len(cv)):
                s += rv[i] * matrix[i, j] * cv[j]
        return s

    def __repr__(self):
        s = ""
        for i, oplist in enumerate(self.opdict):
            s += str(self.opdict[oplist]) + "*"
            for op in oplist:
                s += op.__repr__() + "*"
            s = s[:-1] + " + "
        return s[:-3]

    __str__ = __repr__

    def __add__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):
            other = type(self).from_op(other)
        newdict = self.opdict.copy()
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) + v

        return type(self).from_opdict(newdict)

    def __sub__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):
            other = type(self).from_op(other)
        newdict = self.opdict.copy()
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) - v

        return type(self).from_opdict(newdict)

    def __rsub__(self, other):
        return -1.0 * self + other

    def __mul__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):
            other = type(self).from_op(other)
        newdict = {}
        for k1, v1 in self.opdict.items():
            for k2, v2 in other.opdict.items():
                newdict[tuple(list(k1) + list(k2))] = v1 * v2
        return type(self).from_opdict(newdict)

    def __rmul__(self, other):  # multiply by a number
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        return other.__mul__(self)

    def __truediv__(self, other):
        try:
            other = assert_num(other)
            return 1 / other * self
        except ValueError:
            return other.__rtruediv__(self)

    def __pow__(self, n):
        assert isinstance(n, int)
        assert n >= 0
        if n == 0:
            return type(self)([[self.OP()]])
        nops = self
        if n == 1:
            return nops
        return nops * nops ** (n - 1)

    def __radd__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        return self.__add__(other)

    def __neg__(self):
        return -1.0 * self

    def __eq__(self, other):
        self.simplify()
        opdict1 = self.opdict
        if is_num(other):
            other = other * self.OP()
        if isinstance(other, Operator):
            other = self.from_op(other)
        other.simplify()
        opdict2 = other.opdict
        if len(opdict1) != len(opdict2):
            return False
        for k, v in opdict1.items():
            if not np.allclose(opdict2.get(k, 0.0), v):
                return False
        return True

    def simplify(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk, coeff = self.standardize(k)
            if coeff != 0:
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        newdict = {k: v for k, v in newdict.items() if v != 0}
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        self.opdict = newdict
        return self

    def standardize(self, opl):
        if len(opl) == 0:
            return [self.OP()], 1
        if len(opl) == 1:
            return opl, 1
        nk = []
        for op in list(opl):
            if op.label[0] == -1:
                continue
            nk.append(op)
        if len(nk) == 0:
            nk = [type(opl[0])()]
        return nk, 1
