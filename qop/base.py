from functools import total_ordering
import numpy as np


@total_ordering
class Operator:
    _exists = {}

    def __new__(cls, *args, dagger=False, name="OP", repr=None):
        key = (tuple(args), dagger, name)
        if key in cls._exists:
            return cls._exists[key]
        op = super().__new__(cls)
        if len(args) == 0:
            op.label = (-1,)
        else:
            op.label = tuple(args)
        op.d = dagger
        op.key = key
        op.name = name
        op.type = 0
        op.repr = repr
        cls._exists[key] = op
        return op

    @property
    def D(self):
        dagger = False if self.d else True

        return type(self)(*self.label, dagger=dagger, name=self.name, repr=self.repr)

    def __repr__(self):
        if self.repr is not None:
            return self.repr(self)
        return self.name + str(self.label) + (".D " if self.d else " ")

    __str__ = __repr__

    def simplify(self):
        return self

    def __add__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        else:
            rops = other
        return lops + rops

    def __sub__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        else:
            rops = other
        return lops - rops

    def __mul__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        else:
            rops = other
        return lops * rops

    def __rmul__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        else:
            rops = other
        return rops * lops

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __pow__(self, n):
        ops = OperatorString.from_op(self)
        return ops ** n

    def __eq__(self, other):  # break hashable
        return self.label == other.label and self.d == other.d

    def __lt__(self, other):
        if self.d and not other.d:
            return True
        if not self.d and other.d:
            return False
        return self.label < other.label

    def __hash__(self):
        return hash(self.key)


