from functools import total_ordering
import numpy as np


def assert_num(c):
    if isinstance(c, int):
        return float(c)
    if isinstance(c, float) or isinstance(c, complex):
        return c
    raise ValueError("Only float/complex number is supported in this operation.")


@total_ordering
class Operator:
    _exists = {}

    def __new__(cls, *args, dagger=False, name="OP", zeta=-1, repr=None):
        key = (tuple(args), dagger, name, zeta)
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
        op.type = zeta
        op.repr = repr
        cls._exists[key] = op
        return op

    @property
    def D(self):
        dagger = False if self.d else True

        return Operator(
            *self.label, dagger=dagger, name=self.name, zeta=self.type, repr=self.repr
        )

    def __repr__(self):
        if self.repr is not None:
            return self.repr(self)
        if self.label == (-1,):
            return "I"
        return self.name + str(self.label) + (".D " if self.d else " ")

    __str__ = __repr__

    def simplify(self):
        return self

    def __add__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        elif (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            rops = OperatorString.from_op(Operator(zeta=self.type), [other])
        else:
            rops = other
        return lops + rops

    def __sub__(self, other):
        lops = OperatorString.from_op(self)
        if isinstance(other, Operator):
            rops = OperatorString.from_op(other)
        elif (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            rops = OperatorString.from_op(Operator(zeta=self.type), [other])
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

    def __truediv__(self, other):
        ops = OperatorString.from_op(self)
        return ops / other

    def __radd__(self, other):
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


def fop(*args, **kws):
    return Operator(*args, **kws, zeta=1)


OP = Operator
op = OP
bop = OP
BOP = OP
b = OP
FOP = fop
f = fop


class OperatorString:
    def __init__(self, ops=None, coeff=None, zeta=1):
        self.opdict = {}
        self.type = zeta
        if ops is None:
            if not coeff:
                coeff = 0
            self.opdict[tuple([Operator(zeta=self.type)])] = coeff
        else:
            if not coeff:
                coeff = [1.0] * len(ops)
            for i, oplist in enumerate(ops):
                self.opdict[tuple(oplist)] = (
                    self.opdict.get(tuple(oplist), 0) + coeff[i]
                )

    @classmethod
    def from_op(cls, op, coeff=None):
        return cls([[op]], coeff=coeff)

    @classmethod
    def from_opdict(cls, opdict):
        _instance = cls([[]])
        _instance.opdict = opdict
        return _instance

    @classmethod
    def from_matrix(cls, matrix, cv, rv=None):
        if rv is None:
            rv = [op.D for op in cv]
        assert len(cv) == len(rv) == matrix.shape[0] == matrix.shape[1]
        s = 0.0
        for i in range(len(cv)):
            for j in range(len(cv)):
                s += rv[i] * matrix[i, j] * cv[j]
        return s

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
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            other = type(self)([[Operator(zeta=self.type)]], coeff=[other])
        if not isinstance(other, OperatorString):
            return NotImplemented  # raise NotImplementedError doesn't work!
        newdict = self.opdict
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) + v
        newops = [k for k in newdict]
        newcoeff = [v for k, v in newdict.items()]
        return OperatorString(newops, newcoeff)

    def __sub__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            other = type(self)([[Operator(zeta=self.type)]], coeff=[other])
        if not isinstance(other, OperatorString):
            return NotImplemented  # raise NotImplementedError doesn't work!
        newdict = self.opdict
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) - v
        newops = [k for k in newdict]
        newcoeff = [v for k, v in newdict.items()]
        return OperatorString(newops, newcoeff)

    def __mul__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            other = type(self)([[Operator(zeta=self.type)]], coeff=[other])
        if not isinstance(other, OperatorString):
            return NotImplemented  # raise NotImplementedError doesn't work!
        newdict = {}
        for k1, v1 in self.opdict.items():
            for k2, v2 in other.opdict.items():
                newdict[tuple(list(k1) + list(k2))] = v1 * v2
        return type(self).from_opdict(newdict)

    def __rmul__(self, other):  # multiply by a number
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            other = type(self)([[Operator(zeta=self.type)]], coeff=[other])
        return other.__mul__(self)

    def __truediv__(self, other):
        other = assert_num(other)
        return 1 / other * self

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
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, complex)
        ):
            other = type(self)([[Operator(zeta=self.type)]], coeff=[other])
        return self.__add__(other)

    def __eq__(self, other):
        opdict1 = self.normal_order().opdict
        opdict2 = other.normal_order().opdict
        if len(opdict1) != len(opdict2):
            return False
        for k, v in opdict1.items():
            if not np.allclose(opdict2.get(k, 0.0), v):
                return False
        return True

    @property
    def E(self):
        for k, v in self.normal_order().opdict.items():
            if k == (Operator(zeta=self.type),):
                return v
        return 0.0

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
            if not zeroflag and v != 0:
                nk, coeff = self.standardize(nk)
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        if len(newdict) == 0:
            newdict[tuple([Operator(zeta=self.type)])] = 0.0
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
                    left = OperatorString([[Operator(zeta=self.type)]])
                else:
                    left = OperatorString([oplist[: i - 1]])
                if len(oplist) > i + 1:
                    right = OperatorString([oplist[i + 1 :]])
                else:
                    right = OperatorString([[Operator(zeta=self.type)]])
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

    @property
    def D(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk = tuple([op.D for op in reversed(k)])
            newdict[nk] = newdict.get(nk, 0.0) + np.conj(v)
        self.opdict = newdict
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
                return cls([[OP(zeta=zeta)], [opb, opa]], [zeta * coeff, -zeta * coeff])
            return cls([[opb, opa]], [-zeta * coeff])
        if not opa.d and opb.d:  # ab^\dagger
            if opa.label == opb.label:
                return cls([[OP(zeta=zeta)], [opb, opa]], [coeff, -zeta * coeff])
            return cls([[opb, opa]], [-zeta * coeff])


class State:
    def __init__(self, ops=None, dagger=False, zeta=-1):
        """
        state is ops|0> if dagger is False or <0|ops if dagger is true
        It is worth noting the state from ops is not normalized by default,
        instead State.from_str normalize the state by default

        :param ops:
        :param dagger:
        """
        newdict = {}
        if ops is None:
            ops = OperatorString(coeff=1.0, zeta=zeta)
        for k, v in ops.normal_order().opdict.items():
            if not dagger and (list(k)[-1].d or list(k)[-1].label == (-1,)):
                newdict[k] = v
            if dagger and (not list(k)[0].d or list(k)[0].label == (-1,)):
                newdict[k] = v
        self.type = ops.type
        self.opdict = newdict
        self.d = dagger

    @classmethod
    def from_opdict(cls, opdict, dagger=False):
        return cls(OperatorString.from_opdict(opdict), dagger=dagger)

    @classmethod
    def from_str(cls, s="", normalized=True, zeta=-1):
        if not s:
            return State()

        ops = OP(zeta=zeta)
        if len(s.split(";")) > 1:
            s = [t for t in s.split(";") if t.strip()]
        for i in s:
            if len(i.split(",")) > 1:
                label = i.split(",")
                label = [int(j) for j in label]
            else:
                label = [int(i)]
            ops *= OP(*label, zeta=zeta).D
        st = cls(ops, dagger=False, zeta=zeta)
        if normalized:
            st = st.normalize()
        return st

    def normalize(self):
        n = self.norm()
        if n > 0:
            self.opdict = {k: v / n for k, v in self.opdict.items()}
        else:  # the state is zero itself
            self.opdict = {tuple([OP(zeta=self.type)]): 0}
        return self

    def norm(self):
        if not self.d:
            innerp = (
                OperatorString.from_opdict(self.opdict).D
                * OperatorString.from_opdict(self.opdict)
            ).E
        else:
            innerp = (
                OperatorString.from_opdict(self.opdict)
                * OperatorString.from_opdict(self.opdict).D
            ).E
        n = np.sqrt(innerp)
        return n

    def to_ops(self):
        return OperatorString.from_opdict(self.opdict)

    @property
    def D(self):
        dagger = True if not self.d else False
        newdict = {}
        for k, v in self.opdict.items():
            nk = tuple([op.D for op in reversed(k)])
            newdict[nk] = newdict.get(nk, 0.0) + np.conj(v)
        return type(self).from_opdict(newdict, dagger=dagger)

    def __add__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        assert self.d == other.d
        return type(self)(self.to_ops() + other.to_ops(), self.d)

    def __sub__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        assert self.d == other.d
        return type(self)(self.to_ops() - other.to_ops(), self.d)

    def __mul__(self, other):  # times a number
        other = assert_num(other)
        return type(self)(other * self.to_ops(), self.d)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = assert_num(other)
        return 1 / other * self

    def __ror__(self, other):
        assert self.d is False
        if isinstance(other, Operator):
            other = OperatorString.from_op(other)
        assert isinstance(other, OperatorString) or isinstance(other, State)
        if isinstance(other, OperatorString):
            return type(self)(other * self.to_ops())
        else:  # other is left vector
            return (other.to_ops() * self.to_ops()).E

    def __or__(self, other):
        assert self.d is True
        if isinstance(other, Operator):
            other = OperatorString.from_op(other)
        assert isinstance(other, OperatorString) or isinstance(other, State)
        if isinstance(other, OperatorString):
            return type(self)(self.to_ops() * other, dagger=True)
        else:
            return (self.to_ops() * other.to_ops()).E

    def __repr__(self):
        if not self.d:
            return "( " + self.to_ops().__repr__() + " ) |0>"
        else:
            return "<0| ( " + self.to_ops().__repr__() + " )"


OPS = OperatorString


def fState(s="", normalized=True):
    return State.from_str(s, normalized=normalized, zeta=1)


Sf = fState


def bState(s="", normalized=True):
    return State.from_str(s, normalized=normalized, zeta=-1)


Sb = bState


def commutator(ops1, ops2, zeta=-1):
    zeta = float(zeta)
    return ops1 * ops2 + zeta * ops2 * ops1


def exp(ops, cutoff=2):
    s = 1.0
    last = 1.0
    for i in range(1, cutoff + 1):
        last = ops / float(i) * last
        s += last
    return s
