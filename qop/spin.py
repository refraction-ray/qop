import sys
import numpy as np
from . import base
from .hardcoreboson import HardcoreBosonOperator, HardcoreBosonOperatorString

thismodule = sys.modules[__name__]


class SpinOperator(base.Operator):
    def __new__(cls, *args, direction="z", name="s", repr_=None):
        key = (tuple(args), direction, name)
        if key in cls._exists:
            return cls._exists[key]
        op = object.__new__(cls)
        if len(args) == 0:
            op.label = (-1, direction)
        else:
            op.label = tuple(list(args) + [direction])
        op.direction = direction
        op.key = key
        op.name = name
        op.repr = repr_
        cls._exists[key] = op
        return op

    def strfy(self):
        return SpinOperatorString.from_op(self)

    def __lt__(self, other):
        if self.label[:-1] != other.label[:-1]:
            return self.label[:-1] < other.label[:-1]
        return self.direction < other.direction

    @property
    def x(self):
        if self.direction == "x":
            return self
        return SpinOperator(
            *self.label[:-1], direction="x", name=self.name, repr_=self.repr
        )

    @property
    def y(self):
        if self.direction == "y":
            return self
        return SpinOperator(
            *self.label[:-1], direction="y", name=self.name, repr_=self.repr
        )

    @property
    def z(self):
        if self.direction == "z":
            return self
        return SpinOperator(
            *self.label[:-1], direction="z", name=self.name, repr_=self.repr
        )

    def to_hb(self):
        name = "hb"
        if self.direction == "x":
            return (
                HardcoreBosonOperator(*self.label[:-1], name=name, repr_=self.repr).D
                + HardcoreBosonOperator(*self.label[:-1], name=name, repr_=self.repr)
            ) / 2.0
        if self.direction == "y":
            return (
                -1.0j
                / 2
                * (
                    HardcoreBosonOperator(
                        *self.label[:-1], name=name, repr_=self.repr
                    ).D
                    - HardcoreBosonOperator(
                        *self.label[:-1], name=name, repr_=self.repr
                    )
                )
            )
        if self.direction == "z":
            return (
                HardcoreBosonOperator(*self.label[:-1], name=name, repr_=self.repr).D
                * HardcoreBosonOperator(*self.label[:-1], name=name, repr_=self.repr)
                - 1 / 2.0
            )


s = SpinOperator

result_table = {
    ("x", "y"): (0.5j, "z"),
    ("y", "x"): (-0.5j, "z"),
    ("y", "z"): (0.5j, "x"),
    ("z", "y"): (-0.5j, "x"),
    ("z", "x"): (0.5j, "y"),
    ("x", "z"): (-0.5j, "y"),
}


class SpinOperatorString(base.OperatorString):
    def to_hb(self):
        hs = [HardcoreBosonOperatorString([[HardcoreBosonOperator()]])] * len(
            self.opdict
        )
        for i, k in enumerate(self.opdict):
            for op in list(k):
                hs[i] *= op.to_hb()
            hs[i] *= self.opdict[k]
        return sum(hs)

    @staticmethod
    def op_from_hb(op):
        if op.d:
            return SpinOperator(
                op.label[:-1], direction="x", name="s"
            ) + 1j * SpinOperator(op.label[:-1], direction="y", name="s")
        return SpinOperator(op.label[:-1], direction="x", name="s") - 1j * SpinOperator(
            op.label[:-1], direction="y", name="s"
        )

    @classmethod
    def from_hb(cls, ops):
        ops = ops.simplify()
        hs = [cls([[SpinOperator()]])] * len(ops.opdict)
        for i, k in enumerate(ops.opdict):
            for op in list(k):
                hs[i] *= cls.op_from_hb(op)
            hs[i] *= ops.opdict[k]
        return sum(hs)

    def standardize(self, opl):
        nopl = []
        for op in opl:
            if op.label[0] != -1:
                nopl.append(op)
        if len(nopl) == 0:
            return [SpinOperator()], 1
        ti = sorted([[t, i] for i, t in enumerate(nopl)], key=lambda s: s[0])
        pm = np.zeros([len(nopl), len(nopl)])
        for j, tt in enumerate(ti):
            pm[j, int(tt[1])] = 1.0
        sign = np.linalg.det(pm)
        nopl = sorted(nopl)
        nnopl = [SpinOperator()]
        for op in nopl:
            if op.label[:-1] == nnopl[-1].label[:-1]:
                nnopl[-1], nsign = self.spin_product(nnopl[-1], op)
                sign *= nsign
            else:
                nnopl.append(op)
        if len(nnopl) > 1:
            nnopl = nnopl[1:]

        return nnopl, sign

    @staticmethod
    def spin_product(sopa, sopb):
        assert sopa.label[:-1] == sopb.label[:-1]
        if sopa.direction == sopb.direction:
            return SpinOperator(), 0.25
        coeff, outd = result_table[(sopa.direction, sopb.direction)]
        outop = SpinOperator(*sopa.label[:-1], direction=outd)
        return outop, coeff


for i in range(10):
    setattr(thismodule, "s" + str(i), s(i, name="s"))

SOS = SpinOperatorString