class OperatorString:
    def __init__(self, ops, coeff=None):
        self.opdict = {}
        if not coeff:
            coeff = [1.0] * len(ops)
        for i, oplist in enumerate(ops):
            self.opdict[tuple(oplist)] = self.opdict.get(tuple(oplist), 0) + coeff[i]

    @classmethod
    def from_op(cls, op):
        return cls([[op]])

    @classmethod
    def from_opdict(cls, opdict):
        _instance = cls([[]])
        _instance.opdict = opdict
        return _instance

    def is_all_normal_ordered(self):
        for oplist in self.opdict:
            d = True
            for op in oplist:
                if op.d and d:
                    continue
                if op.d and not d:
                    return False
                if not op.d and d:
                    d = False
                if not op.d and not d:
                    continue
        return True

    @staticmethod
    def is_normal_ordered(oplist):

        d = True
        for op in oplist:
            if op.d and d:
                continue
            if op.d and not d:
                return False
            if not op.d and d:
                d = False
            if not op.d and not d:
                continue
        return True

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
        if isinstance(other, float):
            other = type(self)([[Operator()]], coeff=[other])
        newdict = self.opdict
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) + v
        newops = [k for k in newdict]
        newcoeff = [v for k, v in newdict.items()]
        return OperatorString(newops, newcoeff)

    def __sub__(self, other):
        if isinstance(other, float):
            other = type(self)([[Operator()]], coeff=[other])
        newdict = self.opdict
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) - v
        newops = [k for k in newdict]
        newcoeff = [v for k, v in newdict.items()]
        return OperatorString(newops, newcoeff)

    def __mul__(self, other):
        if isinstance(other, float):
            other = type(self)([[Operator()]], coeff=[other])
        if not isinstance(other, OperatorString):
            return NotImplemented  # raise NotImplementedError doesn't work!
        newdict = {}
        for k1, v1 in self.opdict.items():
            for k2, v2 in other.opdict.items():
                newdict[tuple(list(k1) + list(k2))] = v1 * v2
        return type(self).from_opdict(newdict)

    def __rmul__(self, other):  # multiply by a number
        if isinstance(other, float):
            other = type(self)([[Operator()]], coeff=[other])
        return other.__mul__(self)

    def __pow__(self, n):
        assert isinstance(n, int)
        assert n >= 0
        if n == 0:
            return OperatorString([[OP()]])
        nops = self
        if n == 1:
            return nops
        return nops * nops ** (n - 1)

    def __radd__(self, other):
        if isinstance(other, float):
            other = type(self)([[Operator()]], coeff=[other])
        return self.__add__(other)

    def __eq__(self, other):
        opdict1 = self.normal_order().opdict
        opdict2 = other.normal_order().opdict
        if len(opdict1) != len(opdict2):
            return False
        for k, v in opdict1.items():
            if opdict2.get(k, 0.0) != v:
                return False
        return True

    def simplify(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk = []
            zeroflag = False
            for op in k:
                if op.label == (-1,):
                    continue
                if len(nk) > 0 and op.type == 1:
                    if op == nk[-1]:
                        zeroflag = True
                        break
                nk.append(op)
            if len(nk) == 0:
                nk = [OP(-1)]
            if not zeroflag:
                nk, coeff = self.standardize(nk)
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        self.opdict = newdict
        return self

    @classmethod
    def standardize(cls, opl):
        """

        :param opl:
        :return:
        """
        zeta = opl[0].type
        l = []
        innerl = []
        st = True
        for op in opl:
            if op.d and st:
                innerl.append(op)
            elif not op.d and not st:
                innerl.append(op)
            elif op.d and not st:
                if innerl:
                    l.append(innerl.copy())
                innerl = [op]
                st = True
            else:
                if innerl:
                    l.append(innerl.copy())
                innerl = [op]
                st = False
        if innerl:
            l.append(innerl.copy())
        if zeta == -1:  # boson
            nopl = []
            for il in l:
                nopl += sorted(il)
            return nopl, 1.0
        else:  # fermion
            sign = 1
            nopl = []
            for il in l:
                ti = sorted([[t, i] for i, t in enumerate(il)], key=lambda s: s[0])
                pm = np.zeros([len(il), len(il)])
                for j, tt in enumerate(ti):
                    pm[j, int(tt[1])] = 1.0
                sign *= np.linalg.det(pm)
                nopl += [t[0] for t in ti]
            return nopl, sign

    def no1(self):
        for oplist, v in self.opdict.items():
            if not self.is_normal_ordered(oplist):
                st = 0
                i = 0
                while True:
                    if not oplist[i].d and st == 0:
                        st = 1
                    elif oplist[i].d and st == 1:
                        break
                    i += 1
                middle = self.exchange(oplist[i - 1], oplist[i], coeff=v).simplify()
                if i - 1 < 1:
                    left = OperatorString([[Operator()]])
                else:
                    left = OperatorString([oplist[: i - 1]])
                if len(oplist) > i + 1:
                    right = OperatorString([oplist[i + 1 :]])
                else:
                    right = OperatorString([[Operator()]])
                newops = (left * middle * right).simplify()
                del self.opdict[oplist]
                for k, v in newops.opdict.items():
                    self.opdict[k] = self.opdict.get(k, 0) + v
                return False
        return True

    def normal_order(self):
        self.simplify()
        while not self.no1():
            self.simplify()
        return self

    @classmethod
    def exchange(cls, opa, opb, coeff=1):
        assert opa.type in [-1, 1]
        assert opb.type in [-1, 1]
        if opa.type != opb.type:
            return cls([[opb, opa]], [coeff])
        zeta = opa.type  # 1 for fermion and -1 for boson
        if (opa.d and opb.d) or (not opa.d and not opb.d):
            if zeta == 1 and opa.label == opb.label:
                return cls([[opb, opa]], [0.0])
            return cls([[opb, opa]], [-zeta * coeff])
        if opa.d and not opb.d:  # a^\dagger b
            if opa.label == opb.label:
                return cls([[Operator()], [opb, opa]], [zeta * coeff, -zeta * coeff])
            return cls([[opb, opa]], [-zeta * coeff])
        if not opa.d and opb.d:  # ab^\dagger
            if opa.label == opb.label:
                return cls([[Operator()], [opb, opa]], [coeff, -zeta * coeff])
            return cls([[opb, opa]], [-zeta * coeff])


OP = Operator
OPS = OperatorString
