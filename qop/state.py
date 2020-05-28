import numpy as np
from .base import assert_num, Operator, OperatorString
from .boson import BosonOperator, BosonOperatorString
from .fermion import FermionOperator, FermionOperatorString
from .spin import SpinOperator, SpinOperatorString
from .hardcoreboson import HardcoreBosonOperator, HardcoreBosonOperatorString


class State:
    def __init__(self, ops=None, dagger=False):
        """
        state is ops|0> if dagger is False or <0|ops if dagger is true
        It is worth noting the state from ops is not normalized by default,
        instead State.from_str normalize the state by default

        :param ops:
        :param dagger:
        """
        newdict = {}

        if ops is None:
            ops = self.get_OS()([[self.get_OP()()]])
        for k, v in ops.normal_order().opdict.items():
            if not dagger and (list(k)[-1].d or list(k)[-1].label[0] == -1):
                newdict[k] = v
            if dagger and (not list(k)[0].d or list(k)[-1].label[0] == -1):
                newdict[k] = v
        if not newdict:
            newdict = {tuple([self.get_OP()()]): 0.0}
        self.opdict = newdict
        self.d = dagger

    @classmethod
    def get_OP(cls):
        raise NotImplementedError()

    @classmethod
    def get_OS(cls):
        raise NotImplementedError()

    @classmethod
    def from_opdict(cls, opdict, dagger=False):
        return cls(cls.get_OS().from_opdict(opdict), dagger=dagger)

    @classmethod
    def from_str(cls, s="", normalized=True):
        if not s:
            return cls(cls.get_OS()([[cls.get_OP()()]]))

        ops = cls.get_OP()()
        if len(s.split(";")) > 1:
            s = [t for t in s.split(";") if t.strip()]
        for i in s:
            if len(i.split(",")) > 1:
                label = i.split(",")
                label = [int(j) for j in label]
            else:
                label = [int(i)]
            ops *= cls.get_OP()(*label).D
        st = cls(ops, dagger=False)
        if normalized:
            st = st.normalize()
        return st

    def normalize(self):
        n = self.norm()
        if n > 0:
            self.opdict = {k: v / n for k, v in self.opdict.items()}
        else:  # the state is zero itself
            self.opdict = {tuple([self.get_OP()()]): 0}
        return self

    def norm(self):
        if not self.d:
            innerp = (
                self.get_OS().from_opdict(self.opdict).D
                * self.get_OS().from_opdict(self.opdict)
            ).E
        else:
            innerp = (
                self.get_OS().from_opdict(self.opdict)
                * self.get_OS().from_opdict(self.opdict).D
            ).E
        n = np.sqrt(innerp)
        return n

    def to_ops(self):
        return self.get_OS().from_opdict(self.opdict)

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
            other = self.get_OS().from_op(other)
        assert isinstance(other, OperatorString) or isinstance(other, State)
        if isinstance(other, OperatorString):
            return type(self)(other * self.to_ops())
        else:  # other is left vector
            return (other.to_ops() * self.to_ops()).E

    def __or__(self, other):
        assert self.d is True
        if isinstance(other, Operator):
            other = self.get_OS().from_op(other)
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


class FermionState(State):
    @classmethod
    def get_OP(cls):
        return FermionOperator

    @classmethod
    def get_OS(cls):
        return FermionOperatorString


def Sf(s="", normalized=True):
    return FermionState.from_str(s, normalized)


class BosonState(State):
    @classmethod
    def get_OP(cls):
        return BosonOperator

    @classmethod
    def get_OS(cls):
        return BosonOperatorString


def Sb(s="", normalized=True):
    return BosonState.from_str(s, normalized)


class HardcoreBosonState(State):
    @classmethod
    def get_OP(cls):
        return HardcoreBosonOperator

    @classmethod
    def get_OS(cls):
        return HardcoreBosonOperatorString


def Shb(s="", normalized=True):
    return HardcoreBosonState.from_str(s, normalized)


class SpinState(HardcoreBosonState):
    def __ror__(self, other):
        assert self.d is False
        if isinstance(other, Operator):
            other = SpinOperatorString.from_op(other)
        assert isinstance(other, OperatorString) or isinstance(other, State)
        if isinstance(other, SpinOperatorString):
            return type(self)(other.to_hb() * self.to_ops())
        elif isinstance(other, HardcoreBosonOperatorString):
            return type(self)(other * self.to_ops())
        else:  # other is left vector
            return (other.to_ops() * self.to_ops()).E

    def __or__(self, other):
        assert self.d is True
        if isinstance(other, Operator):
            other = SpinOperatorString.from_op(other)
        assert isinstance(other, OperatorString) or isinstance(other, State)
        if isinstance(other, SpinOperatorString):
            return type(self)(self.to_ops() * other.to_hb(), dagger=True)
        elif isinstance(other, HardcoreBosonOperatorString):
            return type(self)(self.to_ops() * other, dagger=True)
        else:
            return (self.to_ops() * other.to_ops()).E


def Ss(s="", normalized=True):
    return SpinState.from_str(s, normalized)
